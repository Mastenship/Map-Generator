# Square-Grid Coordinates and Map Reading — Working Reference

**Status:** Working convention recorded 2026-10-21; agreed direction is east-right/north-up square indexing, with the exact long-distance world reference frame still to be chosen.

**Readers:** Human DM, LLM working through Map Generator COTs, map drawing tool and future renderer. This is a shared reference, not a command to insert the whole manual inside every final map or COT.

**Source:** `GRID_TOOLS/SQUARE/Square_Grid_With_Edge_Midpoints.py` and its generated SVG. The original HEX reference and historical COT source remain preserved.

## 1. The basic map-reading rule

**Read right, then up: easting (E) first, northing (N) second.** East lies to the **right** of the map; north lies toward the **top**. The southwest corner is the origin for a local sheet unless an explicit source sheet or world origin is supplied.

Our square *cell* address uses the form **`CELL(E,N)`**. On the drawn sheet its compact label remains **`(E,N)`**.

- `E` is the integer square-column address and **increases eastward**.
- `N` is the integer square-row address and **increases northward**.
- A square label identifies an *area*, **not** the precise center point, not a gridline intersection and not a real UTM coordinate.
- Each square and border shared by adjacent squares occupies a consistent position in this addressing system.
- A specific point within a square requires an additional measured position or an expressly named anchor.

For a standard 20-by-20 sheet beginning with the southwest cell `CELL(0,0)`:

| Position on sheet | Square address |
| --- | --- |
| Southwest (bottom-left) | `CELL(0,0)` |
| Southeast (bottom-right) | `CELL(19,0)` |
| Northwest (top-left) | `CELL(0,19)` |
| Northeast (top-right) | `CELL(19,19)` |

This replaces the original SVG labeling that increased the second coordinate downward.

## 2. Distinguish the three coordinate concepts

**Square address:** `CELL(E,N)` indicates which whole grid square contains something. The displayed pair `(E,N)` is an abbreviation under this convention.

**Measured geographic point:** `POINT(E_m,N_m)` expresses the actual easting and northing in meters **relative to a named reference frame**, with sub-square precision. For example, the center of an indoor 2-meter cell can be a full meter north and east of its southwest corner. Meters are consistent with the current indoor working grid; the final global/outdoor reference convention and projection are still an open design decision.

**SVG pixel position:** `(x_px,y_px)` refers to the drawing canvas. SVG Y increases **down**, so pixel Y must be computed by inverting the geographical northing. Pixel addresses are not world addresses.

Do not confuse `CELL(3,4)` with an easting of three meters and a northing of four meters. A cell reference must be interpreted using the sheet's stated scale and origin.

## 3. Map-sheet metadata

Every drawn sheet or completed map package should carry at minimum:

- `MAP_ID`: identifier that distinguishes this map from other maps, scales and versions.
- `REFERENCE_FRAME_ID`: the geographic reference and orientation to which measured points belong (details pending).
- `GRID_TYPE`: `SQUARE`, the current preferred working architecture.
- `CELL_FIRST_E`, `CELL_FIRST_N`: integer addresses of the **southwest cell** of the sheet.
- `COLS`, `ROWS`: number of columns and rows drawn.
- `CELL_WIDTH_M`: physical distance represented by one grid square (may vary from map to map).
- `SHEET_SW_E_M`, `SHEET_SW_N_M`: measured location of the southwest outer corner of the sheet, in the named reference frame.
- `CELL_DRAW_SIZE_PX`: visual drawing size, presently **100 pixels**.
- Parent/source map and asset-library references when this sheet develops an existing region.

These are proposed readable field names for discussion, **not yet a finalized serialization schema**. The physical meter coordinate origin should have a defined relationship to the grid indexing origin.

## 4. Drawing the north-up sheet in SVG

The existing Python grid draws straight lines and center, lower and shared-edge dots. It now generates **north-up square labels**.

For a sheet with `R` rows and bottom-row northing `N0`:

```text
northing_cell = N0 + (R - 1 - svg_row_from_top)
easting_cell  = E0 + svg_col_from_left
```

For measured points, using a southwest sheet corner `(E_sw,N_sw)`, square width `m_per_cell`, drawing width `px_per_cell`, and `R` rows:

```text
x_px = (E_m - E_sw) * px_per_cell / m_per_cell
y_px = R * px_per_cell - (N_m - N_sw) * px_per_cell / m_per_cell
```

These formulas are for the map's **local planar reference frame**. A world-size spherical/planetary projection and conversions across reference frames remain to be designed. The renderer must not silently reinterpret coordinates from incompatible map frames.

**SVG pixel Y goes down; geographic northing goes up.** This is an intentional conversion, not a contradiction.

## 5. Existing dots and shared boundaries

The source square-grid SVG preserves these graphical anchors:

- **Center `C`**: dot at the geometric center of the cell.
- **Edge midpoints `N`, `E`, `S`, `W`**: the red dot at the midpoint of each boundary, drawn only once when that boundary is shared.
- **Lower anchor `L`**: additional interior dot drawn **0.4 cell-height below** the center in SVG, toward geographic south. This is a useful graphics anchor, *not* the southern edge of the cell.

An illustrative way to refer to a marker during DM/LLM discussion is `CELL(3,4):C` or `CELL(3,4):EDGE_E`. At a shared border, `CELL(3,4):EDGE_E` and `CELL(4,4):EDGE_W` refer to the **same physical edge**, not two walls or two crossings. Canonical edge-ID serialization is still open.

The dots assist navigation and symbol positioning. **Do not force actual walls, doors, river banks, roads, furniture, forests or topography onto dots or full-square increments.** A measurable feature may occupy a small portion of a cell, cross an edge at a non-midpoint, or span many cells.

A complete final map may hide display dots and labels while retaining the same geometry and coordinates.

## 6. Putting the next sheet beside the first

For the example 20-by-20 grid with **the same cell scale and reference frame**:

| Sheet | Southwest-cell address | Covered cell indices |
| --- | --- | --- |
| Sheet A | `CELL(0,0)` | E 0–19, N 0–19 |
| Sheet B placed directly **east** | `CELL(20,0)` | E 20–39, N 0–19 |
| Sheet C placed directly **north** | `CELL(0,20)` | E 0–19, N 20–39 |
| Sheet D placed directly **west** | `CELL(-20,0)` | E −20–−1, N 0–19 |

In Python, `grid_origin_e` and `grid_origin_n` specify the southwest cell indices; the renderer changes labels while preserving its 100-pixel squares and dots.

If the scale is `100 meters per square`, Sheet A is 2,000 meters wide. Sheet B's southwest physical corner lies 2,000 meters east of Sheet A's southwest corner. A stream or road ending on Sheet A's eastern edge must begin at the **same measured northing** on Sheet B's western edge, even if neither crosses at an edge-midpoint dot.

The physical position and asset identity of the shared feature are preserved by the map packages, not inferred from the colors of drawn stamps.

## 7. Zooming into an existing square

To zoom from a country/valley map to a site or building:

1. Identify the **source `MAP_ID` and source cell(s)**.
2. Retrieve that completed map's spatial data and its **own preserved asset library**.
3. Establish a new, finer sheet physical extent, measured origin and meters-per-cell.
4. Refine already-established rivers, roads, ridges, settlements and structures rather than generating unrelated replacements.
5. Save the more detailed child map and **its own asset library**; retain source feature and map references.

**Important:** `CELL(3,4)` on a 1-km grid and `CELL(3,4)` on a 2-m grid are not the same geographic square. Full references must include the map identity and scale/reference-frame metadata. Use measured positions to locate the same geographical point across maps.

This also applies when generating a larger sheet from an existing small map or adjoining sheets of similar size.

## 8. Indoor working scale and wall geometry

The current indoor design uses **2 meters per square** at **100 SVG pixels per square**, corresponding to 50 drawing pixels per meter.

The real thickness, height and shape of each wall belong to the wall's physical map record. A 0.30-meter wall would draw about 15 pixels thick at this working scale, although its physical geometry is not constrained to an integral number of pixels.

A wall or doorway may be located with grid addresses and anchors **plus precise measured offsets**. Usable room dimensions derive from the actual inner wall faces, not just cell counts.

Outdoor squares may represent larger distances, but must declare their physical scale; a 100-pixel drawing square is **not universally two meters**.

## 9. What the LLM must read and what the DM must see

The LLM receives the map metadata, coordinate conventions, affected cells/neighboring sheets, asset-library context and any necessary measured feature geometry. It need not read the entire raw SVG markup to understand what is present.

The DM sees a legible map with coordinate labels, orientation, scale, meaningful symbols/stamps and a concise legend. A separate booklet or COT reference can contain the full rules; the final map only needs a usable abbreviated legend and enough metadata to remain intelligible by itself.

Feature data, terrain causation and artifact identities remain distinct from the stamps or lines used to draw them.

## 10. Relation to actual military systems

The **current MGRS** is a globally specified alphanumeric grid referencing UTM/UPS projected coordinates in meters, including grid-zone identifiers and 100-kilometer square identifiers. The Map Generator's numeric `CELL(E,N)` labels are **NOT official MGRS references** and must not be presented as such.

Our initial approach borrows the practical measured-grid principle and military **easting first, northing second** ordering. Later real-Earth integration could use genuine MGRS/UTM with proper zone/datum/projection metadata. For a fictional planet, those Earth-specific zone rules do not automatically apply.

References:
- [NGA Office of Geomatics — Coordinate Systems](https://earth-info.nga.mil/?action=coordsys&dir=coordsys)
- [USGS — How UTM coordinates are measured](https://www.usgs.gov/faqs/how-are-utm-coordinates-measured-usgs-topographic-maps)
- [FGDC — How to read US National Grid](https://www.fgdc.gov/usng/how-to-read-usng)

## 11. Items still to resolve before declaring a complete world-coordinate standard

- The named physical reference frame for an entire fictional country/world, origin and potentially curved planetary surface.
- Final shared physical unit for all maps, outdoor scale choices and procedures for changing scale.
- Canonical shared-edge IDs, local measured point and polygon serialization, and precision rules.
- Parent/child map transforms and relationships between widely separated coordinate frames.
- Placement/legend/stamp vocabulary for topography and constructed features.
- Map-sheet metadata field spelling in the original generator's DSL and the later renderer's data contract.

**Implementation note:** The revised Python source and regenerated example SVG fix the northing-label direction and allow origin offsets; they do not yet implement full physical-coordinate transforms or complete MGRS. The retained historical hex tool remains unchanged.
