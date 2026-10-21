def rect_grid_svg_lines_points(
    cols, rows, side=100, stroke="#333", fill="none",
    stroke_width=1, font_size=9, font_color="#333",
    dot_color="#333", dot_radius=1,
    edge_dot_color="#c00", grid_origin_e=0, grid_origin_n=0
):
    """Draw a north-up map sheet using an east/north square-grid convention.

    Grid labels are (E,N): E increases right/east; N increases up/north.
    (grid_origin_e, grid_origin_n) is the SOUTHWEST cell address in
    integer cell indices, not meters or full real-world UTM coordinates.
    An adjacent 20-column sheet to the east starts at grid_origin_e=20.
    Shared edge midpoint dots are emitted once. These dots are visual
    reference anchors; physical features may use sub-cell coordinates.
    SVG downward-positive Y is a rendering coordinate, not northing.
    """
    if not isinstance(cols, int) or not isinstance(rows, int) or cols <= 0 or rows <= 0:
        raise ValueError("cols and rows must be positive integers")
    if not isinstance(grid_origin_e, int) or not isinstance(grid_origin_n, int):
        raise ValueError("grid origins must be integer cell indices")
    if side <= 0:
        raise ValueError("side must be positive")
    width = cols * side
    height = rows * side

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">\n']

    # Draw grid lines
    for i in range(cols + 1):
        x = i * side
        svg.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="{stroke}" stroke-width="{stroke_width}"/>\n')
    for j in range(rows + 1):
        y = j * side
        svg.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="{stroke}" stroke-width="{stroke_width}"/>\n')

    # To prevent redundant dots, store already-rendered midpoints as (x, y)
    rendered_midpoints = set()

    for col in range(cols):
        for svg_row in range(rows):
            easting_cell = grid_origin_e + col
            northing_cell = grid_origin_n + (rows - 1 - svg_row)
            cx = round(col * side + side / 2)
            cy = round(svg_row * side + side / 2)

            # Cell label
            svg.append(f'<text x="{cx}" y="{cy - int(side*0.4)}" font-size="{font_size}" fill="{font_color}" text-anchor="middle" alignment-baseline="hanging">({easting_cell},{northing_cell})</text>\n')
            # Center circle
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{dot_radius}" fill="{dot_color}"/>\n')
            # Bottom circle, 40% down from center toward bottom
            bottom_y = round(cy + (side * 0.4))
            svg.append(f'<circle cx="{cx}" cy="{bottom_y}" r="{dot_radius}" fill="{dot_color}"/>\n')

            # Edge midpoints (top, right, bottom, left)
            edge_midpoints = [
                (cx, cy - side // 2),         # top
                (cx + side // 2, cy),         # right
                (cx, cy + side // 2),         # bottom
                (cx - side // 2, cy),         # left
            ]
            for mx, my in edge_midpoints:
                key = (mx, my)
                if key not in rendered_midpoints:
                    rendered_midpoints.add(key)
                    svg.append(f'<circle cx="{mx}" cy="{my}" r="{dot_radius}" fill="{edge_dot_color}"/>\n')

    svg.append("</svg>\n")
    return "".join(svg)

if __name__ == "__main__":
    svg_code = rect_grid_svg_lines_points(cols=20, rows=20, side=100, dot_radius=1, edge_dot_color="#c00")
    output_path = "Square_Grid_With_Edge_Midpoints.svg"
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg_code)
    print(f"SVG generated: {output_path}")
