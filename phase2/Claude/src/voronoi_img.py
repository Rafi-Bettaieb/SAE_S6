"""
voronoi_img.py
--------------
Export du diagramme de Voronoï en image raster (PNG, JPEG, BMP).

Utilise uniquement Pillow (PIL) pour le rendu — aucune bibliothèque
Voronoï externe. Le rendu est identique en style au SVG (thème sombre).

Fonctionnalités :
    - Rendu haute résolution paramétrable.
    - Antialiasing des arêtes via sur-échantillonnage (rendu 2× puis
      réduction, technique simple et sans dépendance extra).
    - Support PNG (avec transparence possible), JPEG et BMP.
    - Affichage optionnel des labels de coordonnées.
"""

import math
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from voronoi_calc import VoronoiDiagram, Point


# ---------------------------------------------------------------------------
# Palette de couleurs (cohérente avec le SVG / l'interface Tkinter)
# ---------------------------------------------------------------------------

PALETTE = {
    "background":  (17,  17,  27),    # #11111b  fond très sombre
    "grid":        (30,  30,  46),    # #1e1e2e  grille subtile
    "edge":        (137, 180, 250),   # #89b4fa  arêtes Voronoï (bleu clair)
    "site_fill":   (243, 139, 168),   # #f38ba8  point du germe (rose)
    "site_halo":   (243, 139, 168, 80),  # idem, semi-transparent
    "label":       (108, 112, 134),   # #6c7086  texte des coordonnées
    "legend_text": (166, 173, 200),   # #a6adc8  texte légende
}

# Facteur de sur-échantillonnage pour l'antialiasing
_SSAA = 2


# ---------------------------------------------------------------------------
# Fonction principale d'export
# ---------------------------------------------------------------------------

def export_to_image(
    diagram: VoronoiDiagram,
    output_path: str,
    width: int = 1200,
    height: int = 900,
    show_labels: bool = True,
    show_grid: bool = True,
    quality: int = 95,
) -> None:
    """
    Exporte le diagramme de Voronoï dans un fichier image (PNG/JPEG/BMP).

    Le format est déduit automatiquement depuis l'extension du chemin.
    Formats supportés : .png, .jpg / .jpeg, .bmp

    Paramètres :
        diagram     : résultat du calcul du diagramme de Voronoï.
        output_path : chemin du fichier image de destination.
        width       : largeur de l'image en pixels.
        height      : hauteur de l'image en pixels.
        show_labels : afficher ou non les coordonnées des sites.
        show_grid   : afficher ou non la grille de fond.
        quality     : qualité JPEG (1-95), ignoré pour PNG/BMP.

    Raises :
        ValueError : si le format de fichier n'est pas supporté.
        IOError    : si l'écriture échoue.
    """
    ext = Path(output_path).suffix.lower()
    supported = {".png", ".jpg", ".jpeg", ".bmp"}
    if ext not in supported:
        raise ValueError(
            f"Format non supporté : '{ext}'. "
            f"Utilisez l'un des suivants : {', '.join(sorted(supported))}"
        )

    # Rendu en haute résolution (sur-échantillonnage pour l'antialiasing)
    render_w = width  * _SSAA
    render_h = height * _SSAA
    pad      = 40    * _SSAA

    # ── Calcul de la transformation données → pixels ──────────────────────
    x_min = min(p.x for p in diagram.sites)
    x_max = max(p.x for p in diagram.sites)
    y_min = min(p.y for p in diagram.sites)
    y_max = max(p.y for p in diagram.sites)
    data_w = max(x_max - x_min, 1.0)
    data_h = max(y_max - y_min, 1.0)
    scale = min(
        (render_w - 2 * pad) / data_w,
        (render_h - 2 * pad) / data_h
    )
    offset_x = pad + ((render_w - 2 * pad) - data_w * scale) / 2 - x_min * scale
    offset_y = pad + ((render_h - 2 * pad) - data_h * scale) / 2 - y_min * scale

    def to_px(p: Point) -> tuple[int, int]:
        """Transforme un point données → coordonnées pixel (sans inversion Y)."""
        px = int(round(p.x * scale + offset_x))
        py = int(round(p.y * scale + offset_y))
        return px, py

    # ── Création de l'image et du contexte de dessin ──────────────────────
    img  = Image.new("RGB", (render_w, render_h), PALETTE["background"])
    draw = ImageDraw.Draw(img, "RGBA")

    # 1. Grille de fond
    if show_grid:
        _draw_grid(draw, render_w, render_h, step=40 * _SSAA)

    # 2. Arêtes de Voronoï
    edge_w = max(1, int(round(1.5 * _SSAA)))
    for (p1, p2) in diagram.edges:
        px1, py1 = to_px(p1)
        px2, py2 = to_px(p2)
        # Vérifier qu'au moins un bout est dans l'image (avec marge)
        margin = 10 * _SSAA
        if _segment_visible(px1, py1, px2, py2, render_w, render_h, margin):
            draw.line(
                [(px1, py1), (px2, py2)],
                fill=PALETTE["edge"],
                width=edge_w,
            )

    # 3. Sites (germes)
    r_halo = int(round(8  * _SSAA))
    r_dot  = int(round(5  * _SSAA))
    for site in diagram.sites:
        sx, sy = to_px(site)
        # Halo semi-transparent
        draw.ellipse(
            [sx - r_halo, sy - r_halo, sx + r_halo, sy + r_halo],
            outline=PALETTE["site_halo"],
            width=max(1, int(_SSAA)),
        )
        # Point plein
        draw.ellipse(
            [sx - r_dot, sy - r_dot, sx + r_dot, sy + r_dot],
            fill=PALETTE["site_fill"],
        )

    # 4. Labels de coordonnées
    if show_labels:
        font = _load_font(size=int(10 * _SSAA))
        for site in diagram.sites:
            sx, sy = to_px(site)
            label = f"({site.x:.0f}, {site.y:.0f})"
            draw.text(
                (sx + int(10 * _SSAA), sy - int(12 * _SSAA)),
                label,
                fill=PALETTE["label"],
                font=font,
            )

    # 5. Légende en bas à gauche
    _draw_legend(draw, render_w, render_h, len(diagram.sites),
                 len(diagram.edges), _SSAA)

    # ── Réduction (antialiasing) ───────────────────────────────────────────
    final = img.resize((width, height), Image.LANCZOS)

    # ── Enregistrement ────────────────────────────────────────────────────
    save_kwargs: dict = {}
    if ext in (".jpg", ".jpeg"):
        save_kwargs["quality"]   = quality
        save_kwargs["optimize"]  = True
        save_kwargs["subsampling"] = 0
    elif ext == ".png":
        save_kwargs["optimize"]  = True
        save_kwargs["compress_level"] = 6

    final.save(output_path, **save_kwargs)


# ---------------------------------------------------------------------------
# Helpers de rendu
# ---------------------------------------------------------------------------

def _draw_grid(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    step: int,
) -> None:
    """Dessine une grille de fond subtile."""
    color = PALETTE["grid"]
    for x in range(0, width, step):
        draw.line([(x, 0), (x, height)], fill=color, width=1)
    for y in range(0, height, step):
        draw.line([(0, y), (width, y)], fill=color, width=1)


def _draw_legend(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    nb_sites: int,
    nb_edges: int,
    ssaa: int,
) -> None:
    """Ajoute une légende en bas à gauche de l'image."""
    font  = _load_font(size=int(10 * ssaa))
    color = PALETTE["legend_text"]
    lines = [
        f"Sites : {nb_sites}",
        f"Arêtes : {nb_edges}",
        "Algorithme : Bowyer-Watson + Delaunay dual",
    ]
    y_base = height - int(14 * ssaa)
    x_base = int(10 * ssaa)
    for i, line in enumerate(reversed(lines)):
        draw.text(
            (x_base, y_base - i * int(14 * ssaa)),
            line,
            fill=color,
            font=font,
        )


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """
    Charge une police monospace. Utilise la police par défaut de Pillow
    si aucune police système n'est disponible.
    """
    candidates = [
        "DejaVuSansMono.ttf",
        "consola.ttf",       # Windows Consolas
        "Courier New.ttf",
        "LiberationMono-Regular.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except (IOError, OSError):
            continue
    # Repli sur la police bitmap intégrée à Pillow
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        # Pillow < 10 : load_default() ne prend pas de paramètre size
        return ImageFont.load_default()


def _segment_visible(
    x1: int, y1: int,
    x2: int, y2: int,
    w: int, h: int,
    margin: int = 0,
) -> bool:
    """Vérifie grossièrement si un segment est dans la zone image."""
    return not (
        max(x1, x2) < -margin or min(x1, x2) > w + margin or
        max(y1, y2) < -margin or min(y1, y2) > h + margin
    )
