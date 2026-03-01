import tkinter as tk
from tkinter import filedialog, messagebox
import math

from geometry import Vertex
from algorithms import delaunay_triangulate, compute_voronoi_edges, clip_line
from utils import load_points_from_file

class VoronoiApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Voronoi Diagram Generator")
        
        self.width = 600
        self.height = 500
        self.points = []
        self.voronoi_lines = [] # To store lines for SVG export
        self.diagram_generated = False 
        
        self._setup_ui()

    def _setup_ui(self):
        self.root.configure(bg="#f0f0f0")
        
        control_frame = tk.Frame(self.root, pady=5, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, anchor="nw") 
        
        tk.Button(control_frame, text="Charger points", command=self.load_points).pack(side=tk.LEFT, padx=(10, 5))
        tk.Button(control_frame, text="Générer", command=self.generate_diagram).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Exporter SVG", command=self.export_svg).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Effacer", command=self.clear).pack(side=tk.LEFT, padx=5)
        
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="white", highlightthickness=1, highlightbackground="#ccc")
        self.canvas.pack(padx=10, pady=20)
        self.canvas.bind("<Button-1>", self.add_point_manual)

    def add_point_manual(self, event):
        if self.diagram_generated:
            return 
        self.points.append((event.x, event.y))
        self.canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, fill="black")

    def load_points(self):
        filepath = filedialog.askopenfilename(title="Sélectionner un fichier", filetypes=(("Fichiers texte", "*.txt *.csv"), ("Tous", "*.*")))
        if not filepath: 
            return
            
        try:
            self.clear()
            vertices = load_points_from_file(filepath)
            
            if not vertices:
                return

            raw_points = [(v.x, v.y) for v in vertices]
            
            # Mise à l'échelle
            min_x = min(p[0] for p in raw_points)
            max_x = max(p[0] for p in raw_points)
            min_y = min(p[1] for p in raw_points)
            max_y = max(p[1] for p in raw_points)
            
            width_data = max(max_x - min_x, 1)
            height_data = max(max_y - min_y, 1)
            margin = 30
            
            scale_x = (self.width - (2 * margin)) / width_data
            scale_y = (self.height - (2 * margin)) / height_data
            scale = min(scale_x, scale_y)
            
            for x, y in raw_points:
                nx = (x - min_x) * scale + margin
                ny = (y - min_y) * scale + margin
                self.points.append((nx, ny))
                self.canvas.create_oval(nx-3, ny-3, nx+3, ny+3, fill="black")
                
            messagebox.showinfo("Succès", f"{len(self.points)} points chargés.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la lecture:\n{e}")

    def generate_diagram(self):
        if len(self.points) < 3:
            messagebox.showwarning("Attention", "Il faut au moins 3 points pour utiliser l'algorithme de Grok.")
            return
            
        self.canvas.delete("all")
        self.voronoi_lines.clear()
        
        vertices = [Vertex(p[0], p[1]) for p in self.points]
        
        try:
            triangles = delaunay_triangulate(vertices)
            edges = compute_voronoi_edges(triangles, vertices)
            
            for v1, v2 in edges:
                clipped = clip_line(v1.x, v1.y, v2.x, v2.y, 0, 0, self.width, self.height)
                if clipped:
                    x1, y1, x2, y2 = clipped
                    self.voronoi_lines.append((x1, y1, x2, y2))
                    self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Le moteur a rencontré une erreur:\n{e}")
            
        for p in self.points:
            self.canvas.create_oval(p[0]-3, p[1]-3, p[0]+3, p[1]+3, fill="black")
            
        self.diagram_generated = True

    def export_svg(self):
        if not self.diagram_generated:
            messagebox.showwarning("Attention", "Générez le diagramme avant d'exporter.")
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("Fichiers SVG", "*.svg")])
        if not filepath: 
            return
            
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n')
                f.write('<rect width="100%" height="100%" fill="white"/>\n')
                
                for x1, y1, x2, y2 in self.voronoi_lines:
                    f.write(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="blue" stroke-width="2"/>\n')
                    
                for p in self.points:
                    f.write(f'<circle cx="{p[0]}" cy="{p[1]}" r="3" fill="black"/>\n')
                    
                f.write('</svg>')
            messagebox.showinfo("Succès", "Fichier SVG exporté avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'exportation:\n{e}")

    def clear(self):
        self.points.clear()
        self.voronoi_lines.clear()
        self.canvas.delete("all")
        self.diagram_generated = False