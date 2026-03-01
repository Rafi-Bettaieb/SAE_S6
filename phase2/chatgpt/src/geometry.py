"""
geometry.py
Fonctions géométriques robustes pour le diagramme de Voronoï.
"""

import math

EPSILON = 1e-9


class GeometryError(Exception):
    pass


def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)


def perpendicular_bisector(p1, p2):
    if abs(p1[0] - p2[0]) < EPSILON and abs(p1[1] - p2[1]) < EPSILON:
        raise GeometryError("Points identiques détectés.")

    mx, my = midpoint(p1, p2)

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    length = math.hypot(dx, dy)
    dx /= length
    dy /= length

    A = dx
    B = dy
    C = -(A * mx + B * my)

    return A, B, C


def clip_polygon(polygon, A, B, C, keep_point):

    def signed_distance(point):
        return A * point[0] + B * point[1] + C

    keep_sign = signed_distance(keep_point)

    def is_inside(point):
        return signed_distance(point) * keep_sign >= -EPSILON

    def intersection(p1, p2):
        x1, y1 = p1
        x2, y2 = p2

        dx = x2 - x1
        dy = y2 - y1

        denom = A * dx + B * dy
        if abs(denom) < EPSILON:
            return None

        t = -(A * x1 + B * y1 + C) / denom
        return (x1 + t * dx, y1 + t * dy)

    new_polygon = []
    n = len(polygon)

    for i in range(n):
        current = polygon[i]
        previous = polygon[i - 1]

        current_inside = is_inside(current)
        previous_inside = is_inside(previous)

        if current_inside:
            if not previous_inside:
                inter = intersection(previous, current)
                if inter:
                    new_polygon.append(inter)
            new_polygon.append(current)

        elif previous_inside:
            inter = intersection(previous, current)
            if inter:
                new_polygon.append(inter)

    return remove_duplicates(new_polygon)


def remove_duplicates(polygon):
    cleaned = []
    for p in polygon:
        if not any(
            abs(p[0] - q[0]) < EPSILON and abs(p[1] - q[1]) < EPSILON
            for q in cleaned
        ):
            cleaned.append(p)
    return cleaned