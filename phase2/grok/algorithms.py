import math
from collections import defaultdict
from typing import List, Tuple, Optional
from geometry import Vertex, Edge, Triangle

def super_triangle(points: List[Vertex]) -> Triangle:
    minx = min(p.x for p in points)
    miny = min(p.y for p in points)
    maxx = max(p.x for p in points)
    maxy = max(p.y for p in points)
    dx = maxx - minx
    dy = maxy - miny
    return Triangle(
        Vertex(minx - 3*dx, miny - 3*dy),
        Vertex(maxx + 3*dx, miny - 3*dy),
        Vertex(maxx, maxy + 3*dy)
    )

def delaunay_triangulate(points: List[Vertex]) -> List[Triangle]:
    if len(points) < 3:
        raise ValueError("Au moins 3 points sont requis.")
    unique = []
    for p in points:
        if not any(p.equals(u) for u in unique):
            unique.append(p)
    points = unique

    st = super_triangle(points)
    triangles = [st]

    for p in points:
        bad = [t for t in triangles if t.in_circumcircle(p)]
        edge_count = defaultdict(int)
        for t in bad:
            for e in [(t.v0, t.v1), (t.v1, t.v2), (t.v2, t.v0)]:
                key = tuple(sorted(e, key=id))
                edge_count[key] += 1
        polygon = [Edge(e[0], e[1]) for e, cnt in edge_count.items() if cnt == 1]

        remaining = [t for t in triangles if t not in bad]
        new_tri = []
        for e in polygon:
            try:
                new_tri.append(Triangle(e.v0, e.v1, p))
            except ValueError:
                pass
        triangles = remaining + new_tri

    st_set = {st.v0, st.v1, st.v2}
    triangles = [t for t in triangles if not {t.v0, t.v1, t.v2} & st_set]
    return triangles

def compute_voronoi_edges(triangles: List[Triangle], points: List[Vertex]) -> List[Tuple[Vertex, Vertex]]:
    edge_to_tris = defaultdict(list)
    for t in triangles:
        for pair in [(t.v0, t.v1), (t.v1, t.v2), (t.v2, t.v0)]:
            key = tuple(sorted(pair, key=id))
            edge_to_tris[key].append(t)

    vor_edges = []
    ray_length = 5000.0

    for key, tris in edge_to_tris.items():
        p, q = key
        if len(tris) == 2:
            c1 = tris[0].circumcircle['c']
            c2 = tris[1].circumcircle['c']
            if not c1.equals(c2):
                vor_edges.append((c1, c2))

        elif len(tris) == 1:
            t = tris[0]
            c = t.circumcircle['c']
            third = next(v for v in (t.v0, t.v1, t.v2) if v is not p and v is not q)

            mx = (p.x + q.x) / 2.0
            my = (p.y + q.y) / 2.0

            dx = q.x - p.x
            dy = q.y - p.y

            px1, py1 = -dy, dx
            px2, py2 = dy, -dx

            vec_to_third_x = third.x - mx
            vec_to_third_y = third.y - my
            dot1 = px1 * vec_to_third_x + py1 * vec_to_third_y

            px, py = (px1, py1) if dot1 < 0 else (px2, py2)

            length = math.hypot(px, py)
            if length > 1e-8:
                px /= length
                py /= length
                far = Vertex(c.x + px * ray_length, c.y + py * ray_length)
                vor_edges.append((c, far))

    return vor_edges

def clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax) -> Optional[Tuple[float, float, float, float]]:
    def outcode(x, y):
        code = 0
        if x < xmin: code |= 1
        if x > xmax: code |= 2
        if y < ymin: code |= 4
        if y > ymax: code |= 8
        return code

    oc1 = outcode(x1, y1)
    oc2 = outcode(x2, y2)
    while True:
        if not (oc1 | oc2):
            return x1, y1, x2, y2
        if oc1 & oc2:
            return None
        oc = oc1 if oc1 else oc2
        if oc & 8:
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax
        elif oc & 4:
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin
        elif oc & 2:
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax
        elif oc & 1:
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin
        if oc == oc1:
            x1, y1, oc1 = x, y, outcode(x, y)
        else:
            x2, y2, oc2 = x, y, outcode(x, y)