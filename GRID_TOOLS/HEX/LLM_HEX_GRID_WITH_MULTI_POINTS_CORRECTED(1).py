"""Draw flat-top hex graph paper with mathematically exact SVG edge anchors.

This is a revision of the user's small Python script. It retains the odd-column
vertical offset grid, (col,row) labels, central and lower overlay dots, and six
red edge-midpoint overlays. Cell dimensions are in SVG units, not world units.

The SVG contains 400 cells for the default 20 by 20 grid; each *shared* edge
receives one marker. This drawing code does not assign game-world scale.
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape


def hex_vertices_flat(cx, cy, r):
    """Return the 6 flat-top vertices clockwise in SVG coordinates."""
    return [
        (cx + r * math.cos(math.radians(60 * i)),
         cy + r * math.sin(math.radians(60 * i)))
        for i in range(6)
    ]


def hex_grid_svg_flat_with_edge_midpoints(
    cols, rows, r, decimals=4, stroke="#333", fill="none",
    stroke_width=1, font_size=9, font_color="#333",
    dot_color="#333", dot_radius=1, edge_dot_color="#c00", margin=10,
):
    """Generate a self-contained SVG; overlay dots track drawn edges exactly.

    Important implementation details:
      1. Vertices are quantized ONCE and used for both polygons and red anchors.
      2. Shared edges are recognized by their two canonical endpoint pairs.
      3. Red midpoints are (endpoint A + endpoint B) / 2, with NO pixel rounding.
      4. Margins and ceil-sized canvas avoid clipping edge markers.
    """
    if cols < 1 or rows < 1 or r <= 0 or decimals < 0 or margin < 0:
        raise ValueError("Need positive cols, rows, radius; nonnegative precision and margin")

    h = math.sqrt(3) * r
    dx = 1.5 * r
    dy = h
    num = lambda n: f"{n:.{decimals}f}"
    # A midpoint of vertices with N decimal places may need N+1 places.
    edge_num = lambda n: f"{n:.{decimals + 1}f}"

    # Flat-top cell bounding rectangle: width 2r, height sqrt(3)*r.
    max_x = margin + (cols - 1) * dx + 2 * r
    max_y = margin + (rows - 1) * dy + h + ((cols > 1) * h / 2)
    viewport_width = math.ceil(max_x + margin + dot_radius + stroke_width / 2)
    viewport_height = math.ceil(max_y + margin + dot_radius + stroke_width / 2)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{viewport_width}" height="{viewport_height}" '
        f'viewBox="0 0 {viewport_width} {viewport_height}">',
        '<!-- Cols grow rightward; rows grow downward; odd columns stagger lower. -->',
    ]
    rendered_edges = set()
    edge_circles = []

    for col in range(cols):
        for row in range(rows):
            cx = margin + col * dx + r
            cy = margin + row * dy + (col % 2) * (dy / 2) + h / 2

            # Use these SAME displayed vertices for polygon and midpoint math.
            vertices = [tuple(round(value, decimals) for value in xy)
                        for xy in hex_vertices_flat(cx, cy, r)]
            vertices_s = " ".join(f"{num(x)},{num(y)}" for x, y in vertices)
            svg.append(f'<g id="hex-{col}-{row}">')
            svg.append(f'<polygon points="{vertices_s}" '
                       f'stroke="{escape(stroke)}" fill="{escape(fill)}" '
                       f'stroke-width="{num(stroke_width)}"/>')
            svg.append(f'<text x="{num(cx)}" y="{num(cy - r * 0.7)}" '
                       f'font-size="{num(font_size)}" fill="{escape(font_color)}" '
                       f'text-anchor="middle" dominant-baseline="hanging">'
                       f'({col},{row})</text>')
            svg.append(f'<circle id="hex-{col}-{row}-center" '
                       f'cx="{num(cx)}" cy="{num(cy)}" '
                       f'r="{num(dot_radius)}" fill="{escape(dot_color)}"/>')
            svg.append(f'<circle id="hex-{col}-{row}-bottom" '
                       f'cx="{num(cx)}" cy="{num(cy + r * 0.7)}" '
                       f'r="{num(dot_radius)}" fill="{escape(dot_color)}"/>')
            svg.append('</g>')

            for i in range(6):
                start, end = vertices[i], vertices[(i + 1) % 6]
                edge_key = tuple(sorted((start, end)))
                if edge_key in rendered_edges:
                    continue
                rendered_edges.add(edge_key)
                mx = (start[0] + end[0]) / 2
                my = (start[1] + end[1]) / 2
                edge_circles.append(
                    f'<circle id="edge-mid-{len(edge_circles)}" '
                    f'cx="{edge_num(mx)}" cy="{edge_num(my)}" '
                    f'r="{num(dot_radius)}" fill="{escape(edge_dot_color)}"/>'
                )

    # Draw edge dots last so all shared-edge overlay markers remain visible.
    svg.append('<g id="edge-midpoint-overlays">')
    svg.extend(edge_circles)
    svg.append('</g>')
    svg.append('</svg>')
    return "\n".join(svg) + "\n"


if __name__ == "__main__":
    svg_code = hex_grid_svg_flat_with_edge_midpoints(
        cols=20, rows=20, r=50, decimals=4,
        dot_color="#333", dot_radius=1, edge_dot_color="#c00",
    )
    destination = Path(__file__).with_name("Hex_Grid_With_Edge_Midpoints.svg")
    destination.write_text(svg_code, encoding="utf-8")
    print(f"SVG generated: {destination}")
