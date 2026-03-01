"""
svg_export.py
Module dédié à l'exportation du diagramme de Voronoï au format vectoriel (SVG).
"""

from typing import List, Tuple, Optional

class SVGExporter:
    """Utilitaire pour la génération de fichiers SVG à partir de données géométriques."""

    @staticmethod
    def export(filename: str, 
               points: List[Tuple[float, float]], 
               cells: List[List[Tuple[float, float]]], 
               colors: Optional[List[str]] = None) -> None:
        """
        Exporte les cellules et les sites du diagramme dans un fichier XML/SVG.
        Utilise l'attribut 'viewBox' pour gérer automatiquement l'échelle et les proportions.
        
        :param filename: Chemin absolu ou relatif du fichier de destination.
        :param points: Liste des sites générateurs (coordonnées x, y).
        :param cells: Liste des polygones de Voronoï (chaque polygone est une liste de sommets).
        :param colors: Liste optionnelle de codes couleurs hexadécimaux pour le remplissage.
        """
        if not points:
            return

        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        width_data = max_x - min_x
        height_data = max_y - min_y

        margin = max(width_data, height_data) * 0.1

        view_min_x = min_x - margin
        view_min_y = min_y - margin
        view_width = width_data + 2 * margin
        view_height = height_data + 2 * margin

        BASE_SIZE = 800

        if view_width >= view_height:
            svg_width = BASE_SIZE
            svg_height = BASE_SIZE * (view_height / view_width)
        else:
            svg_height = BASE_SIZE
            svg_width = BASE_SIZE * (view_width / view_height)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{int(svg_width)}" height="{int(svg_height)}" '
                f'viewBox="{view_min_x} {view_min_y} {view_width} {view_height}">\n'
            )

            stroke_w = max(view_width, view_height) * 0.001

            for i, cell in enumerate(cells):
                if not cell:
                    continue
                
                pts = " ".join(f"{x},{y}" for x, y in cell)
                fill_color = colors[i] if colors and i < len(colors) else "none"
                
                f.write(
                    f'  <polygon points="{pts}" '
                    f'style="fill:{fill_color};stroke:gray;stroke-width:{stroke_w}"/>\n'
                )

            radius = max(view_width, view_height) * 0.005

            for x, y in points:
                f.write(
                    f'  <circle cx="{x}" cy="{y}" r="{radius}" '
                    f'style="fill:black"/>\n'
                )

            f.write("</svg>\n")