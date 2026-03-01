import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Tuple
from phase2.grok.src.geometry import Vertex
from algorithms import delaunay_triangulate, compute_voronoi_edges, clip_line
from phase2.grok.src.utils import load_points_from_file

class VoronoiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diagramme de Voronoï - Version Finale")
        self.root.geometry("940x780")

        self.canvas = tk.Canvas(root, width=900, height=700, bg="#f8f9fa", highlightthickness=0)
        self.canvas.pack(pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="Charger fichier points (.txt)", 
                  command=self.load_file, width=28, height=2).pack(side=tk.LEFT, padx=15)
        self.export_btn = tk.Button(btn_frame, text="Exporter en SVG", 
                                    command=self.export_svg, state=tk.DISABLED, width=28, height=2)
        self.export_btn.pack(side=tk.LEFT, padx=15)

        self.points: List[Vertex] = []
        self.vor_edges: List[Tuple[Vertex, Vertex]] = []

    def load_file(self):
        file = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt")])
        if not file:
            return
        try:
            self.points = load_points_from_file(file)
            if len(self.points) < 3:
                raise ValueError("Le fichier doit contenir au moins 3 points.")

            triangles = delaunay_triangulate(self.points)
            self.vor_edges = compute_voronoi_edges(triangles, self.points)

            self.draw_diagram()
            self.export_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Succès", f"{len(self.points)} points → Diagramme correct !")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def draw_diagram(self):
        self.canvas.delete("all")
        if not self.points:
            return

        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        pad = max(maxx-minx, maxy-miny) * 0.22
        xmin, xmax = minx - pad, maxx + pad
        ymin, ymax = miny - pad, maxy + pad

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        scale = min((w-60)/(xmax-xmin), (h-60)/(ymax-ymin))
        ox = 30 - xmin * scale
        oy = 30 - ymin * scale

        for v1, v2 in self.vor_edges:
            clipped = clip_line(v1.x, v1.y, v2.x, v2.y, xmin, ymin, xmax, ymax)
            if clipped:
                x1, y1, x2, y2 = clipped
                self.canvas.create_line(
                    x1*scale + ox, y1*scale + oy,
                    x2*scale + ox, y2*scale + oy,
                    fill="#2c3e50", width=2.2
                )

        for p in self.points:
            x = p.x * scale + ox
            y = p.y * scale + oy
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="#e74c3c", outline="#2c3e50", width=1.5)

    def export_svg(self):
        if not self.points:
            return
        file = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG", "*.svg")])
        if file:
            xs = [p.x for p in self.points]
            ys = [p.y for p in self.points]
            minx, maxx = min(xs), max(xs)
            miny, maxy = min(ys), max(ys)
            pad = max(maxx-minx, maxy-miny) * 0.22
            xmin, xmax = minx - pad, maxx + pad
            ymin, ymax = miny - pad, maxy + pad

            w = 920
            h = 720
            scale = min((w-60)/(xmax-xmin), (h-60)/(ymax-ymin))
            ox = 30 - xmin * scale
            oy = 30 - ymin * scale

            with open(file, 'w', encoding='utf-8') as f:
                f.write(f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">\n')
                f.write('<rect width="100%" height="100%" fill="#f8f9fa"/>\n')
                for v1, v2 in self.vor_edges:
                    clipped = clip_line(v1.x, v1.y, v2.x, v2.y, xmin, ymin, xmax, ymax)
                    if clipped:
                        x1, y1, x2, y2 = clipped
                        x1 = x1*scale + ox
                        y1 = y1*scale + oy
                        x2 = x2*scale + ox
                        y2 = y2*scale + oy
                        f.write(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                                f'stroke="#2c3e50" stroke-width="2.2"/>\n')
                for p in self.points:
                    x = p.x * scale + ox
                    y = p.y * scale + oy
                    f.write(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="#e74c3c" stroke="#2c3e50"/>\n')
                f.write('</svg>\n')
            messagebox.showinfo("Export terminé", f"Sauvegardé :\n{file}")