"""
svg_export.py
Export SVG dynamique et proportionnel.
"""

class SVGExporter:

    @staticmethod
    def export(filename, points, cells):

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
                f'width="{svg_width}" height="{svg_height}" '
                f'viewBox="{view_min_x} {view_min_y} '
                f'{view_width} {view_height}">\n'
            )

            for cell in cells:
                if not cell:
                    continue
                pts = " ".join(f"{x},{y}" for x, y in cell)
                f.write(
                    f'<polygon points="{pts}" '
                    f'style="fill:none;stroke:black;stroke-width:0.01"/>\n'
                )

            radius = max(view_width, view_height) * 0.01

            for x, y in points:
                f.write(
                    f'<circle cx="{x}" cy="{y}" r="{radius}" '
                    f'style="fill:red"/>\n'
                )

            f.write("</svg>")