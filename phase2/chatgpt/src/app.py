"""
app.py
Interface graphique (Vue) pour la génération, l'affichage et l'exportation
de diagrammes de Voronoï.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import random 

from voronoi import VoronoiDiagram
from svg_export import SVGExporter

class VoronoiApp:
    """Contrôleur principal de l'application Tkinter."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Voronoi Diagram Generator")

        # Initialisation adaptative selon la résolution de l'écran
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.initial_width = min(1000, int(screen_width * 0.9))
        self.initial_height = min(700, int(screen_height * 0.8))
        self.root.geometry(f"{self.initial_width}x{self.initial_height}")

        # Interface de contrôle
        frame = tk.Frame(root, pady=10)
        frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(frame, text="Charger points", command=self.load_points).pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="Générer", command=self.generate).pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="Exporter SVG", command=self.export_svg).pack(side=tk.LEFT, padx=10)

        # Zone de rendu
        self.canvas = tk.Canvas(
            root,
            width=self.initial_width - 40,
            height=self.initial_height - 80,
            bg="white"
        )
        self.canvas.pack(pady=10)

        # Modèles de données
        self.points = []
        self.cells = []
        self.colors = []

    def load_points(self) -> None:
        """
        Charge un ensemble de points 2D depuis un fichier texte.
        Supporte les séparateurs par espaces ou virgules.
        """
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filepath:
            return

        try:
            with open(filepath, "r") as f:
                self.points.clear()
                self.cells.clear()
                self.colors.clear()
                self.canvas.delete("all")

                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(",") if "," in line else line.split()

                    if len(parts) != 2:
                        raise ValueError("Format de coordonnées invalide.")

                    self.points.append((float(parts[0]), float(parts[1])))

            if len(self.points) < 2:
                raise ValueError("Un minimum de deux points est requis.")

            messagebox.showinfo("Succès", f"{len(self.points)} points chargés avec succès.")

        except Exception as e:
            messagebox.showerror("Erreur de lecture", str(e))

    def compute_dynamic_size(self):
        """
        Calcule la boîte englobante des données et détermine la taille optimale 
        du canevas pour conserver le ratio (aspect ratio) sans dépasser la taille de l'écran.
        """
        min_x = min(p[0] for p in self.points)
        max_x = max(p[0] for p in self.points)
        min_y = min(p[1] for p in self.points)
        max_y = max(p[1] for p in self.points)

        width_data = max_x - min_x
        height_data = max_y - min_y

        margin = max(width_data, height_data) * 0.1

        view_width = width_data + 2 * margin
        view_height = height_data + 2 * margin

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        # Marges de sécurité pour l'interface système (barre des tâches, bordures)
        max_canvas_w = screen_w - 50
        max_canvas_h = screen_h - 150

        base_w = min(800, max_canvas_w)
        base_h = min(600, max_canvas_h)

        ratio = view_width / view_height

        # Ajustement proportionnel
        if ratio >= 1:
            canvas_width = base_w
            canvas_height = canvas_width / ratio
            if canvas_height > base_h:
                canvas_height = base_h
                canvas_width = canvas_height * ratio
        else:
            canvas_height = base_h
            canvas_width = canvas_height * ratio
            if canvas_width > base_w:
                canvas_width = base_w
                canvas_height = canvas_width / ratio

        return int(canvas_width), int(canvas_height), min_x - margin, min_y - margin, view_width, view_height

    def generate(self) -> None:
        """
        Exécute le moteur algorithmique pour générer le diagramme de Voronoï
        à partir des sites chargés, puis déclenche le rendu visuel.
        """
        if not self.points:
            messagebox.showwarning("Attention", "Aucun site (point) n'est chargé en mémoire.")
            return

        (canvas_width,
         canvas_height,
         self.view_min_x,
         self.view_min_y,
         self.view_width,
         self.view_height) = self.compute_dynamic_size()

        self.canvas.config(width=canvas_width, height=canvas_height)
        self.root.geometry(f"{canvas_width + 40}x{canvas_height + 80}")

        # Définition de l'univers de calcul (Bounding Box)
        bbox = [
            (self.view_min_x, self.view_min_y),
            (self.view_min_x + self.view_width, self.view_min_y),
            (self.view_min_x + self.view_width, self.view_min_y + self.view_height),
            (self.view_min_x, self.view_min_y + self.view_height)
        ]

        diagram = VoronoiDiagram(self.points, bbox)
        self.cells = diagram.compute()

        # Assignation de couleurs pastel aléatoires pour le rendu des régions
        self.colors = []
        for _ in self.cells:
            r, g, b = random.randint(150, 255), random.randint(150, 255), random.randint(150, 255)
            self.colors.append(f"#{r:02x}{g:02x}{b:02x}")

        self.draw(canvas_width, canvas_height)

    def draw(self, canvas_width: int, canvas_height: int) -> None:
        """
        Affiche les cellules de Voronoï et les sites sur le canevas en appliquant 
        une transformation affine (mise à l'échelle et translation) spatiale.
        """
        self.canvas.delete("all")

        def transform(p):
            x = (p[0] - self.view_min_x) * (canvas_width / self.view_width)
            y = (p[1] - self.view_min_y) * (canvas_height / self.view_height)
            return x, y

        # Tracé des polygones (Régions)
        for i, cell in enumerate(self.cells):
            if not cell:
                continue

            coords = []
            for p in cell:
                x, y = transform(p)
                coords.extend([x, y])
            
            self.canvas.create_polygon(coords, outline="gray", fill=self.colors[i])

        # Tracé des germes (Sites)
        for p in self.points:
            x, y = transform(p)
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="black")

    def export_svg(self) -> None:
        """
        Délègue l'exportation vectorielle du diagramme à la classe SVGExporter.
        """
        if not self.cells:
            messagebox.showwarning("Attention", "Veuillez générer le diagramme avant d'exporter.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG Files", "*.svg")]
        )

        if not filepath:
            return

        try:
            SVGExporter.export(filepath, self.points, self.cells, self.colors)
            messagebox.showinfo("Succès", "Exportation SVG réalisée avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur d'exportation", str(e))


def main():
    root = tk.Tk()
    app = VoronoiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()