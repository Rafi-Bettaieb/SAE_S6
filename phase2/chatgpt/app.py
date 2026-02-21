"""
app.py
Interface graphique dynamique adaptée à l'image générée.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from voronoi import VoronoiDiagram
from svg_export import SVGExporter


class VoronoiApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Voronoi Diagram Generator")

        # 🔹 Taille initiale confortable
        self.initial_width = 1000
        self.initial_height = 800

        self.root.geometry(f"{self.initial_width}x{self.initial_height}")

        self.canvas = tk.Canvas(
            root,
            width=self.initial_width,
            height=self.initial_height - 80,
            bg="white"
        )
        self.canvas.pack()

        frame = tk.Frame(root)
        frame.pack()

        tk.Button(frame, text="Charger points", command=self.load_points).pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="Générer", command=self.generate).pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="Exporter SVG", command=self.export_svg).pack(side=tk.LEFT, padx=10)

        self.points = []
        self.cells = []

    def load_points(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filepath:
            return

        try:
            with open(filepath, "r") as f:
                self.points = []

                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    if "," in line:
                        parts = line.split(",")
                    else:
                        parts = line.split()

                    if len(parts) != 2:
                        raise ValueError("Format invalide.")

                    x = float(parts[0])
                    y = float(parts[1])
                    self.points.append((x, y))

            if len(self.points) < 2:
                raise ValueError("Il faut au minimum deux points.")

            messagebox.showinfo("Succès", "Points chargés.")

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def compute_dynamic_size(self):

        min_x = min(p[0] for p in self.points)
        max_x = max(p[0] for p in self.points)
        min_y = min(p[1] for p in self.points)
        max_y = max(p[1] for p in self.points)

        width_data = max_x - min_x
        height_data = max_y - min_y

        margin = max(width_data, height_data) * 0.1

        view_width = width_data + 2 * margin
        view_height = height_data + 2 * margin

        BASE_SIZE = 800

        if view_width >= view_height:
            canvas_width = BASE_SIZE
            canvas_height = BASE_SIZE * (view_height / view_width)
        else:
            canvas_height = BASE_SIZE
            canvas_width = BASE_SIZE * (view_width / view_height)

        return int(canvas_width), int(canvas_height), min_x - margin, min_y - margin, view_width, view_height

    def generate(self):

        if not self.points:
            messagebox.showwarning("Attention", "Aucun point chargé.")
            return

        (canvas_width,
         canvas_height,
         self.view_min_x,
         self.view_min_y,
         self.view_width,
         self.view_height) = self.compute_dynamic_size()

        self.canvas.config(width=canvas_width, height=canvas_height)
        self.root.geometry(f"{canvas_width}x{canvas_height+60}")

        bbox = [
            (self.view_min_x, self.view_min_y),
            (self.view_min_x + self.view_width, self.view_min_y),
            (self.view_min_x + self.view_width, self.view_min_y + self.view_height),
            (self.view_min_x, self.view_min_y + self.view_height)
        ]

        diagram = VoronoiDiagram(self.points, bbox)
        self.cells = diagram.compute()

        self.draw(canvas_width, canvas_height)

    def draw(self, canvas_width, canvas_height):

        self.canvas.delete("all")

        def transform(p):
            x = (p[0] - self.view_min_x) * (canvas_width / self.view_width)
            y = (p[1] - self.view_min_y) * (canvas_height / self.view_height)
            return x, y

        for cell in self.cells:
            if not cell:
                continue

            coords = []
            for p in cell:
                x, y = transform(p)
                coords.extend([x, y])

            self.canvas.create_polygon(coords, outline="black", fill="")

        for p in self.points:
            x, y = transform(p)
            self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="red")

    def export_svg(self):

        if not self.cells:
            messagebox.showwarning("Attention", "Générez d'abord le diagramme.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG Files", "*.svg")]
        )

        if not filepath:
            return

        try:
            SVGExporter.export(filepath, self.points, self.cells)
            messagebox.showinfo("Succès", "Export SVG réussi.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


def main():
    root = tk.Tk()
    app = VoronoiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()