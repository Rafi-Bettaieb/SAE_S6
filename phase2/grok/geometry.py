import math

class Vertex:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def equals(self, other: 'Vertex') -> bool:
        return math.isclose(self.x, other.x, abs_tol=1e-9) and math.isclose(self.y, other.y, abs_tol=1e-9)

class Edge:
    def __init__(self, v0: Vertex, v1: Vertex):
        self.v0 = v0
        self.v1 = v1

class Triangle:
    def __init__(self, v0: Vertex, v1: Vertex, v2: Vertex):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.circumcircle = self._calc_circumcircle()

    def _calc_circumcircle(self):
        ax, ay = self.v0.x, self.v0.y
        bx, by = self.v1.x, self.v1.y
        cx, cy = self.v2.x, self.v2.y
        D = 2 * (ax*(by - cy) + bx*(cy - ay) + cx*(ay - by))
        if abs(D) < 1e-10:
            raise ValueError("Points colinéaires")
        ux = ((ax**2 + ay**2)*(by - cy) + (bx**2 + by**2)*(cy - ay) + (cx**2 + cy**2)*(ay - by)) / D
        uy = ((ax**2 + ay**2)*(cx - bx) + (bx**2 + by**2)*(ax - cx) + (cx**2 + cy**2)*(bx - ax)) / D
        center = Vertex(ux, uy)
        r = math.hypot(ux - ax, uy - ay)
        return {'c': center, 'r': r}

    def in_circumcircle(self, v: Vertex) -> bool:
        dx = self.circumcircle['c'].x - v.x
        dy = self.circumcircle['c'].y - v.y
        return math.hypot(dx, dy) <= self.circumcircle['r'] + 1e-8