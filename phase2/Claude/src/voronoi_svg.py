"""
voronoi_svg.py
--------------
Export du diagramme de Voronoï au format SVG.

Génère un fichier SVG vectoriel autonome, lisible dans tout navigateur
ou éditeur graphique (Inkscape, Illustrator, etc.).
"""

import math
import xml.etree.ElementTree as ET
from typing import Optional
from xml.dom import minidom

from voronoi_calc import VoronoiDiagram, Point


# ---------------------------------------------------------------------------
# Constantes de style SVG (facilement modifiables)
# ---------------------------------------------------------------------------

STYLE = {
    "background":     "#1e1e2e",   # Fond sombre
    "edge_color":     "#89b4fa",   # Arêtes Voronoï (bleu clair)
    "edge_width":     1.5,         # Épaisseur des arêtes
    "site_color":     "#f38ba8",   # Couleur des sites (germes)
    "site_radius":    4.0,         # Rayon des cercles de site
    "site_label":     "#cdd6f4",   # Couleur des étiquettes
    "font_size":      10,          # Taille de police pour les coordonnées
    "padding":        40,          # Marge autour du contenu
}


# ---------------------------------------------------------------------------
# Fonction principale d'export
# ---------------------------------------------------------------------------

def export_to_svg(diagram: VoronoiDiagram, output_path: str,
                  width: int = 800, height: int = 600,
                  show_labels: bool = True) -> None:
    """
    Exporte le diagramme de Voronoï dans un fichier SVG.

    Paramètres :
        diagram     : résultat du calcul du diagramme de Voronoï.
        output_path : chemin du fichier SVG à créer.
        width       : largeur du SVG en pixels.
        height      : hauteur du SVG en pixels.
        show_labels : afficher ou non les coordonnées des sites.

    Raises :
        IOError : si l'écriture du fichier échoue.
    """
    pad = STYLE["padding"]
    x_min = min(p.x for p in diagram.sites)
    x_max = max(p.x for p in diagram.sites)
    y_min = min(p.y for p in diagram.sites)
    y_max = max(p.y for p in diagram.sites)

    # Calcul de la transformation (espace données → espace SVG)
    data_w = max(x_max - x_min, 1.0)
    data_h = max(y_max - y_min, 1.0)
    available_w = width - 2 * pad
    available_h = height - 2 * pad
    scale = min(available_w / data_w, available_h / data_h)

    # Centrage
    offset_x = pad + (available_w - data_w * scale) / 2 - x_min * scale
    offset_y = pad + (available_h - data_h * scale) / 2 - y_min * scale

    def transform(p: Point) -> tuple[float, float]:
        """Transforme un point de l'espace données vers l'espace SVG."""
        sx = p.x * scale + offset_x
        sy = p.y * scale + offset_y
        return sx, sy

    # -----------------------------------------------------------------------
    # Construction de l'arbre XML
    # -----------------------------------------------------------------------
    svg = ET.Element("svg", {
        "xmlns":   "http://www.w3.org/2000/svg",
        "version": "1.1",
        "width":   str(width),
        "height":  str(height),
        "viewBox": f"0 0 {width} {height}",
    })

    # Métadonnées
    title = ET.SubElement(svg, "title")
    title.text = "Diagramme de Voronoï"
    desc = ET.SubElement(svg, "desc")
    desc.text = f"Voronoï avec {len(diagram.sites)} sites, généré automatiquement."

    # Fond
    ET.SubElement(svg, "rect", {
        "width":  str(width),
        "height": str(height),
        "fill":   STYLE["background"],
    })

    # Groupe des arêtes de Voronoï
    g_edges = ET.SubElement(svg, "g", {
        "id":           "voronoi-edges",
        "stroke":       STYLE["edge_color"],
        "stroke-width": str(STYLE["edge_width"]),
        "stroke-linecap": "round",
    })

    clipping_rect = (0, 0, width, height)
    for (p1, p2) in diagram.edges:
        sx1, sy1 = transform(p1)
        sx2, sy2 = transform(p2)
        # Vérifier que le segment est dans la zone visible
        clipped = _clip_segment(sx1, sy1, sx2, sy2, clipping_rect)
        if clipped:
            cx1, cy1, cx2, cy2 = clipped
            ET.SubElement(g_edges, "line", {
                "x1": f"{cx1:.2f}",
                "y1": f"{cy1:.2f}",
                "x2": f"{cx2:.2f}",
                "y2": f"{cy2:.2f}",
            })

    # Groupe des sites (germes)
    g_sites = ET.SubElement(svg, "g", {
        "id":   "voronoi-sites",
        "fill": STYLE["site_color"],
    })
    g_labels = ET.SubElement(svg, "g", {
        "id":          "voronoi-labels",
        "fill":        STYLE["site_label"],
        "font-family": "monospace",
        "font-size":   str(STYLE["font_size"]),
    })

    for site in diagram.sites:
        sx, sy = transform(site)
        ET.SubElement(g_sites, "circle", {
            "cx": f"{sx:.2f}",
            "cy": f"{sy:.2f}",
            "r":  str(STYLE["site_radius"]),
        })
        # Anneau extérieur semi-transparent
        ET.SubElement(g_sites, "circle", {
            "cx":   f"{sx:.2f}",
            "cy":   f"{sy:.2f}",
            "r":    str(STYLE["site_radius"] + 3),
            "fill": "none",
            "stroke": STYLE["site_color"],
            "stroke-width": "1",
            "opacity": "0.4",
        })
        if show_labels:
            label = f"({site.x:.1f}, {site.y:.1f})"
            ET.SubElement(g_labels, "text", {
                "x":           f"{sx + 8:.2f}",
                "y":           f"{sy - 6:.2f}",
                "text-anchor": "start",
            }).text = label

    # Légende
    _add_legend(svg, len(diagram.sites), len(diagram.edges), width, height)

    # -----------------------------------------------------------------------
    # Écriture du fichier
    # -----------------------------------------------------------------------
    rough_string = ET.tostring(svg, encoding="unicode")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

    with open(output_path, "wb") as f:
        f.write(pretty_xml)


# ---------------------------------------------------------------------------
# Fonctions utilitaires SVG
# ---------------------------------------------------------------------------

def _add_legend(svg: ET.Element, nb_sites: int, nb_edges: int,
                width: int, height: int) -> None:
    """Ajoute une petite légende en bas à gauche du SVG."""
    g = ET.SubElement(svg, "g", {
        "id":          "legend",
        "fill":        "#a6adc8",
        "font-family": "sans-serif",
        "font-size":   "11",
    })
    texts = [
        f"Sites : {nb_sites}",
        f"Arêtes : {nb_edges}",
        "Algorithme : Bowyer-Watson + Delaunay dual",
    ]
    y_base = height - 12
    for i, text in enumerate(reversed(texts)):
        ET.SubElement(g, "text", {
            "x": "10",
            "y": str(y_base - i * 14),
        }).text = text


def _clip_segment(
    x1: float, y1: float,
    x2: float, y2: float,
    rect: tuple[float, float, float, float]
) -> Optional[tuple[float, float, float, float]]:
    """
    Algorithme de Liang-Barsky pour clipper un segment à un rectangle.

    Retourne (cx1, cy1, cx2, cy2) si le segment est visible, sinon None.
    """
    x_min, y_min, x_max, y_max = rect
    dx = x2 - x1
    dy = y2 - y1

    p = [-dx, dx, -dy, dy]
    q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]

    t0, t1 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if abs(pi) < 1e-10:
            if qi < 0:
                return None  # Parallèle et en dehors
        else:
            r = qi / pi
            if pi < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)

    if t0 > t1:
        return None

    cx1 = x1 + t0 * dx
    cy1 = y1 + t0 * dy
    cx2 = x1 + t1 * dx
    cy2 = y1 + t1 * dy
    return cx1, cy1, cx2, cy2

