"""
voronoi.py
Calcul du diagramme de Voronoï par intersection de demi-plans.
"""

from geometry import perpendicular_bisector, clip_polygon


class VoronoiDiagram:

    def __init__(self, points, bounding_box):
        self.points = points
        self.bounding_box = bounding_box
        self.cells = []

    def compute(self):
        self.cells = []

        for i, p in enumerate(self.points):
            polygon = self.bounding_box[:]

            for j, q in enumerate(self.points):
                if i == j:
                    continue

                A, B, C = perpendicular_bisector(p, q)
                polygon = clip_polygon(polygon, A, B, C, p)

                if not polygon:
                    break

            self.cells.append(polygon)

        return self.cells