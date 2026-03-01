from typing import List
from phase2.grok.src.geometry import Vertex

def load_points_from_file(filename: str) -> List[Vertex]:
    points = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.replace(' ', ',').split(',')
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) == 2:
                try:
                    points.append(Vertex(float(parts[0]), float(parts[1])))
                except ValueError:
                    pass
    return points