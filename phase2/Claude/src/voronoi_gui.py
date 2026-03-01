"""
voronoi_gui.py
--------------
Interface graphique Tkinter pour l'application de diagramme de Voronoï.

L'interface permet de :
    - Charger un fichier de points (format texte).
    - Générer et afficher le diagramme de Voronoï sur un canevas.
    - Exporter le résultat en SVG.
    - Ajouter des points à la main en cliquant sur le canevas.
    - Réinitialiser / changer de jeu de points.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import math
import os
from typing import Optional

from voronoi_calc import VoronoiDiagram, Point, compute_voronoi, load_points_from_file
from voronoi_svg import export_to_svg
from voronoi_img import export_to_image


# ---------------------------------------------------------------------------
# Palette de couleurs (thème sombre cohérent avec le SVG)
# ---------------------------------------------------------------------------

COLORS = {
    "bg":           "#1e1e2e",
    "bg_panel":     "#313244",
    "bg_btn":       "#45475a",
    "bg_btn_hover": "#585b70",
    "accent":       "#89b4fa",
    "accent2":      "#a6e3a1",
    "danger":       "#f38ba8",
    "text":         "#cdd6f4",
    "text_dim":     "#6c7086",
    "edge":         "#89b4fa",
    "site":         "#f38ba8",
    "canvas_bg":    "#11111b",
    "grid":         "#1e1e2e",
}

FONT_TITLE  = ("Segoe UI", 14, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 9)


# ---------------------------------------------------------------------------
# Application principale
# ---------------------------------------------------------------------------

class VoronoiApp(tk.Tk):
    """Fenêtre principale de l'application."""

    def __init__(self):
        super().__init__()
        self.title("Diagramme de Voronoï")
        self.geometry("1100x720")
        self.minsize(800, 550)
        self.configure(bg=COLORS["bg"])

        # État interne
        self.points: list[Point] = []
        self.diagram: Optional[VoronoiDiagram] = None
        self.filepath: Optional[str] = None
        self._show_labels = tk.BooleanVar(value=True)
        self._show_sites  = tk.BooleanVar(value=True)
        self._show_grid   = tk.BooleanVar(value=True)

        # Construction de l'UI
        self._build_ui()
        self._bind_events()

        # Points d'exemple par défaut
        self._load_default_points()

    # -----------------------------------------------------------------------
    # Construction de l'interface
    # -----------------------------------------------------------------------

    def _build_ui(self):
        """Crée tous les widgets de l'interface."""
        # ── Panneau gauche (contrôles) ──
        self.panel = tk.Frame(self, bg=COLORS["bg_panel"], width=240)
        self.panel.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self.panel.pack_propagate(False)

        # Titre
        tk.Label(
            self.panel, text="🔷 Voronoï",
            font=FONT_TITLE, bg=COLORS["bg_panel"], fg=COLORS["accent"]
        ).pack(pady=(20, 4), padx=16, anchor="w")
        tk.Label(
            self.panel, text="Générateur de diagramme",
            font=FONT_SMALL, bg=COLORS["bg_panel"], fg=COLORS["text_dim"]
        ).pack(padx=16, anchor="w")

        _separator(self.panel)

        # ── Section Fichier ──
        _section_label(self.panel, "FICHIER DE POINTS")

        self.btn_open = _button(self.panel, "📂  Ouvrir un fichier…",
                                self._open_file)
        self.lbl_file = tk.Label(
            self.panel, text="Aucun fichier chargé",
            font=FONT_SMALL, bg=COLORS["bg_panel"], fg=COLORS["text_dim"],
            wraplength=210, justify="left"
        )
        self.lbl_file.pack(padx=16, anchor="w", pady=(2, 0))

        _separator(self.panel)

        # ── Section Points manuels ──
        _section_label(self.panel, "POINTS MANUELS")
        tk.Label(
            self.panel,
            text="Clic gauche sur le canevas\npour ajouter un point.",
            font=FONT_SMALL, bg=COLORS["bg_panel"], fg=COLORS["text_dim"],
            justify="left"
        ).pack(padx=16, anchor="w")

        self.lbl_count = tk.Label(
            self.panel, text="Points : 0",
            font=FONT_MONO, bg=COLORS["bg_panel"], fg=COLORS["accent"]
        )
        self.lbl_count.pack(padx=16, anchor="w", pady=(6, 0))

        _button(self.panel, "🗑  Effacer les points", self._clear_points,
                color=COLORS["danger"])

        _separator(self.panel)

        # ── Section Calcul ──
        _section_label(self.panel, "CALCUL")
        self.btn_compute = _button(
            self.panel, "⚡  Générer le diagramme", self._compute,
            color=COLORS["accent2"]
        )

        _separator(self.panel)

        # ── Section Options ──
        _section_label(self.panel, "OPTIONS D'AFFICHAGE")
        _checkbox(self.panel, "Afficher les étiquettes",
                  self._show_labels, self._redraw)
        _checkbox(self.panel, "Afficher les sites",
                  self._show_sites, self._redraw)
        _checkbox(self.panel, "Grille de fond",
                  self._show_grid, self._redraw)

        _separator(self.panel)

        # ── Section Export ──
        _section_label(self.panel, "EXPORT")
        self.btn_export = _button(
            self.panel, "💾  Exporter en SVG…", self._export_svg,
            color="#cba6f7"
        )
        self.btn_export.config(state=tk.DISABLED)

        self.btn_export_img = _button(
            self.panel, "🖼  Exporter en image…", self._export_image,
            color="#fab387"
        )
        self.btn_export_img.config(state=tk.DISABLED)

        _separator(self.panel)

        # Barre de statut en bas du panneau
        self.lbl_status = tk.Label(
            self.panel, text="Prêt.",
            font=FONT_SMALL, bg=COLORS["bg_panel"], fg=COLORS["text_dim"],
            wraplength=210, justify="left"
        )
        self.lbl_status.pack(padx=16, pady=8, anchor="w", side=tk.BOTTOM)

        # ── Canevas principal ──
        canvas_frame = tk.Frame(self, bg=COLORS["canvas_bg"])
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=COLORS["canvas_bg"],
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _bind_events(self):
        """Lie les événements clavier/souris."""
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    # -----------------------------------------------------------------------
    # Chargement des points
    # -----------------------------------------------------------------------

    def _load_default_points(self):
        """Charge un jeu de points d'exemple pour démarrer."""
        defaults = [
            (100, 150), (250, 80),  (400, 200), (300, 350),
            (150, 300), (500, 120), (450, 380), (200, 450),
            (350, 480), (80,  400), (530, 300), (280, 200),
        ]
        self.points = [Point(x, y) for x, y in defaults]
        self._update_count()
        self._compute()

    def _open_file(self):
        """Ouvre un fichier de points via une boîte de dialogue."""
        path = filedialog.askopenfilename(
            title="Choisir un fichier de points",
            filetypes=[
                ("Fichiers texte", "*.txt *.csv *.dat *.pts"),
                ("Tous les fichiers", "*.*"),
            ]
        )
        if not path:
            return

        try:
            self.points = load_points_from_file(path)
            self.filepath = path
            filename = os.path.basename(path)
            self.lbl_file.config(
                text=f"✓ {filename}\n({len(self.points)} points)",
                fg=COLORS["accent2"]
            )
            self._update_count()
            self._set_status(f"Fichier chargé : {filename}")
            self._compute()
        except FileNotFoundError:
            messagebox.showerror("Fichier introuvable",
                                 f"Impossible d'ouvrir :\n{path}")
        except ValueError as e:
            messagebox.showerror("Erreur de format", str(e))

    def _clear_points(self):
        """Efface tous les points."""
        self.points.clear()
        self.diagram = None
        self.filepath = None
        self.btn_export.config(state=tk.DISABLED)
        self.btn_export_img.config(state=tk.DISABLED)
        self.lbl_file.config(text="Aucun fichier chargé", fg=COLORS["text_dim"])
        self._update_count()
        self.canvas.delete("all")
        self._draw_grid()
        self._set_status("Points effacés.")

    # -----------------------------------------------------------------------
    # Ajout de points à la souris
    # -----------------------------------------------------------------------

    def _on_canvas_click(self, event: tk.Event):
        """Ajoute un point aux coordonnées du clic (espace données)."""
        # Convertir les coordonnées canevas → espace données
        data_point = self._canvas_to_data(event.x, event.y)
        if data_point is None:
            # Pas encore de transformation définie, utiliser les coords brutes
            data_point = Point(float(event.x), float(event.y))
        self.points.append(data_point)
        self._update_count()

        # Affichage immédiat du point
        r = 4
        self.canvas.create_oval(
            event.x - r, event.y - r,
            event.x + r, event.y + r,
            fill=COLORS["site"], outline="", tags="site_preview"
        )

        # Recalcul automatique si au moins 3 points
        if len(self.points) >= 3:
            self._compute()
        self._set_status(
            f"Point ajouté : ({data_point.x:.1f}, {data_point.y:.1f})"
        )

    def _canvas_to_data(self, cx: float, cy: float) -> Optional[Point]:
        """
        Convertit des coordonnées canevas en coordonnées de l'espace données.
        Retourne None si la transformation inverse n'est pas disponible.
        """
        if not hasattr(self, "_transform_params"):
            return None
        scale, offset_x, offset_y, h = self._transform_params
        if scale < 1e-10:
            return None
        x = (cx - offset_x) / scale
        y = (cy - offset_y) / scale
        return Point(x, y)

    # -----------------------------------------------------------------------
    # Calcul et dessin
    # -----------------------------------------------------------------------

    def _compute(self):
        """Lance le calcul du diagramme de Voronoï et redessine."""
        if len(self.points) < 2:
            self._set_status("Ajoutez au moins 2 points.")
            return

        self._set_status("Calcul en cours…")
        self.update_idletasks()

        try:
            self.diagram = compute_voronoi(self.points)
            self.btn_export.config(state=tk.NORMAL)
            self.btn_export_img.config(state=tk.NORMAL)
            n = len(self.diagram.edges)
            s = len(self.diagram.sites)
            self._set_status(f"Diagramme calculé : {s} sites, {n} arêtes.")
            self._redraw()
        except ValueError as e:
            messagebox.showwarning("Calcul impossible", str(e))
            self._set_status("Erreur de calcul.")
        except Exception as e:
            messagebox.showerror("Erreur inattendue", str(e))
            self._set_status("Erreur inattendue.")

    def _redraw(self):
        """Redessine le canevas avec le diagramme actuel."""
        self.canvas.delete("all")
        self._draw_grid()
        if self.diagram:
            self._draw_diagram(self.diagram)
        elif self.points:
            self._draw_points_only()

    def _draw_grid(self):
        """Dessine une grille légère en fond."""
        if not self._show_grid.get():
            return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        step = 40
        for x in range(0, w, step):
            self.canvas.create_line(x, 0, x, h,
                                    fill=COLORS["grid"], width=1, tags="grid")
        for y in range(0, h, step):
            self.canvas.create_line(0, y, w, y,
                                    fill=COLORS["grid"], width=1, tags="grid")

    def _draw_diagram(self, diag: VoronoiDiagram):
        """Dessine le diagramme complet (arêtes + sites + labels)."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return

        pad = 40
        x_min = min(p.x for p in diag.sites)
        x_max = max(p.x for p in diag.sites)
        y_min = min(p.y for p in diag.sites)
        y_max = max(p.y for p in diag.sites)
        data_w = max(x_max - x_min, 1.0)
        data_h = max(y_max - y_min, 1.0)
        scale = min((w - 2 * pad) / data_w, (h - 2 * pad) / data_h)
        offset_x = pad + ((w - 2 * pad) - data_w * scale) / 2 - x_min * scale
        offset_y = pad + ((h - 2 * pad) - data_h * scale) / 2 - y_min * scale

        # Mémoriser la transformation pour les clics
        self._transform_params = (scale, offset_x, offset_y, h)

        def to_canvas(p: Point) -> tuple[float, float]:
            return p.x * scale + offset_x, p.y * scale + offset_y

        # Arêtes de Voronoï
        for (p1, p2) in diag.edges:
            cx1, cy1 = to_canvas(p1)
            cx2, cy2 = to_canvas(p2)
            # Clipper grossièrement au canevas
            if _any_in_bounds(cx1, cy1, cx2, cy2, w, h):
                self.canvas.create_line(
                    cx1, cy1, cx2, cy2,
                    fill=COLORS["edge"], width=1.5,
                    tags="edge", capstyle=tk.ROUND
                )

        # Sites et labels
        if self._show_sites.get():
            for site in diag.sites:
                sx, sy = to_canvas(site)
                r = 5
                # Halo
                self.canvas.create_oval(
                    sx - r - 3, sy - r - 3,
                    sx + r + 3, sy + r + 3,
                    outline=COLORS["site"], fill="", width=1, tags="site"
                )
                # Point
                self.canvas.create_oval(
                    sx - r, sy - r,
                    sx + r, sy + r,
                    fill=COLORS["site"], outline="", tags="site"
                )
                if self._show_labels.get():
                    label = f"({site.x:.0f},{site.y:.0f})"
                    self.canvas.create_text(
                        sx + 10, sy - 10,
                        text=label,
                        fill=COLORS["text_dim"],
                        font=FONT_MONO,
                        anchor="w",
                        tags="label"
                    )

    def _draw_points_only(self):
        """Dessine uniquement les points quand le diagramme n'est pas calculé."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        for p in self.points:
            # Affichage brut dans l'espace canevas
            r = 5
            self.canvas.create_oval(
                p.x - r, p.y - r, p.x + r, p.y + r,
                fill=COLORS["site"], outline=""
            )

    # -----------------------------------------------------------------------
    # Export SVG
    # -----------------------------------------------------------------------

    def _export_svg(self):
        """Exporte le diagramme courant en SVG."""
        if not self.diagram:
            messagebox.showwarning("Rien à exporter",
                                   "Générez d'abord le diagramme.")
            return

        path = filedialog.asksaveasfilename(
            title="Enregistrer le SVG",
            defaultextension=".svg",
            filetypes=[("SVG vectoriel", "*.svg"), ("Tous les fichiers", "*.*")],
            initialfile="voronoi.svg",
        )
        if not path:
            return

        try:
            export_to_svg(
                self.diagram,
                path,
                width=1200,
                height=900,
                show_labels=self._show_labels.get(),
            )
            self._set_status(f"SVG exporté : {os.path.basename(path)}")
            messagebox.showinfo(
                "Export réussi",
                f"Diagramme exporté avec succès :\n{path}"
            )
        except Exception as e:
            messagebox.showerror("Erreur d'export", str(e))
            self._set_status("Erreur lors de l'export SVG.")

    def _export_image(self):
        """Exporte le diagramme courant en image raster (PNG, JPEG, BMP)."""
        if not self.diagram:
            messagebox.showwarning("Rien à exporter",
                                   "Générez d'abord le diagramme.")
            return

        path = filedialog.asksaveasfilename(
            title="Enregistrer l'image",
            defaultextension=".png",
            filetypes=[
                ("PNG (recommandé)", "*.png"),
                ("JPEG",             "*.jpg"),
                ("BMP",              "*.bmp"),
                ("Tous les fichiers","*.*"),
            ],
            initialfile="voronoi.png",
        )
        if not path:
            return

        # Boîte de dialogue de résolution
        resolution = _ask_resolution(self)
        if resolution is None:
            return  # L'utilisateur a annulé

        self._set_status("Génération de l'image en cours…")
        self.update_idletasks()

        try:
            w, h = resolution
            export_to_image(
                self.diagram,
                path,
                width=w,
                height=h,
                show_labels=self._show_labels.get(),
                show_grid=self._show_grid.get(),
            )
            self._set_status(f"Image exportée : {os.path.basename(path)}")
            messagebox.showinfo(
                "Export réussi",
                f"Image exportée ({w}×{h} px) :\n{path}"
            )
        except ValueError as e:
            messagebox.showerror("Format non supporté", str(e))
            self._set_status("Format d'image non supporté.")
        except Exception as e:
            messagebox.showerror("Erreur d'export", str(e))
            self._set_status("Erreur lors de l'export image.")

    # -----------------------------------------------------------------------
    # Événements divers
    # -----------------------------------------------------------------------

    def _on_canvas_resize(self, _event: tk.Event):
        """Redessine quand la fenêtre est redimensionnée."""
        self._redraw()

    # -----------------------------------------------------------------------
    # Helpers UI
    # -----------------------------------------------------------------------

    def _update_count(self):
        self.lbl_count.config(text=f"Points : {len(self.points)}")

    def _set_status(self, message: str):
        self.lbl_status.config(text=message)


# ---------------------------------------------------------------------------
# Widgets utilitaires
# ---------------------------------------------------------------------------

def _separator(parent: tk.Widget):
    """Ligne de séparation horizontale."""
    tk.Frame(parent, height=1, bg=COLORS["bg_btn"]).pack(
        fill=tk.X, padx=12, pady=8
    )


def _section_label(parent: tk.Widget, text: str):
    """Étiquette de section en majuscules."""
    tk.Label(
        parent, text=text,
        font=("Segoe UI", 8, "bold"),
        bg=COLORS["bg_panel"], fg=COLORS["text_dim"]
    ).pack(padx=16, anchor="w", pady=(4, 4))


def _button(
    parent: tk.Widget,
    text: str,
    command,
    color: str = COLORS["accent"]
) -> tk.Button:
    """Crée un bouton stylisé."""
    btn = tk.Button(
        parent, text=text, command=command,
        bg=COLORS["bg_btn"], fg=color,
        activebackground=COLORS["bg_btn_hover"], activeforeground=color,
        font=FONT_NORMAL, relief=tk.FLAT,
        padx=10, pady=6, cursor="hand2", anchor="w"
    )
    btn.pack(fill=tk.X, padx=12, pady=3)

    def on_enter(_e): btn.config(bg=COLORS["bg_btn_hover"])
    def on_leave(_e): btn.config(bg=COLORS["bg_btn"])
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def _checkbox(
    parent: tk.Widget,
    text: str,
    variable: tk.BooleanVar,
    command
) -> tk.Checkbutton:
    """Crée une case à cocher stylisée."""
    cb = tk.Checkbutton(
        parent, text=text, variable=variable, command=command,
        bg=COLORS["bg_panel"], fg=COLORS["text"],
        activebackground=COLORS["bg_panel"], activeforeground=COLORS["text"],
        selectcolor=COLORS["bg_btn"],
        font=FONT_NORMAL, relief=tk.FLAT, cursor="hand2"
    )
    cb.pack(padx=16, anchor="w", pady=1)
    return cb


# ---------------------------------------------------------------------------
# Fonctions utilitaires de dessin
# ---------------------------------------------------------------------------

def _any_in_bounds(
    x1: float, y1: float,
    x2: float, y2: float,
    w: float, h: float,
    margin: float = 50.0
) -> bool:
    """Vérifie grossièrement si un segment est dans la zone visible."""
    return not (
        max(x1, x2) < -margin or min(x1, x2) > w + margin or
        max(y1, y2) < -margin or min(y1, y2) > h + margin
    )


# ---------------------------------------------------------------------------
# Boîte de dialogue : choix de la résolution d'export image
# ---------------------------------------------------------------------------

class _ResolutionDialog(tk.Toplevel):
    """
    Fenêtre modale permettant de choisir la résolution de l'image exportée.

    Propose des préréglages (HD, Full HD, 4K) ou une saisie libre.
    Retourne un tuple (width, height) via self.result, ou None si annulé.
    """

    PRESETS = [
        ("HD       (1280 × 720)",  1280,  720),
        ("Full HD  (1920 × 1080)", 1920, 1080),
        ("2K       (2560 × 1440)", 2560, 1440),
        ("4K       (3840 × 2160)", 3840, 2160),
        ("Carré    (2000 × 2000)", 2000, 2000),
        ("Personnalisé…",          None,  None),
    ]

    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.title("Résolution de l'image")
        self.configure(bg=COLORS["bg_panel"])
        self.resizable(False, False)
        self.result: Optional[tuple[int, int]] = None

        self._selected = tk.IntVar(value=1)  # Full HD par défaut
        self._custom_w = tk.StringVar(value="1920")
        self._custom_h = tk.StringVar(value="1080")

        self._build()
        self.transient(parent)
        self.grab_set()
        # Centrer sur le parent
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - self.winfo_width())  // 2
        py = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")

    def _build(self):
        tk.Label(
            self, text="Choisissez la résolution :",
            font=FONT_NORMAL, bg=COLORS["bg_panel"], fg=COLORS["text"]
        ).pack(padx=20, pady=(16, 8), anchor="w")

        for i, (label, w, h) in enumerate(self.PRESETS):
            rb = tk.Radiobutton(
                self, text=label, variable=self._selected, value=i,
                command=self._on_select,
                bg=COLORS["bg_panel"], fg=COLORS["text"],
                activebackground=COLORS["bg_panel"],
                activeforeground=COLORS["accent"],
                selectcolor=COLORS["bg_btn"],
                font=FONT_MONO, relief=tk.FLAT
            )
            rb.pack(padx=24, anchor="w", pady=1)

        # Champs de saisie personnalisée
        self._custom_frame = tk.Frame(self, bg=COLORS["bg_panel"])
        self._custom_frame.pack(padx=24, pady=4, anchor="w")
        tk.Label(
            self._custom_frame, text="Largeur :",
            font=FONT_SMALL, bg=COLORS["bg_panel"], fg=COLORS["text_dim"]
        ).grid(row=0, column=0, sticky="w", padx=(0, 6))
        tk.Entry(
            self._custom_frame, textvariable=self._custom_w, width=7,
            bg=COLORS["bg_btn"], fg=COLORS["text"], font=FONT_MONO,
            insertbackground=COLORS["text"], relief=tk.FLAT
        ).grid(row=0, column=1, padx=(0, 12))
        tk.Label(
            self._custom_frame, text="Hauteur :",
            font=FONT_SMALL, bg=COLORS["bg_panel"], fg=COLORS["text_dim"]
        ).grid(row=0, column=2, sticky="w", padx=(0, 6))
        tk.Entry(
            self._custom_frame, textvariable=self._custom_h, width=7,
            bg=COLORS["bg_btn"], fg=COLORS["text"], font=FONT_MONO,
            insertbackground=COLORS["text"], relief=tk.FLAT
        ).grid(row=0, column=3)

        self._on_select()  # État initial

        # Boutons OK / Annuler
        btn_frame = tk.Frame(self, bg=COLORS["bg_panel"])
        btn_frame.pack(fill=tk.X, padx=16, pady=(12, 16))

        tk.Button(
            btn_frame, text="Annuler", command=self.destroy,
            bg=COLORS["bg_btn"], fg=COLORS["text_dim"],
            activebackground=COLORS["bg_btn_hover"],
            font=FONT_NORMAL, relief=tk.FLAT, padx=12, pady=5, cursor="hand2"
        ).pack(side=tk.RIGHT, padx=(6, 0))

        tk.Button(
            btn_frame, text="  Exporter  ", command=self._on_ok,
            bg=COLORS["bg_btn"], fg=COLORS["accent2"],
            activebackground=COLORS["bg_btn_hover"],
            font=FONT_NORMAL, relief=tk.FLAT, padx=12, pady=5, cursor="hand2"
        ).pack(side=tk.RIGHT)

    def _on_select(self):
        """Active/désactive les champs personnalisés."""
        idx = self._selected.get()
        _, w, h = self.PRESETS[idx]
        is_custom = (w is None)
        state = tk.NORMAL if is_custom else tk.DISABLED
        for widget in self._custom_frame.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.config(state=state)
        if not is_custom:
            self._custom_w.set(str(w))
            self._custom_h.set(str(h))

    def _on_ok(self):
        """Valide la saisie et ferme la fenêtre."""
        try:
            w = int(self._custom_w.get())
            h = int(self._custom_h.get())
            if w < 100 or h < 100:
                raise ValueError("Dimensions trop petites (minimum 100 px).")
            if w > 8000 or h > 8000:
                raise ValueError("Dimensions trop grandes (maximum 8000 px).")
            self.result = (w, h)
            self.destroy()
        except ValueError as e:
            messagebox.showerror(
                "Résolution invalide",
                f"Valeur incorrecte : {e}\n"
                "Saisissez des entiers entre 100 et 8000.",
                parent=self
            )


def _ask_resolution(parent: tk.Tk) -> Optional[tuple[int, int]]:
    """Affiche la boîte de dialogue de résolution et retourne le choix."""
    dialog = _ResolutionDialog(parent)
    parent.wait_window(dialog)
    return dialog.result
