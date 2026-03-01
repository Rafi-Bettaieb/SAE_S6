"""
voronoi_calc.py
---------------
Calcul du diagramme de Voronoï à partir d'un ensemble de points 2D.

Approche : Algorithme de Fortune (ligne de balayage) implémenté from scratch.
Pour simplifier l'implémentation tout en restant correct, on utilise une
version robuste basée sur la triangulation de Delaunay duale, construite
manuellement via la méthode de Bowyer-Watson, puis on en déduit les arêtes
de Voronoï comme les perpendiculaires des cercles circonscrits.
"""

import math
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Structures de données de base
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Point:
    """Un point 2D immuable."""
    x: float
    y: float

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Point":
        return Point(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> "Point":
        return Point(self.x / scalar, self.y / scalar)

    def distance_to(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        return f"Point({self.x:.3f}, {self.y:.3f})"


@dataclass
class Triangle:
    """Triangle défini par trois points (pour la triangulation de Delaunay)."""
    a: Point
    b: Point
    c: Point
    circumcenter: Optional[Point] = field(default=None, init=False)
    circumradius: float = field(default=0.0, init=False)

    def __post_init__(self):
        self.circumcenter, self.circumradius = self._compute_circumcircle()

    def _compute_circumcircle(self) -> tuple[Optional[Point], float]:
        """Calcule le centre et le rayon du cercle circonscrit au triangle."""
        ax, ay = self.a.x, self.a.y
        bx, by = self.b.x, self.b.y
        cx, cy = self.c.x, self.c.y

        D = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(D) < 1e-10:
            # Points colinéaires : pas de cercle circonscrit
            return None, float("inf")

        ux = ((ax**2 + ay**2) * (by - cy) +
              (bx**2 + by**2) * (cy - ay) +
              (cx**2 + cy**2) * (ay - by)) / D

        uy = ((ax**2 + ay**2) * (cx - bx) +
              (bx**2 + by**2) * (ax - cx) +
              (cx**2 + cy**2) * (bx - ax)) / D

        center = Point(ux, uy)
        radius = center.distance_to(self.a)
        return center, radius

    def point_in_circumcircle(self, p: Point) -> bool:
        """Retourne True si le point p est DANS le cercle circonscrit."""
        if self.circumcenter is None:
            return False
        return self.circumcenter.distance_to(p) < self.circumradius - 1e-10

    def shares_edge_with(self, other: "Triangle") -> bool:
        """Vérifie si deux triangles partagent une arête."""
        shared = sum(
            1 for v in (other.a, other.b, other.c)
            if v in (self.a, self.b, self.c)
        )
        return shared == 2

    def edges(self) -> list[tuple[Point, Point]]:
        """Retourne les 3 arêtes du triangle (triées pour comparaison)."""
        return [
            _sorted_edge(self.a, self.b),
            _sorted_edge(self.b, self.c),
            _sorted_edge(self.a, self.c),
        ]


def _sorted_edge(p1: Point, p2: Point) -> tuple[Point, Point]:
    """Retourne une arête triée de façon canonique (pour la déduplication)."""
    if (p1.x, p1.y) < (p2.x, p2.y):
        return (p1, p2)
    return (p2, p1)


# ---------------------------------------------------------------------------
# Triangulation de Bowyer-Watson (Delaunay)
# ---------------------------------------------------------------------------

def bowyer_watson(points: list[Point]) -> list[Triangle]:
    """
    Triangulation de Delaunay via l'algorithme de Bowyer-Watson.

    Principe :
        1. Créer un super-triangle englobant tous les points.
        2. Pour chaque point, supprimer les triangles dont le cercle
           circonscrit contient ce point (cavité de Delaunay).
        3. Re-trianguler la cavité en reliant le nouveau point aux
           arêtes du polygone de la cavité.
        4. Supprimer les triangles ayant un sommet du super-triangle.
    """
    if len(points) < 3:
        raise ValueError("Il faut au moins 3 points pour trianguler.")

    # 1. Super-triangle suffisamment grand
    min_x = min(p.x for p in points)
    max_x = max(p.x for p in points)
    min_y = min(p.y for p in points)
    max_y = max(p.y for p in points)

    dx = max_x - min_x
    dy = max_y - min_y
    delta = max(dx, dy) * 10 + 10  # marge généreuse

    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    st_a = Point(mid_x - 2 * delta, mid_y - delta)
    st_b = Point(mid_x, mid_y + 2 * delta)
    st_c = Point(mid_x + 2 * delta, mid_y - delta)
    super_triangle = Triangle(st_a, st_b, st_c)
    super_vertices = {st_a, st_b, st_c}

    triangulation: list[Triangle] = [super_triangle]

    # 2. Insertion point par point
    for point in points:
        # Trouver les triangles « mauvais » (cercle circonscrit contient le point)
        bad_triangles: list[Triangle] = [
            t for t in triangulation if t.point_in_circumcircle(point)
        ]

        # 3. Trouver le polygone de la cavité (arêtes non partagées)
        boundary_edges: list[tuple[Point, Point]] = []
        for bt in bad_triangles:
            for edge in bt.edges():
                # Une arête est sur la frontière si elle n'est partagée
                # qu'avec UN SEUL mauvais triangle
                shared = sum(
                    1 for ot in bad_triangles
                    if ot is not bt and edge in ot.edges()
                )
                if shared == 0:
                    boundary_edges.append(edge)

        # Supprimer les mauvais triangles
        for bt in bad_triangles:
            triangulation.remove(bt)

        # Re-trianguler la cavité
        for edge in boundary_edges:
            new_tri = Triangle(edge[0], edge[1], point)
            triangulation.append(new_tri)

    # 4. Retirer les triangles connectés au super-triangle
    triangulation = [
        t for t in triangulation
        if not (t.a in super_vertices or
                t.b in super_vertices or
                t.c in super_vertices)
    ]

    return triangulation


# ---------------------------------------------------------------------------
# Construction du diagramme de Voronoï depuis la triangulation de Delaunay
# ---------------------------------------------------------------------------

@dataclass
class VoronoiDiagram:
    """
    Résultat du calcul du diagramme de Voronoï.

    Attributs :
        sites       : points d'entrée (germes)
        edges       : liste d'arêtes (paire de Points) du diagramme de Voronoï
        cell_edges  : dictionnaire {site: [arêtes de la cellule]}
        bounds      : (x_min, y_min, x_max, y_max) englobant les sites
    """
    sites: list[Point]
    edges: list[tuple[Point, Point]]
    cell_edges: dict[Point, list[tuple[Point, Point]]]
    bounds: tuple[float, float, float, float]


def compute_voronoi(points: list[Point]) -> VoronoiDiagram:
    """
    Calcule le diagramme de Voronoï des points donnés.

    Étapes :
        1. Triangulation de Delaunay (Bowyer-Watson).
        2. Les arêtes de Voronoï sont les segments reliant les centres
           des cercles circonscrits des triangles adjacents.
        3. Les arêtes de Voronoï ouvertes (bord du convex hull) sont
           prolongées jusqu'aux limites de la zone d'affichage.
    """
    if len(points) < 2:
        raise ValueError("Il faut au moins 2 points pour un diagramme de Voronoï.")

    # Dédoublonnage des points
    unique_points = list({(p.x, p.y): p for p in points}.values())
    if len(unique_points) < 2:
        raise ValueError("Les points doivent être distincts.")

    # Calcul des bornes (avec marge pour l'affichage)
    margin = 50.0
    x_min = min(p.x for p in unique_points) - margin
    x_max = max(p.x for p in unique_points) + margin
    y_min = min(p.y for p in unique_points) - margin
    y_max = max(p.y for p in unique_points) + margin
    bounds = (x_min, y_min, x_max, y_max)

    if len(unique_points) == 2:
        # Cas dégénéré : une seule bissectrice perpendiculaire
        edges = _bisector_edge(unique_points[0], unique_points[1], bounds)
        cell_edges = {
            unique_points[0]: edges,
            unique_points[1]: edges,
        }
        return VoronoiDiagram(unique_points, edges, cell_edges, bounds)

    # Triangulation de Delaunay
    triangles = bowyer_watson(unique_points)
    if not triangles:
        raise RuntimeError("La triangulation de Delaunay a échoué.")

    # Construction des arêtes de Voronoï
    voronoi_edges: list[tuple[Point, Point]] = []
    cell_edges: dict[Point, list[tuple[Point, Point]]] = {
        p: [] for p in unique_points
    }

    # Pour chaque paire de triangles adjacents, relier leurs circumcenters
    processed: set[tuple[int, int]] = set()
    for i, t1 in enumerate(triangles):
        for j, t2 in enumerate(triangles):
            if i >= j:
                continue
            if (i, j) in processed:
                continue
            if t1.shares_edge_with(t2):
                processed.add((i, j))
                if t1.circumcenter and t2.circumcenter:
                    # Ignorer les arêtes dégénérées (circumcenters confondus)
                    if t1.circumcenter.distance_to(t2.circumcenter) < 1e-8:
                        continue
                    edge = (t1.circumcenter, t2.circumcenter)
                    voronoi_edges.append(edge)
                    # Associer l'arête aux sites partagés
                    shared_sites = [
                        v for v in (t1.a, t1.b, t1.c)
                        if v in (t2.a, t2.b, t2.c)
                    ]
                    for site in shared_sites:
                        if site in cell_edges:
                            cell_edges[site].append(edge)

    # Gérer les arêtes ouvertes (triangles sur le bord convex hull)
    # Pour chaque triangle sans voisin sur une arête, prolonger vers l'infini
    all_edges_count: dict[tuple[Point, Point], int] = {}
    for t in triangles:
        for edge in t.edges():
            all_edges_count[edge] = all_edges_count.get(edge, 0) + 1

    for t in triangles:
        if t.circumcenter is None:
            continue
        for edge in t.edges():
            if all_edges_count.get(edge, 0) == 1:
                # Arête de frontière : prolonger le rayon depuis le circumcenter
                p1, p2 = edge
                # Direction perpendiculaire à l'arête, vers l'extérieur
                mid = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                # Perpendiculaire
                perp = Point(-dy, dx)
                norm = math.hypot(perp.x, perp.y)
                if norm < 1e-10:
                    continue
                perp = Point(perp.x / norm, perp.y / norm)

                # S'assurer que la direction pointe vers l'extérieur
                # (opposé au troisième sommet du triangle)
                third = next(
                    v for v in (t.a, t.b, t.c) if v != p1 and v != p2
                )
                to_third = Point(third.x - mid.x, third.y - mid.y)
                if perp.x * to_third.x + perp.y * to_third.y > 0:
                    perp = Point(-perp.x, -perp.y)

                # Prolonger jusqu'au bord de la boîte englobante
                far_length = (x_max - x_min + y_max - y_min) * 2
                far_point = Point(
                    t.circumcenter.x + perp.x * far_length,
                    t.circumcenter.y + perp.y * far_length,
                )
                clipped = _clip_ray_to_box(t.circumcenter, far_point, bounds)
                if clipped:
                    ray_edge = (t.circumcenter, clipped)
                    voronoi_edges.append(ray_edge)
                    for site in (p1, p2):
                        if site in cell_edges:
                            cell_edges[site].append(ray_edge)

    return VoronoiDiagram(
        sites=unique_points,
        edges=voronoi_edges,
        cell_edges=cell_edges,
        bounds=bounds,
    )


# ---------------------------------------------------------------------------
# Fonctions utilitaires géométriques
# ---------------------------------------------------------------------------

def _bisector_edge(
    p1: Point, p2: Point,
    bounds: tuple[float, float, float, float]
) -> list[tuple[Point, Point]]:
    """Crée la bissectrice perpendiculaire entre deux points, clippée aux bornes."""
    mid = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    perp = Point(-dy, dx)
    norm = math.hypot(perp.x, perp.y)
    if norm < 1e-10:
        return []
    perp = Point(perp.x / norm, perp.y / norm)
    x_min, y_min, x_max, y_max = bounds
    far = (x_max - x_min + y_max - y_min) * 2
    a = Point(mid.x - perp.x * far, mid.y - perp.y * far)
    b = Point(mid.x + perp.x * far, mid.y + perp.y * far)
    ca = _clip_ray_to_box(mid, a, bounds)
    cb = _clip_ray_to_box(mid, b, bounds)
    if ca and cb:
        return [(ca, cb)]
    return []


def _clip_ray_to_box(
    origin: Point,
    far: Point,
    bounds: tuple[float, float, float, float]
) -> Optional[Point]:
    """
    Clip le segment [origin → far] à la boîte définie par bounds.
    Retourne le point d'intersection le plus proche de far (sur le bord),
    ou None si aucune intersection n'est trouvée.
    """
    x_min, y_min, x_max, y_max = bounds
    dx = far.x - origin.x
    dy = far.y - origin.y

    t_min = 0.0
    t_max = 1.0

    for edge_x, sign_x, limit in [
        (dx, 1, x_max), (dx, -1, x_min),
        (dy, 1, y_max), (dy, -1, y_min),
    ]:
        pass  # placeholder, on utilise la méthode classique ci-dessous

    # Méthode de Cohen-Sutherland simplifiée : paramétrique
    t_candidates = []
    if abs(dx) > 1e-10:
        t_candidates.append((x_min - origin.x) / dx)
        t_candidates.append((x_max - origin.x) / dx)
    if abs(dy) > 1e-10:
        t_candidates.append((y_min - origin.y) / dy)
        t_candidates.append((y_max - origin.y) / dy)

    for t in t_candidates:
        if t <= 0:
            continue
        ix = origin.x + dx * t
        iy = origin.y + dy * t
        if x_min - 1e-6 <= ix <= x_max + 1e-6 and y_min - 1e-6 <= iy <= y_max + 1e-6:
            return Point(ix, iy)

    return None


# ---------------------------------------------------------------------------
# Lecture de fichier de points
# ---------------------------------------------------------------------------

def load_points_from_file(filepath: str) -> list[Point]:
    """
    Charge des points depuis un fichier texte.

    Formats supportés :
        - Une paire "x y" ou "x,y" par ligne.
        - Les lignes vides et les commentaires (#) sont ignorés.

    Encodage : tente d'abord UTF-8, puis latin-1 en repli (compatible
    avec les fichiers créés sous Windows sans encodage explicite).

    Raises :
        FileNotFoundError : si le fichier n'existe pas.
        ValueError        : si une ligne ne peut pas être parsée.
    """
    # Tentative UTF-8 d'abord, repli sur latin-1 si nécessaire
    for encoding in ("utf-8", "latin-1"):
        try:
            with open(filepath, "r", encoding=encoding) as f:
                raw = f.read()
            break  # Lecture réussie
        except UnicodeDecodeError:
            continue
    else:
        # En dernier recours : lecture avec remplacement des caractères inconnus
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()

    points: list[Point] = []
    for lineno, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Accepter séparateurs espace, virgule ou tabulation
        parts = line.replace(",", " ").replace("\t", " ").split()
        if len(parts) < 2:
            raise ValueError(
                f"Ligne {lineno} invalide : '{line}' "
                f"(format attendu : 'x y' ou 'x,y')"
            )
        try:
            x, y = float(parts[0]), float(parts[1])
        except ValueError:
            raise ValueError(
                f"Ligne {lineno} : impossible de convertir '{parts[0]}' "
                f"ou '{parts[1]}' en nombre."
            )
        points.append(Point(x, y))

    if len(points) < 2:
        raise ValueError("Le fichier doit contenir au moins 2 points.")
    return points
