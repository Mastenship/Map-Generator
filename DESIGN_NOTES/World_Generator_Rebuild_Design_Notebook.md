# World Generator Rebuild — Design Notebook

**Status:** Working notes, not finalized architecture. **Started:** 2026-10-19.
**Goal:** Preserve the world-building ideas from the design discussion. Track established requirements separately from proposed engineering choices.

## Core purpose

The world must exist independently of a character LLM's narrative fluency. During play, character observation, inference, and intention must not become authoritative environmental facts merely because they sound plausible. **Unknown does not mean nonexistent; unknown also does not license invention.** The DM adjudicates consequential unknowns. Human DMs and players must also be able to use and see the world.

## Collaborative authoring

The generator is not an autonomous one-shot process. **DM and LLM reason together through each COT**, potentially over many exchanges. A COT frames a question, examines established facts, discusses options and consequences, proposes results, receives DM corrections/approval, then preserves accepted facts. A preferred sequence should allow revisiting earlier work when downstream changes matter.
Keep the familiar structured-writing convention (section delimiters, named COTs, typed inputs/outputs, scratchpad concepts, checks). Whether to adopt an OTTC-like proposal/commit boundary is an architectural candidate, not yet decided.

## World-building that must survive

Present geography and culture should be explainable as the accumulated result of physical conditions, resource constraints, historical events, economic decisions, adaptation, and decay. Settlements and infrastructure **co-evolve**: a bridge may divert commerce from an upstream ferry town, generate a bridgehead settlement, provoke political and commercial response, and later reshape population patterns. Preserve **reasons and causal dependencies**, not just current placements. Historical layering and taphonomy (ruins, reused foundations, obsolete roads) matter.

## Space, rendering, and sensory realism

Old Python-generated SVG grids are cumbersome (an outdoor hex-system SVG alone ~123 KB). Candidate: compact mathematical coordinates plus an on-demand renderer, not static SVGs as map sources of truth. Regional axial hexes, local Cartesian coordinates, and interior cell/edge grids with multiple levels are *options*, not settled decisions. Shared coordinate transforms and parent/child map relationships need definition.

A DM-facing, simple Minecraft-like voxel viewer, with top-down/free-camera views and object inspection, is desired. A graph-paper-style 2D editor may remain a better authoring tool. The visual style need not constrain physical precision.

Environment should represent wall thickness/materials, door/window type and state, ventilation ducts, shafts, and passages. Traversability, visibility, airborne sound, structural vibration, airflow, and scent **have different paths**. Avoid assuming full physics simulation is necessary; consider presets, approximate propagation and explicit DM adjudication. Sensory signals can come from invisible sources; character interpretations remain separate from world facts.

## Graph-paper grid tools, overlay rendering, and DM composition (discussion, 2026-10-20)

**DM-confirmed starting material:** The GitHub `Mastenship/Map-Generator` repository now includes matching Python/SVG tools at `GRID_TOOLS/HEX/Hex_Grid_With_Edge_Midpoints.{py,svg}` and `GRID_TOOLS/SQUARE/Square_Grid_With_Edge_Midpoints.{py,svg}`. The hex grid is flat-top with odd-column vertical staggering; the square grid uses regular Cartesian cells. Both are 20 × 20 example sheets. Each cell has a coordinate label at the top, a central overlay anchor, and a lower overlay anchor. Shared cell boundaries have red edge-midpoint anchors (six possible sides per hex, four per square). The DM explained that these dots are **places to put display information**, not physical features; the edge anchors also assist in depicting walls, doors, crossings, and other intercell relationships. An object's real footprint or a river's path need not be confined to an overlay anchor. The corrected hex script derives edge midpoints from the drawn vertices, preserving alignment.

**Problem — LLM working context, not DM storage:** Expanded SVG graph paper is verbose (the current example hex SVG is about 306 KB; the square SVG about 127 KB), despite very small Python construction scripts. Lossless compression can save bytes on disk or in transit, but if the decompressed SVG markup is passed to the LLM, its context burden returns. The LLM-run generator should be able to consult compact geometric conventions, coordinate-indexed world data, and targeted deterministic geometry results **without reading every SVG drawing command**. Merely connecting to Python source on GitHub does not guarantee the model can execute it; the execution/runtime interface must be specified separately.

**Proposed visualization technique — overlays on reusable graph paper:** During authored map creation, the LLM reasons through rich geographic/architectural COTs and proposes world placements in logical cells and shared-edge references; the DM reviews and accepts/revises those facts. A deterministic Python drawing tool could translate the **accepted static map data** into one or more transparent SVG overlay layers—terrain, rivers, roads, boundaries, sites, walls/doors, labels, or DM-only secrets. Place these layers over the already-existing hex or square graph-paper SVG, using identical canvas/viewBox, orientation, origin, scale, coordinate calculations, and shared-edge references. The grid is a reusable display template; the overlay depicts data; the **approved map record remains the authoritative deliverable**, not either SVG. Rendering must not invent, alter, or silently commit geographic facts. Different views can select subsets of established facts while keeping the underlying geography fixed.

**Useful boundary principle:** A cell identifies an area; an edge identifies a boundary/connection, ideally one shared logical feature between neighboring cells, not duplicate independent states. The physical path of a river, road, or boundary can be more detailed than midpoint-to-midpoint lines. Overlay markers are graphical convenience; precise terrain/structure geometry, causal history, sensory properties, and object identities belong in map data. The future character parser remains separate from these DM-facing overlays.

**Open coordinate decisions:** Choose outdoor regional geometry/scale, local outdoor and indoor scales, physical units and measurements, edge identity and adjacency, direction/origin conventions, parent/child map placement and transforms, multi-floor elevation, and any off-cell shapes or footprints. The working hex scripts use **offset coordinates**, not the earlier note's proposed axial representation. Their layout is an implementation reference, not approval of every future canonical coordinate convention.

**Open DM interface decision — Inkscape, custom front end, or hybrid:** The DM is weighing using Inkscape to align, inspect, stack and toggle SVG overlays against developing a purpose-built front end for pulling/assembling layers. Inkscape has the benefit of an existing graphical editor and a familiar visual workflow; manual edits must not unintentionally diverge from the approved map data. A custom application could better support map-aware layer toggles, region selection, object inspection, coordinate/edge snapping, DM-only visibility and eventual editing, but creates significant up-front engineering/maintenance work. A **candidate** low-friction progression is to test one base grid plus generated overlay in Inkscape or another ordinary SVG viewer, while retaining the possibility of a dedicated front end later. **No editor choice has been approved, and none is a prerequisite to authoring the first static map.**

**Next small proof of concept (proposed, not committed):** Render a few authored hex features with one river or road crossing a shared boundary, and a few square-grid features including a wall or door on a shared edge, then check pixel alignment, coordinate correctness, layer order, and whether the DM can read the finished graphic. Keep both the coordinate data and the overlays inspectable by a connected LLM.

## Candidate subsystem split

1. Collaborative world-building COTs: generate proposals with rationale.

2. Canonical world record: approved physical/historical facts and causal relationships.

3. Geometry compiler: validate rooms, shared edges, openings, levels, objects and references.

4. **Separate parser/runtime overlay (not generator):** read the finalized static baseline, apply authorized diffs from play, resolve supported spatial/perception queries, and expose bounded observations. Its implementation remains outside the generator redesign's immediate scope.

5. DM/player views: controlled visibility into one authoritative world.

6. ChaOS: interpretation, personality, memory, decisions and proposed actions; **not unilateral environmental authorship**.

## Architecture clarification — STATIC MAP is the generator's deliverable (DM-confirmed, 2026-10-19)

**Accepted requirement:** The generator produces a **completed, pre-authored, static map artifact**. It does **not** generate the environment on the fly during play. World-building COTs are an **authoring-time** DM/LLM collaboration, and stop when the DM accepts the finished map. The result should be equally meaningful as human-viewable map data and as a source for a character's map parser.

**Accepted separation:** During play, the **map parser and its overlay** read that immutable baseline and track only authorized differences from it (e.g., an opened door or container, or a moved chair). Overlay implementation is **not part of the map generator's principal design problem**. Stable object IDs and initial states are useful to support future differences, but runtime state updates do not require rebuilding the static map.

**Existing example:** The uploaded `Black_Mesa_Facility(1).txt` is an instance of the intended *kind* of end product: a self-contained indoor artifact with seven rooms, 5×5-foot grid-scale metadata, per-room dimensions, transitions with initial door states, immovable/movable objects, containers and contents, and five-channel sensory descriptions. It is a **simple example**, not a fully consistent geometry specification or an example of on-the-fly content creation.

**Boundary statement:** The generator authors world facts and packages a map. The parser/runtime resolves observations and game interactions against that static baseline plus a small overlay. ChaOS interprets observations and proposes actions; it does not create authoritative environmental facts by narrative continuation.

## Reading the existing generator through Bridging Document 2

**Reference:** `Mastenship/On-The-Top-Constraint-ChaOS/BRIDGING_DOCUMENTS/02 Producing a Square A Method Demonstration.md` — three ChaOS pillars and the proposer/domain-expert commit method. The following is an *interpretation/application* to world generation, not a claim that the map generator is already a fully governed OTTC square.

| Pillar | Existing correspondence | What a rebuild may improve |
| --- | --- | --- |
| **Conceptual depth** | COTs invoke domain frameworks (physics, geology, hydrology, climate, ecology, transportation geography, settlement theory, functional architecture, archaeological history). Later stages reason against earlier conditions. | Preserve deep concepts and explanations/causal provenance; don't reduce generation to decorative placement. |
| **Chain of thought as process, not product** | Staged COT work yields structured scratchpad outputs. The aim is a final accepted world, not a record of every speculative turn. | DM/LLM discuss each COT for as long as necessary; persist agreed facts, justifications, and relevant dependencies, not uncommitted speculation or a full reasoning transcript. |
| **Qualitative state-machine mechanics** | Named workflow stages, categorical properties, structured output fields, reset/update directives, and chronological logging. | Formalize stage status and approval/revision transitions. **Distinguish authoring workflow states from physical geometry:** accurate dimensions, coordinates, and path calculations may appropriately use deterministic numerical tools. |

**Commit-authority discipline:** The DM is the authoritative creative/world-design decision maker. The LLM proposes. The architecture should not mistake fluency or scientific-sounding prose for confirmation. Geology/economics/etc. are auxiliary foundations for a *fictional world-building tool*, not guarantees of scientific simulation. The model's proposed output must be reviewed before it becomes an established world fact.

## Proposed end-to-end workflow — generator only

**Status:** Proposed sequence for examination; module names/order are not accepted design decisions. Preserve the original layered method, but permit bounded revision **during authoring**, before final static publication.

### Phase A — Initiation and COT contract

1. **World/map premise:** DM and LLM establish what is being authored (planet, region, town, building, isolated dungeon), intended mood/purpose, scale, historical depth, technology/magic/physics assumptions, and fixed DM requirements. **Do not force planet-scale generation when designing one facility.**

2. **Per-COT operating cycle:** load accepted inputs and dependencies → explain the immediate world-building question → discuss options and consequences with the DM → produce a structured proposal → DM accepts, changes, rejects or requests more consideration → preserve only approved results with references and justifications → identify downstream/earlier records potentially affected. Some COTs may take many conversational exchanges.

3. **Working records:** `ACCEPTED_FACTS`, `PROPOSALS_PENDING`, `OPEN_QUESTIONS`, `CAUSAL_DEPENDENCIES`, `AUTHORING_LOG` are candidate logical partitions. Their storage format is undecided.

### Phase B — Outdoor world-building layers (when relevant)

Candidate order:

1. `COT_FOUNDATIONAL_PARAMETERS`: generation premise and relevant setting constraints.

2. `COT_PHYSICS`: laws/conditions when the setting departs from ordinary assumptions.

3. `COT_TERRAIN`: geology, elevation, landforms.

4. `COT_CLIMATE`: climate and geographical influences.

5. `COT_HYDROLOGY`: waterways, watersheds, drainage, water access.

6. `COT_BIOMES`: ecosystems, resources, habitability.

7. `COT_HISTORICAL_DEVELOPMENT`: cultures, migrations, land use, adaptations and previous changes (possibly a cross-cutting repeated inquiry, not one single pass).

8. `COT_SETTLEMENTS`: settlements, founding reasons, population relationships, economic functions.

9. `COT_INFRASTRUCTURE`: roads, ferries, bridges, ports and their network consequences.

10. `COT_LANDMARKS_AND_ASSETS`: distinctive sites, reused assets, ruins and historical evidence.

**Dependency refinement:** The old asset-library COT asks for biome data, while the original generation log shows asset-building before biome generation. A redesign should make prerequisites explicit, avoiding invisible completion by the LLM.

**Feedback case:** An upstream ferry town grows because its crossing channels commerce. A new bridge downstream changes route costs and may redirect traffic. The infrastructure COT must flag affected settlement/economic records for DM discussion and approved revision before the final static map is assembled. Alternatives (adaptation, resistance, seasonal ferry utility, decline) are to be reasoned through, not determined by a single heuristic.

### Phase C — Indoor and site-level construction (when relevant)

Candidate order:

1. `COT_INDOOR_FOUNDATIONS`: purpose, historical setting, scale, materials, floors, links to parent map.

2. `COT_STRUCTURAL_SHELL`: exterior envelope, floors/ceilings, wall thickness, materials, structural openings.

3. `COT_FUNCTIONAL_LAYOUT`: room purposes and spatial relationships.

4. `COT_CIRCULATION`: doors, stairs, corridors, vertical access, blocked/secret passages and links.

5. `COT_ENVIRONMENTAL_SYSTEMS`: ducts, drains, ventilation, light/heat/power sources and conduits.

6. `COT_FEATURES_AND_CONTENTS`: fixtures, furniture, movable objects, containers and initial contents.

7. `COT_ENVIRONMENTAL_CONDITIONS`: wear, damage, state of repair, light, heat, sound/scent sources and other sensory anchors.

8. `COT_FINAL_MAP_ASSEMBLY`: consolidate the approved facility into one static artifact.

**Iterative authoring is not dynamic play-time generation.** Room function can cause a wall/door revision; ventilation may require a shaft through a ceiling; a historical renovation may explain a sealed passage. The DM and LLM resolve those interactions *before the map is frozen*. The old indoor generator's structural/environment/function sequence is a good foundation but may require inter-stage feedback, not strictly one-way execution.

### Phase D — Validate, DM review, and publish

- Assemble the approved world description into a **single self-contained baseline** at the requested scale, or linked static parent/child artifacts when appropriate.

- Validate coordinate frames, shared walls and wall thicknesses, floors/ceilings and level connections, door openings/endpoints/states, navigable topology, object placements/footprints, containers, asset references, and meaningful sensory-system links.

- Check narrative consistency as well: e.g., a described ventilation system should have represented relevant vents/duct connections wherever they influence play.

- Return mechanical contradictions, missing required facts, and unresolved design conflicts to the DM rather than silently fabricate fixes. DM-approved fantasy exceptions can be explicitly identified.

- Obtain final DM approval, then **publish/version the static map**. This is the **end of the generator's operation**. The viewer renders that data; the parser reads it; neither requires the original authoring COTs.

**Candidate final static map payload:** map metadata/scale/orientation/coordinate frame; region/room definitions; physical geometry and cross-level connections; doors and initial states; fixed/movable objects with stable IDs and initial locations; containers and initial contents; lighting, thermal and sensory sources/conditions; relevant physical/sensory transmissions; contextual descriptions and historical provenance, where useful. Exact syntax/schema remains **open**.

## Example mapping: Black Mesa Facility

The already-uploaded `Black_Mesa_Facility(1).txt` includes: Main Entrance, Corridor A, Administrative Office, Living Quarters, Laboratory Wing, Hot Lab, and Lab Support. The Laboratory Wing has a welded bulkhead to Corridor A, an emergency-sealed door to the Hot Lab, and an ajar door to Lab Support; its laboratory fixtures and multi-sensory details are **authored facts present before any character arrives**.

**Reasons to improve representation, not change its purpose:** room-local locations do not establish all room-to-room transforms; examples include object coordinates outside given room dimensions; material assemblies, wall thickness and duct paths are not fully formalized. Those are candidates for geometry validation during generation. Retain its sensory richness, named transitions, room identities, and object/container distinctions.

**Parser-only overlay illustration (not part of generator output):**

```text
STATIC_BASELINE:
  DOOR_LAB_001: Welded_Shut
  CHAIR_OFFICE_001: Position=(5,10)
  FOOTLOCKER_001: Closed

PLAY_OVERLAY:
  CHAIR_OFFICE_001: Position=(8,12)
  FOOTLOCKER_001: Open
```

Illustrative IDs and positions only; these are **not** Black Mesa's existing field IDs or an adopted schema. The parser merges initial state with authorized diffs; failed or merely intended actions don't mutate state.

## Immediate proposed design task

**Begin with the consumer boundary, not a consumer-limited map.** Read ChaOS's `026_COT_SPATIAL_EMBODIMENT_PROCESSING` to establish the **current parser-to-ChaOS interface** and test its behavior with Black Mesa. However, the completed static map is intentionally free to contain **much more information than ChaOS presently consumes**. The generator's world-building ambitions and the DM's needs determine the richness of the map; the parser slices, resolves and filters it for the particular consumer. The COT informs today's adapter contract, **not the maximum schema or allowable detail of the map**. Expand the generator, parser and spatial COT independently where possible and together when required. Open questions: map data model and spatial consistency; parser selection/visibility and evidence contracts; forward compatibility; how physical/sensory detail is evaluated; DM review and publication.

## Consumer-first design dependency — ChaOS spatial COT (DM correction, 2026-10-19)

**Accepted reference hierarchy:** The actual **map consumer**, rather than the Black Mesa example, is the design reference. The authoritative existing consumer is **`CHARACTER_OPERATING_SYSTEM/026_COT_SPATIAL_EMBODIMENT_PROCESSING.txt`** from the `Mastenship/On-The-Top-Constraint-ChaOS` repository. The generator still creates the **finished static map**; Black Mesa demonstrates a basic artifact format and provides test data, but it does not establish the map interface's required features.

**Accepted co-evolution principle (refined):** The generator can **overspecify a static map**—including detailed history, materials, construction, spatial and sensory properties, and information not consumed in current play. **The parser's job is to slice the authoritative baseline (plus authorized runtime diffs) into what ChaOS needs and may access.** The spatial COT defines current **consumption behavior**, not the map's scope. As needs change, parser and ChaOS may expose richer slices of already-present data; the generator changes only where additional authoring information or different structural guarantees are useful. These components can grow side by side while retaining separate responsibilities and explicit interface boundaries.

### Character-dependent sensory slicing — DM requirement (2026-10-19)

**Accepted requirement:** A map's full, overspecified environmental description is *observer-independent*. **The parser** (not the map generator, and not ChaOS's narrative reasoning) selects what each specific character can perceive according to established sensory capabilities, restrictions, location, orientation, environmental conditions, and the current map baseline plus authorized runtime diffs.

**Examples supplied by the DM:**

- **Cybernetic eye with thermal detection:** read relevant heat/thermal contrast where the stated ability and geometry permit it, regardless of conventional visible lighting.

- **Orc with keen smell as a natural biological/racial alteration:** notice qualifying scent traces when their sources and air pathways make those traces available.

- **Elf with low-light vision:** interpret available light under a different sensitivity limit than conventional vision.

- **Drow with darkvision:** receive vision under darkness consistent with the *setting's established definition* of that ability; do not assume a universal version of darkvision.

**ChaOS source model checked:** `007_SCHEME_ALTERATIONS` provides `ALT_XX` with `ALTERATION_TYPE` (including BIOLOGICAL, CYBERNETIC, MAGICAL), `STATUS` (ACTIVE/DORMANT/INACTIVE/REMOVED), `OBJECTIVE_SYSTEM_EFFECTS`, `NEW_ABILITIES`, `VULNERABILITIES_CONSTRAINTS`, and independent `CHARACTER_AWARENESS` fields. `043_DYNAMICS_ALTERATIONS` includes **expanded sense** in enhancement-class inference. A functional sense must be grounded in the committed operational capability/state; character awareness or approval of the ability does **not** determine whether it functions. The current records use descriptive strings, **not** a standardized machine-readable sensory capability profile: converting them into precise parser rules is an interface/design task still open.

**Proposed parser operating sequence:**

1. Read the immutable static map's full environmental/structural facts, plus approved runtime diffs.

2. Read the observer's actual location/pose and *committed* sensory baseline and relevant ACTIVE/conditional alteration effects, with abilities and constraints as defined in that setting.

3. Evaluate relevant environmental pathways **by modality**: ordinary/low-light/dark vision, thermal detection, scent and airflow, audible sources and attenuation, etc. The implementation can begin qualitative and expand later.

4. Return only **character-available observations** with evidence references, uncertainty where appropriate, and no hidden causal facts that the character could not perceive. Seeing a warm shape is not automatically knowing its identity; smelling a chemical odor is not automatically knowing which inaccessible room generated it.

5. Feed that selected observation/context to ChaOS and `026_COT_SPATIAL_EMBODIMENT_PROCESSING` for character interpretation, cognitive/relational effects, and governed proposal-making.

**Invariant:** A superior sense expands what can be detected **within its actual modality and constraints**; it is not permission for omniscience or for the parser to invent missing facts. Normal vision and thermal detection can have different obstructions; scent can traverse a duct while not granting line-of-sight. Failure to detect something is not conclusive proof of absence unless the sensory conditions justify that inference.

**Integration tests to propose:** one fixed room or corridor, several observer profiles (ordinary vision, low-light, darkvision, thermal sensor, enhanced smell), varied door/vent/lighting states; verify distinct lawful perceptual slices from the **same unchanged static map**. 

**Open:** The representation/interpretation of `ALT_XX` sensory rules, default non-altered senses, the interface by which the parser reads relevant committed state, modality-specific physical approximations, and the provenance/evidence schema sent to ChaOS.

### What the existing spatial COT actually says

- **Purpose:** translate spatial position, proximity and environmental features into **embodied effects**, stress modulation, relational pressure and behavioral impulses. It prefers temporary overlays; mere proximity does not authorize durable relational valence changes.

- **Visibility:** `READ_VISIBILITY_CLASS: CHARACTER_VISIBLE`. The COT should work with information the character is entitled to experience, **not omniscient DM-only knowledge**.

- **External input:** `MAP_DATA` is an external narrative/substrate input, **not a ChaOS canonical module root**. Other inputs include scene geometry, body/alterations/relational/temporary-modifier state, relational scheme/dynamics, and narrative input.

- **Triggers:** spatial relation, proximity events, environment/geometry changes, active spatial modifiers, confinement, pursuit, exposure, concealment, crowding, cover, escape routes, approach, retreat, hiding and exploration.

- **Example outputs:** temporary `HYPERVIGILANCE` for threat proximity, `RELAXATION_OPENNESS` for open safe space, `COGNITIVE_OVERLOAD` for crowding/confinement, `ALLY_PROXIMITY_COMFORT` for nearby trusted allies. Behavioral impulses include `APPROACH`, `RETREAT`, `EXPLORE`, `CLAIM_SPACE`, `HIDE`. These are *proposals* with evidence and governance rules; the COT does **not** commit persistent state.

- **Epistemic requirements:** proposals use `PERCEPTION`, `INFERENCE`, `SPECULATION`, or `COMMITTED_FACT` and an `EVIDENCE_REF`. Spatial features remain in justification unless a spatial ID namespace is introduced; impulse target IDs follow the canonical `ENT_XX | NONE` rule.

- **Not currently specified:** a mandatory map serialization schema, full acoustic/scent simulation, numeric line-of-sight engine, geometry compiler, or canonical spatial feature ID namespace. Treat these as possible **generator/parser developments**, not existing spatial-COT obligations.

**Proposed interface flow:** `STATIC_MAP_BASELINE → MAP_PARSER(+ runtime overlay during play) → character-visible MAP_DATA/scene geometry → ChaOS COT_SPATIAL_EMBODIMENT_PROCESSING → governed cognitive proposals`. The renderer can read the baseline through a separate display path for the DM and players, respecting their respective visibility permissions. Precise placement of sensory filtering within the parser/interface remains an open architecture question.

**Proposed engineering discipline:** for each new capability (e.g., closed-door sound transmission, a ventilation route carrying scent, an obstructed escape route), record (a) what the generator must author, (b) how the parser interprets baseline + diffs and converts it to lawful observations, (c) which spatial-COT cues/outputs it should drive, and (d) a small test scene that proves the integration. Keep schema/interface versions explicit so changes don't silently break old maps or consumer expectations.

**First exercise proposed:** inventory the existing spatial COT's inputs and emitted cues to establish the **present parser-to-ChaOS contract**. Separately examine Black Mesa and the old generator for the **full authoring potential** of the static map, including information no current consumer requests. Test how the parser would slice that richer file into lawful, character-visible evidence. Do not trim future map richness merely to match the current COT. Use the gaps to guide parser adaptation and, only where appropriate, generator/COT revisions.

## Scope checkpoint — player character, not NPC; walk before we run (DM-confirmed, 2026-10-19)

**Purpose of the adjacent projects:** The original question recorded in Bridging Document 2 is *"how do I have an LLM be a player at my table?"* ChaOS is being developed for an **LLM-controlled player character**, not a DM-operated nonplayer character. The LLM player makes its character's own decisions about actions, possessions, equipment, clothing and personal style, budgeting, preferences and obligations. ChaOS supports character continuity and governed internal state; the character may choose an attempt but does not unilaterally establish whether the external world permits or fulfills it.

**Map-generator boundary (accepted and reiterated):** This project **authors and publishes a rich, static map** using layered, causal DM–LLM COT collaboration. It may *overspecify* terrain, physical construction, environmental mechanisms, fixed and movable objects, containers, contents, provenance, sensory signals, and other world details. It need not generate only information consumed by current ChaOS modules. **No in-play map generation and no continuous WorldState simulation are required from this generator.** Black Mesa is a simple example of the static product, not the specification's ceiling.

**Parser boundary (accepted and reiterated):** The **parser** consumes the map's full canonical baseline and, during play, any authorized **differences/overlay**; it slices the result into character-relevant observations and mechanically usable affordances according to position, lighting, obstacles, equipment, active Alterations, and other established capabilities. The parser does not hand over the entire map or convert hidden facts into character knowledge. A thermal eye, keen olfaction, low-light vision, and darkvision yield different perceptual slices from the same map. Runtime inventory/object/location changes are outside the generator; stable identities and initial placements in the static map are **possible enabling data**, with exact schema still open.

**Cross-project relevance, not implementation scope:**

- The ChaOS WIP Inventory Discovery notes already discuss a *torch's explicit 20-foot light radius* for an external parser and *interchangeable cybernetic eyes* as detachable items whose installed capability may affect an Alteration. These are instructive parser/ChaOS integration cases, **not requirements to finish the inventory system before the map generator**.

- Bridging Document 3 describes a **hypothetical WorldState** for the external world and a possible future ChaOS–WorldState federation. That is **not the static map generator**, nor an implemented Stage 3 runtime. Ordinary DM-mediated tabletop play illustrates a *pre-federation* under one human authority; the document distinguishes that from a demonstrated federation of two separate sovereign commit authorities.

- **Current work stays narrow:** make the generator's layered COT authoring and static output coherent and inspectable. Keep future interfaces possible but do not require final inventory, parser algorithms, WorldState, or federation machinery to complete generation.

**Practical test of this boundary (proposed):** Generate a small Black Mesa-like static space with consistent geometry, a door, an object/container, light/heat/odor sources and enough material detail for later interpretation. Freeze the map. Separately ask whether different simulated observers *could* receive lawful slices through a future parser. The test is **not** a requirement to implement the full parser now.

**Source cross-references:** [Bridging Document 2](https://github.com/Mastenship/On-The-Top-Constraint-ChaOS/blob/main/BRIDGING_DOCUMENTS/02%20Producing%20a%20Square%20A%20Method%20Demonstration.md); [Bridging Document 3](https://github.com/Mastenship/On-The-Top-Constraint-ChaOS/blob/main/BRIDGING_DOCUMENTS/03%20Federated%20Governance%20and%20the%20Multi-Disciplinary%20Cognitive%20Substrate.md); [ChaOS WIP Inventory Discovery](https://github.com/Mastenship/On-The-Top-Constraint-ChaOS/blob/main/CHARACTER_OPERATING_SYSTEM_WIP_NOTES/02_INVENTORY_DISCOVERY.md).

## Player parity across human and LLM players — confirmed principle

**Accepted requirement:** Every player character follows the same game rules irrespective of whether a person or LLM makes its decisions. Differences in senses, equipment, knowledge, abilities, actions, or outcomes must derive from established character/world facts and consistent adjudication, not a special privilege or penalty attached to the controller type.

**Static map implication:** One authoritative environment, not separate maps or more generous facts for different player types. The generator authors the shared static baseline. The parser delivers lawful character-specific perceptual evidence from that baseline and the approved runtime diffs. Equivalent sensory capabilities and conditions should produce equivalent game-relevant information regardless of whether the character is human- or LLM-controlled; legitimate Alterations may change perceptual access. The map itself remains richer than any single player's information.

**Scope:** This is a design invariant for the future parser and gameplay integration, not a requirement to build the parser, inventory, Stage 3, or WorldState before completing the static map generator. The exact parity tests and presentation interface remain open.

## Portable asset libraries, boundary regions and cultural overlays — DM clarification (2026-10-19)

**Accepted intent:** The asset library is not only an in-map compression or sensory-description dictionary. Asset definitions can be **extracted, saved separately, retrieved, and reused as starting points for later maps**. The map generator still produces a **static finished map**. The parser later slices that static map (plus authorized runtime overlay) for the observing character. The library belongs to **authoring**, not to per-character perception selection.

**Evidence in the old generator:** `COT_ASSET_LIBRARY_BUILDER` constructs `Generated_Asset_Library_Dictionary`, `Asset_ID`, `ACTIVE_ASSET_LIBRARY`, `Historical_Asset_Parent_Chains`, `Taphonomic_State`, `Historical_Context`, sensory descriptions and affordances. `FINAL_MAP_DATA` has an `Asset_Library_Dictionary`, zone-level `Asset_Reference`, square overrides and separate physical grid. `COT_INDOOR_ASSET_LIBRARY_BUILDER` starts from the outdoor library and creates/extends indoor variants with `Parent_Asset` links. **A general cross-map extraction/import repository workflow is desired, not yet explicitly implemented in these old templates.**

**Case A — connecting different terrain regions (DM example):** When authoring an intervening map between two established terrain types, relevant assets from both sides may be imported as source material. The generated boundary still needs its **own coherent terrain, elevation, substrate, drainage, climate and ecological transitions**; reusing source assets must not mean pasting incompatible tiles or assuming an abrupt seam. Consider gradients, ecotones, rivers and roads where appropriate. Proposed authoring distinction: imported **prototype/definition** versus generated **location-specific instantiation**, with provenance and adapted features.

**Case B — culturally influenced neighborhood with nonindigenous residents (DM example):** A neighborhood can reflect cultural traditions transported by migrants or descendants and situated within a different local climate, geology, materials and surrounding culture. Its origin, migration/settlement history, duration, cultural preservation, adaptation, exchange, construction materials and successive historical layers matter. **Culture is not identical to biome and cannot be deduced solely from terrain.** The old `COT_ASSET_LIBRARY_BUILDER` lists strong `Environmental_Determinism` (physical environment rather than social conditions determines culture). **Proposed revision:** replace this as a mandatory explanatory rule with a model in which terrain imposes practical constraints while migration, social organization, exchange, institutions, resources and history also shape cultural assets. This is especially important for borrowed/imported asset libraries.

**Proposed separations in asset architecture (not approved schema):** (1) stable reusable source asset / lineage and version; (2) local adaptation or variant reflecting environment and culture; (3) actual placement and initial condition in one static map. Reuse should not carry the source map's coordinate, locally contingent damage, or unique historical claim into another world without explicit authoring justification; likewise a reused architectural style does not imply its original population founded this new site. Existing parent-chain and indoor variant conventions are a starting point.

**Concrete workflow issue in the old draft:** The outdoor `COT_ASSET_LIBRARY_BUILDER` requests `Biome_Data` from `GENERATED_BIOME` **before** the `COT_BIOME_GENERATOR` appears in the merged file. Resolve this dependency during rebuild (change order, split early/late asset phases, or clarify optional inputs). Not a settled solution.

**Scope / status:** Portable library intent and the two use cases are **DM accepted**. Source/instance separation, provenance/version policy, boundary interpolation mechanics, culture-adaptation model and dependency repair are **proposals to design**, not decisions already implemented. Do not confuse library retrieval with dynamic map generation during play.

## Design checkpoint — indoor COT rebuild, DM-viewable maps, and environmental evidence (discussion, 2026-10-20)

**Status convention for this checkpoint:** "DM accepted" denotes explicit intent or a confirmed existing workflow, "Proposed" denotes a working assistant decomposition, and "Open" denotes a decision or implementation not yet made. This checkpoint adds to the preceding notebook; it does not replace the original COTs or declare a finalized schema.

### 1. The authoring workflow is a layered assembly line — DM accepted

**Correction to earlier assistant interpretation:** The Map Generator does **not** require a formal approval gate *before* every scratchpad write. Historically, each COT executes using the current scratchpad, **writes its result to the appropriate scratchpad section**, and provides the human DM a copy of what it added or changed. The DM can inspect, revise, discuss and correct entries on the fly. The next COT works from the adjusted scratchpad. The existing \`SYSTEM_UPDATE_DIRECTIVES\` are therefore meaningful; do not replace this workflow with ChaOS's proposal/commit machinery merely by analogy.

**Final synthesis happens after all required COT layers are populated:** The LLM reads the accumulated, corrected scratchpad and produces the *final map*. Each COT contributes a particular conceptual/physical layer, not a separately completed map. The DM described this as a house-building or assembly-line process: purpose and planning inform foundations, walls, roof, building systems, room use, contents and finishing. The completed scratchpad is the cumulative record of design decisions and the input to final map assembly. A **provisional visual rendering during drafting** may be useful but is not a separate canonical or compulsory approval transaction.

**Dependencies matter more than slavish order:** A preliminary room/adjacency requirement may be needed before the load-bearing shell, even if fine-grained room and corridor geometry is generated later. Later DM changes may affect dependent entries (moving a wall may change doors, pipes, furniture or light), so revised dependencies should be re-examined without imposing a heavy cyclic verifier architecture.

**Scope:** Authored static baseline before gameplay, not on-the-fly map invention. Runtime diffs and character-specific knowledge/perception remain the future parser/runtime's responsibility.

### 2. Retain the generator's own LLM formatting language — DM accepted

The original source at [SOURCE/merged_output.txt](https://github.com/Mastenship/Map-Generator/blob/main/SOURCE/merged_output.txt) contains \`LLM_FORMATTING_GUIDELINES_TEMPLATE\` near the end. This is deliberate cross-model engineering to reduce ambiguity: explicit \`=== SECTION: ... ===\` headers, \`=== SECTION_BREAK ===\`, \`[KEY_TERM: Document Complete]\`, \`[[LLM_INSTRUCTION]]:\`, \`[KEEP: ...]\`, \`((SYSTEM_REF: ...))\`, labeled-field matrices, lists with \`- \`, no pipe tables, no competing standard Markdown emphasis, and strict blank-line/marker isolation.

**Decision:** New COTs and scratchpad sections should follow **those existing conventions**. Earlier assistant YAML examples were illustrations, **not** a request to make YAML, JSON or Python the COT's native output language. The documentation notebook itself remains ordinary Markdown; the formatting contract applies to operational generator content.

**Related OTTC insight, not a governance import:** [Dual Readership](https://github.com/Mastenship/On-The-Top-Constraint-ChaOS/blob/main/OTTC/05_OTTC_DSL_DUAL_READERSHIP_PRINCIPLE.txt) articulates structural distinctness for both human auditors and LLM attention. The Map Generator is **DM-stepped content authoring**, not an autonomously cycling player-character system. It does not currently need ChaOS-style local constitutional repetition, proposal registries, repeated governance verification or a special commit writer. Ordinary consistency checks and the DM's iterative review should suffice for the initial implementation. Effects of token conventions still vary by model and should not be treated as magically guaranteed.

### 3. Make the world understandable and useful to the DM — DM priority

**Key correction:** The longstanding difficulty is **not primarily what text the LLM sees**. It is turning the richly described world into a map the human DM can *see, inspect, work with, correct, and use at the table*. A complete, information-rich parser file with no intelligible human floor plan is not a satisfactory generator deliverable.

**Three distinct surfaces (proposed implementation separation):**

- **Conceptual authored facts:** historical, geological, cultural, structural, functional, sensory, environmental, social and object-related world facts, including why an element exists.

- **Precise spatial authored facts:** actual rooms, features, coordinates, footprints, boundaries, dimensions, elevations, openings, connections, orientations, conditions and identities.

- **Visual representation:** an SVG drawing, aligned overlays, glyphs/stamps and labels arranged for DM use. Rendering does not invent world facts or supersede the underlying map.

**Reusable renderer, not newly LLM-authored Python for every map (proposed):** The LLM executes conceptual COTs and outputs standardized scratchpad data. One reusable Python program (or equivalent deterministic translator/renderer) interprets the agreed spatial records and creates SVG. It may emit transparent overlays registered to common graph-paper coordinates; a DM can inspect combined architectural, furniture, environment or DM-only layers. The LLM need not generate enormous per-map raw SVG text or a fresh drawing program; script compactness alone is not the whole question, because world details will remain extensive. Tool execution and rendering API are *not yet established*.

**DM editor/interface remains open:** Inkscape is a plausible near-term way to inspect/stack SVG overlays; a dedicated map-aware interface might eventually permit selection, facts-on-click, toggling layers, hidden content and synchronized edits. Neither is mandated now. No assumption that manually altering the SVG automatically updates authoritative data.

**Stamp library (proposed):** Define reusable SVG symbols for couches, tables, chairs, chests, beds, refrigerators, hearths, doors, machinery, etc.; reference a stamp by name with actual footprint, pose, scale and location. Distinguish a **world asset definition**, a **specific physical instance**, and its **visual stamp**. A historically meaningful chest might share the same simple chest stamp as a mundane one while possessing different contents, provenance and condition. Unavailable stamps should fall back to legible labeled shapes; they must not block authoring. The stamp library complements, rather than replaces, portable cultural/environmental asset libraries.

### 4. Geometry and map representation — mostly open choices

The current hex/square Python tools are useful reusable grid-paper renderers, not the finished canonical geometry language. Edge-midpoint red dots are **visual anchors**, not mandatory routes for rivers, roads or other features. A hex-grid *overlay* does not physically restrict river direction; a generator which represents rivers exclusively as discrete edge-point sequences would impose that restriction.

**Proposed alternatives under discussion:**

- Cells/edges as primary spatial references, with precise free-form vector geometry where needed; or

- Continuous measured local coordinates (easting/northing or Cartesian) as physical truth, with switchable hex, square or no-grid overlays and optional cell indexing.
A military-style measured planar system could be useful without importing all Earth-specific UTM/MGRS machinery into fictional geography. A town's buildings and streets need not inherit the directional artifacts of a hex overlay. **No choice was ratified.**

**Indoor conventions already in the old draft:** \`1 square = 5 feet\`; walls usually run along grid boundaries; edge references distinguish connection/opening; adjacent cells should refer to the *same* physical shared wall rather than independently contradicting north/south states. As a candidate convention, wall stroke thickness can depict actual 6–12-inch construction thickness while the grid denotes nominal floor plan dimensions (avoid silently subtracting thickness from nominal room dimensions). True clearance requirements, exceptional thick walls, crawlspaces and ductwork may need explicit measured dimensions. Multiple levels can use separate 2D planes with height/elevation/vertical connectors, i.e. a dimensioned **2.5D** plan before full 3D modeling.

**Suggested small test, not yet executed:** One authored feature set rendered over hex, square, and no grid, and one compact indoor structure with a dividing wall, doorway, fixtures and furniture. Verify consistent coordinate transforms and DM-readable output rather than optimizing speculative infrastructure.

### 5. COT responsibility boundaries — 16+assembly is a proposal, not a ratified count

**Existing source:** Nine indoor COTs, with the separate \`INDOOR_FINAL_MAP_DATA\` assembly contract: Foundational Parameters, Structural Shell, Environmental Conditions, Plumbing Flows, Asset Library Builder, Room Function Generator, Corridor Logic, Major Rooms Logic, Key Feature Populator. They already contain useful architectural, historical, environmental, sensory and material frameworks. Preserve that intellectual depth while improving spatial precision and causal dependencies.

**Working candidate of 16 specialized indoor COTs followed by final map assembly:**

1. **Foundational Parameters** — purpose, requirements, cultural/historical/technological setting, scale, premises and ties to outdoor context.

2. **Site and Substrate** — geology/soil, slope, water, exposures, site constraints and previous structures.

3. **Architectural Space Program** — needed spaces, relationships, rough dimensions, circulation and separation constraints **before** detailed shell construction.

4. **Foundations and Structural Shell** — foundations, supports, structural geometry, loads, materials and dimensions.

5. **Building Envelope and Vertical Geometry** — roof, exterior closure, windows, floor/ceiling elevations, shafts and voids.

6. **Room Geometry and Partitions** — resolved room footprints, functional boundaries and interior divisions.

7. **Circulation and Access** — doors, halls, stairs, thresholds, navigable paths, access and clearances.

8. **Indoor Asset Library Builder** — reusable definitions, variants, lineage, materials and cultural context.

9. **Fixed Installations** — integrated hearths, machinery, built-ins and other permanent fixtures.

10. **Utilities and Physical Flow Networks** — drainage, supply, venting, power, exhaust and setting-specific infrastructure.

11. **Materials, Surfaces and Taphonomy** — finishes, wear, repair, damage, contamination and the effects of time.

12. **Movable Furnishings and Item Contents** — placed portable objects, tools, furniture, containers, contents and specific instances.

13. **Ecology and Biological Traces** — plants, vermin, mold, nests, organic residues and environmental biology as authored baseline.

14. **Security, Concealment, Hazards and Interactions** — locks, traps, hidden passages, protective measures, triggers and mechanical affordances.

15. **Environmental Sources and Operating Conditions** — light, heat, sound, odors, vibration, radiation, emissions, magic and source activation assumptions.

16. **Environmental Field Synthesis** — integrate sources, materials, barriers, structure and air paths to describe ambient or spatially varying conditions.

17. **Final Map Assembly (not one of the 16 authoring COTs)** — synthesize the corrected scratchpad into an authoritative static map package and DM-readable renderable spatial representation.

**Status: Proposed.** This inventory is a decomposition for discussing *number, order and ownership*, not authorization to rewrite all stages. The operating dependencies require review (e.g., preliminarily anticipate chimneys/services and room needs before freezing relevant structural choices). Some stages may be merged, split, or rearranged based on practical tests. The early implementation target remains Foundation/Planning + Structural Shell, with a small genuinely visible map, rather than an entire theoretical stack.

### 6. Rich world truth first, character perception later — DM accepted

The Map Generator can author **more physical, environmental, historical and sensory truth than current ChaOS consumes**. The adjacent ChaOS \`COT_SPATIAL_EMBODIMENT_PROCESSING\` is an important *current consumer*, not the ontology ceiling for the world. The later parser takes the static baseline plus permitted runtime changes and exposes bounded character-relevant slices for human and LLM players under the same rules.

**Examples:** A werewolf-like change may provide enhanced smell; interchangeable cybernetic eye units may enable thermal imaging; a torch's defined light radius must be distinguishable from actually seeing through walls, and from whether the torch is currently lit. Ambient temperature, thermal emissions, wall material, airflow, scent sources, geometry, occlusion and knowledge are independent aspects of the authored world. A thermal eye does not simply reveal omniscient internal room contents.

**Conceptual distinction to test (proposed):** A forge is a physical object/installation; its active fire, smoke, heat, light and noise are *sources*; the resulting gradients/fields depend on materials, geometry, circulation and operating conditions. Author source mechanisms separately from the propagated ambient environment when feasible. This can support new sensory modalities without defining a separate map for every ability. No demand to model exhaustive fluid dynamics, optics or acoustics from day one. Unspecified properties should remain genuinely unspecified rather than being fabricated by the parser.

**ChaOS-related sources:** [Spatial Embodiment COT](https://github.com/Mastenship/On-The-Top-Constraint-ChaOS/blob/main/CHARACTER_OPERATING_SYSTEM/026_COT_SPATIAL_EMBODIMENT_PROCESSING.txt), [Alterations Scheme](https://github.com/Mastenship/On-The-Top-Constraint-ChaOS/blob/main/CHARACTER_OPERATING_SYSTEM/007_SCHEME_ALTERATIONS.txt), and [Inventory Discovery](https://github.com/Mastenship/On-The-Top-Constraint-ChaOS/blob/main/CHARACTER_OPERATING_SYSTEM_WIP_NOTES/02_INVENTORY_DISCOVERY.md). No requirement to modify ChaOS or finish its Inventory WIP first.

### 7. Black Mesa, everyday habitation, and emergent environmental storytelling — DM correction

**Reference saved:** [REFERENCE_MAPS/Black_Mesa_Facility.txt](https://github.com/Mastenship/Map-Generator/blob/main/REFERENCE_MAPS/Black_Mesa_Facility.txt). The original example was added unchanged as a **very simple baseline/benchmark**, emphatically **not** the intended complexity or sophistication of the rebuilt maps. It was produced by the *old generator walking through its COTs*, not by a specially programmed plot/storytelling engine.

**Observations grounded in that file:** the facility has a failing reactor hum and distressed metal; main entrance with scratched, warped door, failed seal, overturned gurney, ruptured gas mask and smashed medical kit; corridor with military-clad body, half-finished checklist, and a welded laboratory bulkhead; living quarters with open novel, interrupted card game and face-down family photograph; laboratory with dead scientist, ruined containment and suspicious biological traces; Hot Lab with ruptured unit and a chittering noise. These together *suggest* a containment catastrophe and emergency sealing which imprisoned people; the DM recognized that emerging story in the physical details. The concise map does not itself spell out every event, killer or causal link as a confirmed fact. Its significance lies in the **LLM's ability to generate consistent traces and human-scale evidence while executing the conceptual COTs**.

**DM's stronger point:** Not every place needs a disaster, mystery or dramatic plot. An ordinary occupied house still reflects the occupants' routines, habits, tastes, personal objects, priorities, sentimental attachments and ongoing lives. Black Mesa is moving partly because it contains *ordinary lives interrupted*: books, playing cards, family photos, desk items, coffee mug, telephone receiver. Items need not have elaborate magical/game mechanical properties to matter to people.

**Design consequence:** Do not make a dramatic-story COT mandatory or script plot beats into every map. Instead let functional planning, cultural/material context, inhabitants' ordinary use of space, object placement, history, taphonomy and current conditions causally interact. If a significant event is appropriate, let it leave physically coherent evidence. A site may have (1) intended construction and original use, (2) accumulated personal and material history, and (3) conditions still active at the authored starting moment. These dimensions should affect existing COTs, not require a forced thriller.

**Open idea:** Whether to give site-history/event causality its own COT or distribute that reasoning across Foundational Parameters, use-of-space, asset, taphonomy and feature stages. The latter may better preserve emergent storytelling; decide by testing rather than architectural preference. Preserve that physical evidence, full underlying history and the meaning a character infers from clues are **not synonymous**. The parser should not automatically disclose secret causes or a person's sentimental relationship to an item merely because they are in the authoritative map.

### 8. Immediate development and unresolved decisions

**Working next step:** Draft/review the revised \`COT_INDOOR_FOUNDATIONAL_PARAMETERS\` and the early architectural/structural dependencies using the existing formatting guidelines and scientific foundations. Establish a drawable **small real test map** before expanding the whole catalog. Keep the current nine originals available as references and do not revise the immutable source archive in place.

**Still open:** final number/order of indoor COTs; optional standalone versus inherited outdoor context inputs; physical coordinate convention and precise schema; shared wall identities and opening references; previsualization frequency; SVG renderer/translator implementation; stamps and label aesthetics; 2.5D level linking; persistence/reuse/versioning of asset definitions; how history and occupant significance are represented without compulsorily making a narrative; rules for sources versus environmental fields; and exact future parser contracts. Each should be resolved against practical DM use, not a prematurely comprehensive governance or full 3D application.

## COT pass-through revision — working draft (2026-10-21)

**Working draft, not approved final architecture:** [Revised COT Pass-through](https://github.com/Mastenship/Map-Generator/blob/main/DESIGN_NOTES/REVISED_COT_PASSTHROUGH_WORKING_DRAFT.txt). This new file is written in the original generator's marker/field conventions and leaves `SOURCE/merged_output.txt` intact. It audits the real historical stage inputs, output destinations and scratchpad updates.

**Corrections now recorded:** fix outdoor Biome→Asset Library dependency and malformed infrastructure header; make indoor purpose/site/inhabitants/history/space requirements precede exact structural geometry; move exact rooms and circulation ahead of utilities and object placements; compute environmental sources then fields after their causal features are established; and assemble the completed static map from one consistent, DM-corrected scratchpad. Explicitly preserve immediate scratchpad writes, post-write DM review, and the human-readable map requirement.

**Sequence proposed for testing:** 17 indoor authoring COTs plus final assembly, revising the earlier unratified 16+assembly sketch by making `HABITATION_AND_HISTORY` an early distinct contributor. The extra stage is intended to preserve ordinary life, inhabitants' routines and causal evidence without forcing tragedy or a scripted plot. Stage count, names, granularity, coordinate format and final scratchpad schema remain open. The draft defines responsibilities and pass-through, **not** the complete rebuilt COT bodies.

**Immediate test:** author a small standalone building with early foundational/planning/geometry stages, then draw it with the existing square-grid/SVG tools before pursuing a full suite. Preserve Black Mesa as the simple benchmark of emergent traces of interrupted lives, not as the map complexity ceiling.

## Scientific foundations of each COT — working companion (2026-10-21)

**New proposal:** [COT Scientific Foundations Working Draft](https://github.com/Mastenship/Map-Generator/blob/main/DESIGN_NOTES/COT_SCIENTIFIC_FOUNDATIONS_WORKING_DRAFT.txt). This separate operational-format file covers all **nine existing outdoor authoring COTs**, the **17 currently proposed indoor authoring COTs**, and **final map assembly**. For every stage it names relevant sciences/interpretive methods, concrete causal questions to resolve from prior scratchpad state, and the facts that should persist. It retains the source template's substantive models where appropriate but explicitly revises unconditional environmental determinism, misapplied indoor central-place theory, blindly imported modern width or drainage standards, forced point-to-point waterways, and formulaic mandatory plot/trap distribution.

**Method:** Domain depth should come from *applying mechanisms to the actual world*, not merely listing scientific labels or generating decorative details. The COTs remain DM-directed: write to scratchpad, present changes, accept DM corrections after write, and move forward. The scratchpad relieves re-creation but is not an infinite context window; later COTs need the pertinent records. Physical science, engineering, archaeology, anthropology, spatial analysis, and creative tabletop design are distinguishable knowledge sources rather than universally interchangeable empirical laws.

**Status:** This is a working scientific-foundation companion, not approval of every discipline, numeric rule, stage allocation or 17-COT count. The historical source and current pass-through draft remain intact.

## Outdoor COT pass-through — expanded working sequence and grid choice (2026-10-21)

**New companion proposal:** [Outdoor COT Pass-through Working Draft](https://github.com/Mastenship/Map-Generator/blob/main/DESIGN_NOTES/OUTDOOR_COT_PASSTHROUGH_WORKING_DRAFT.txt). This extends the original nine outdoor authoring stages to a **provisional sixteen authoring COTs plus final assembly**, with each stage's principal scientific disciplines, causal questions, scratchpad inputs/outputs and ownership boundaries. The old source remains unchanged. The proposed progression is scope/reference frame; inherited or newly established physics; geology; topography; climate; hydrology; soils; ecology; natural resources/hazards; human history and land use; asset library; settlement; infrastructure; landmarks; landscape taphonomy; present environmental conditions; final synthesis. Stage count and exact assignments remain open for DM review.

**Coordinate recommendation, not a decision:** Favor one shared, measured geographic reference for actual feature geometry (points, free-form lines/curves, polygons, elevation fields and explicit parent-child transforms). Derive the existing flat-top hex map and a measured/military-style square-grid view as **optional visual/indexing overlays** of those same facts. This avoids forcing roads, coastlines and rivers to follow hex-edge centers. Real UTM/MGRS is Earth-specific; a fictional world may adopt east/north measured coordinates without claiming its actual geodetic zones. The DM has not yet chosen canonical geometry, world projection, grid size or map resolution.

**Practical test:** Generate a small coherent watershed with a ridge, stream, ecological transition, farm or settlement, travel routes and normal evidence of land use. Render the identical geometry through hex, measured-square and gridless views; attach one local/indoor submap. Judge spatial continuity, scientific causality, parser potential and DM readability before ratifying grid architecture.

**Standing collaboration rule:** Each COT reads the relevant current scratchpad, writes its complete output immediately, sends the DM an update to inspect or correct, and later stages use that corrected state. The scratchpad prevents loss of prior authored layers but does not give the active LLM infinite context. No ChaOS-style mutation governance is imported into the authoring workflow.

## Scale-sensitive outdoor generation and inheritance through per-map asset libraries — DM clarification (2026-10-21)

**Problem:** A country and a county or river valley use many of the same scientific disciplines, but at very different geographic extents and levels of spatial detail. The model must also retain facts already authored at the larger scale when the DM selects a smaller region. Coarse map detail cannot simply be regenerated independently at each zoom. These are *authoring-time* maps created before gameplay, not dynamic maps created by ChaOS.

**DM accepted — each map has its own asset library:** When the country map is completed, preserve the country's map **and its asset library**. When generating one river valley within it, retrieve relevant country asset definitions, environmental/geological/historical context and the established spatial facts for the selected valley. The new valley scratchpad draws on those inherited sources during all applicable COTs; once finished, the valley has **its own asset library**, containing inherited references, refined or adapted definitions and newly authored assets. The same pattern applies to a settlement, neighborhood, street, site or indoor map. An asset library is not merely a decorative object catalog; it is reusable authored context that can support future maps. The completed map must also preserve the actual positions, connections and identities of placed features—asset definitions by themselves are not a substitute for the map's geography.

**Example — country to river valley:** The country may establish a northern mountain range, a named river flowing through a watershed, two settlements and a principal river crossing. The valley pass uses those specific facts rather than making another river or new towns. Local geology/terrain resolves slopes and terraces; hydrology refines the established river, adding meanders, springs and previously unspecified minor tributaries; ecology develops riparian corridors; human geography develops farms, tracks and smaller land-use parcels. New local details enrich the country without contradicting it. Actual contradictions are discussed with the DM rather than silently overwriting a parent map. The finished valley and its asset library become further source material for finer maps.

**Accepted reasoning principle — scale matters:** Each outdoor COT should know geographic extent, generation resolution, DM purpose, and what spatial/historical facts already exist in the source map(s). A country-level geology COT may need tectonic belts and large basins; a valley-level geology pass examines rock exposures and local formations. A country hydrology pass establishes drainage basins and principal waterways; a valley pass develops tributaries, floodplains and banks. Not drawing a minor creek on a country map does not mean it cannot exist. Deliberately defer overly fine detail until the appropriate map is authored. This does not change the LLM's disciplinary foundations; it changes how those disciplines are applied.

**DM accepted use case — blend from multiple asset libraries:** A map joining distinct terrain regions may import both sets of assets and develop ecologically and geomorphologically plausible transitional features. Soil, moisture, geology, disturbance, land use and history determine whether forest becomes woodland and grassland gradually or through a sharp boundary. The goal is causal continuity, not averaging hex colors or pasting tiles. The same logic extends to city neighborhoods influenced by different cultures and architectural traditions: migration, trade, materials, artisans, economic differences, urban morphology and building history may produce mixed forms, locally adapted variants, reused structures or persistently distinct districts. A wall, river, railway or historical separation can make an abrupt cultural/architectural boundary more credible than seamless blending. Culture is not determined by biome, and cultural mixes are not compulsory.

**Current simplifying architecture:** Preserve each map as a reusable package consisting of its completed map facts and its own asset library, with sufficient source-map references for the next scale. No separate mandatory central World Geographic Record is required for this inheritance use case, and this is not the hypothetical runtime WorldState from the ChaOS bridging papers. The **active scratchpad** remains the local working record for whichever map is being authored and continues to be written to immediately by each COT, then inspected/corrected by the DM after the write.

**Coordinate choice still open:** A measured coordinate base with selectable hex, square or gridless overlays is the current assistant recommendation, **not** a DM-approved decision. The inherited-map requirement applies regardless of which geometric representation we choose. We still need to specify feature identity, parent/child placement, coordinates/transforms, scale/resolution and library serialization.

**Documents updated:** [Outdoor Pass-through](https://github.com/Mastenship/Map-Generator/blob/main/DESIGN_NOTES/OUTDOOR_COT_PASSTHROUGH_WORKING_DRAFT.txt) (16 provisional outdoor COTs), [Indoor Pass-through](https://github.com/Mastenship/Map-Generator/blob/main/DESIGN_NOTES/REVISED_COT_PASSTHROUGH_WORKING_DRAFT.txt) (17 provisional indoor COTs), and [Scientific Foundations](https://github.com/Mastenship/Map-Generator/blob/main/DESIGN_NOTES/COT_SCIENTIFIC_FOUNDATIONS_WORKING_DRAFT.txt) (nine original outdoor scientific sections, with a cross-scale supplement and separate sixteen-stage outdoor responsibilities). Original source and existing map/grid tools unchanged.

**Test recommendation — proposed:** Make a country segment with a river, valley, broad ecological transition, settlements and a crossing; generate a more detailed valley from its preserved asset library and spatial facts; then generate a boundary area drawing on two neighboring terrain or cultural libraries. Check source-feature identity, environmental/historical plausibility, edge continuity, locally adapted assets and DM readability before ratifying a coordinate format or stage counts.

## Indoor 2-meter square grid and physical wall thickness — DM-directed working scale (2026-10-21)

**DM clarification and working choice:** Adopt **2 meters × 2 meters per indoor grid square** for the rebuilding drafts, retaining the current **100 × 100 SVG pixels per square** and the existing center, edge-midpoint and lower-offset dots. The actual square-grid Python script uses 100-pixel cells in the current 20 × 20 generated example. The resulting drawing ratio is **50 pixels per meter** before any rescaling. This supersedes the historical generator's five-foot indoor square as the new working authoring scale; preserve the original file unchanged.

**Reason for the change:** The primary motivation is **room to represent a wall's physical thickness**, not just a larger character-movement cell or a different display scale. The map must construct buildings with walls as spatial solids, not zero-width lines separating nominal squares. A wall's material, construction, length, thickness, height, location, inside/outside faces and actual occupied footprint should be available to the structural shell and downstream COTs. Different wall types require different thicknesses; the grid does not make all walls two meters thick. For illustrative true-scale rendering, 0.10 m = 5 SVG pixels, 0.30 m = 15 pixels and 0.50 m = 25 pixels. These are illustrations, not universal structural standards.

**Geometry and stage implications:** The foundational-parameters COT records the new indoor scale; the structural-shell COT owns canonical bearing-wall geometry, thickness and IDs; room-geometry COT positions partitions and derives **clear usable room dimensions from real wall faces**, distinct from gross footprints; access/circulation COT creates door/window apertures *through* the existing wall, including opening width, depth and clearances. The final assembly renders actual wall polygons consistently, rather than drawing thick walls only as an artistic effect. Adjacent rooms must refer to the same shared physical wall.

**Dots and sub-cell features:** Keep the existing square center, shared edge-midpoint and lower markers as references useful for positioning, but **do not force walls, openings, furniture or utilities exclusively onto the dots**. Measurable dimensions and coordinates within a square are necessary, and the physical world retains finer detail than the default renderer can necessarily display. Larger grid cells do not by themselves confer finer physical precision. Marker display could later be configurable without removing them from the spatial reference.

**Indoor/outdoor consistency:** The DM prefers one common square-grid architecture over parallel live hex and square coordinate systems. Outdoors the same 100-pixel square drawing pattern can represent a much larger real distance. Switching the indoor working grid to 2 m makes a consistent metric convention attractive, but the **final outdoor units, coordinate origin, projection and scale choices remain open** rather than silently decided. Actual Earth UTM/MGRS should not be assumed to cover a fictional world unchanged.

**Status and source protection:** 2 m per indoor square is the current DM-directed working design for COT drafting and prototype tests, not a completed renderer or a fully approved global coordinate standard. Preserve GRID_TOOLS/SQUARE and the HEX reference, original merged COT source, Black Mesa reference, and historical artifacts. No new rendering code was requested. Updated working companions: [Indoor Pass-through](https://github.com/Mastenship/Map-Generator/blob/main/DESIGN_NOTES/REVISED_COT_PASSTHROUGH_WORKING_DRAFT.txt), [Scientific Foundations](https://github.com/Mastenship/Map-Generator/blob/main/DESIGN_NOTES/COT_SCIENTIFIC_FOUNDATIONS_WORKING_DRAFT.txt), and [Outdoor Pass-through](https://github.com/Mastenship/Map-Generator/blob/main/DESIGN_NOTES/OUTDOOR_COT_PASSTHROUGH_WORKING_DRAFT.txt).

## Square-grid easting/northing naming and Python correction — working convention (2026-10-21)

**DM decision and reason:** The existing 20×20 square grid has the correct eastward X direction, but originally numbered Y **down** the drawing; military-style location references must read **right, then up**. The DM agrees to correct the Python grid rather than replacing the existing geometry. North should be up, east to the right, while retaining the 100-pixel squares and the original center, lower-interior and shared-edge midpoint dots.

**Recorded method:** [Square-Grid Coordinates and Map Reading — Working Reference](https://github.com/Mastenship/Map-Generator/blob/main/DESIGN_NOTES/GRID_COORDINATES_AND_MAP_READING_WORKING_REFERENCE.md) is a separate human/LLM reference booklet. Its basic square address is **`CELL(E,N)`**, displayed compactly as **`(E,N)`**: first number E increases east/right, second number N increases north/up. The standard 20×20 sheet beginning at southwest cell `CELL(0,0)` has southwest (0,0), southeast (19,0), northwest (0,19) and northeast (19,19). This is **square-cell indexing**, not an official MGRS reference and not itself a meter-valued geographic point. Precise measured positions use a separate easting/northing pair in a named frame; the SVG uses x right and y **down** and therefore inverts northing during rendering.

**Source changes:** [Square-grid Python script](https://github.com/Mastenship/Map-Generator/blob/main/GRID_TOOLS/SQUARE/Square_Grid_With_Edge_Midpoints.py) now reverses the displayed row index and adds optional `grid_origin_e`, `grid_origin_n` parameters denoting the **southwest cell indices**. A second 20-column sheet placed directly east can start at `(20,0)` rather than restarting at (0,0); a sheet directly north begins at (0,20), at the same cell scale and reference frame. Its default cell size is now 100 SVG pixels to match the existing output. The [square SVG](https://github.com/Mastenship/Map-Generator/blob/main/GRID_TOOLS/SQUARE/Square_Grid_With_Edge_Midpoints.svg) has been regenerated with north-up labels and unchanged 20×20 grid, 400 cell centers, 400 lower markers and 840 unique red shared-edge markers. The historical hex generator remains untouched.

**Important distinctions:** `CELL(E,N)` selects an *area*, an edge-dot reference such as `CELL(3,4):EDGE_E` identifies an authoring anchor shared with the adjacent square, and a precisely located feature requires a measured coordinate in the named map reference frame. The same numeric cell address at different scales does **not** identify the same physical location; the source map's identity, scale and spatial reference are mandatory context for a zoom. Stamps and graphic anchors are not a substitute for actual terrain lines, wall solids, room clear dimensions or coordinate-bearing feature geometry. The 2-meter indoor working cell still renders as 100 pixels; an outdoor cell will have its own declared larger physical scale.

**Implementation status:** The Python indexing and generated SVG are corrected, while exact fictional-world reference frame, outdoor grid-unit/scale presets, finalized field serialization, renderer integration and full MGRS compliance remain *open*. This is an MGRS/UTM-inspired square-grid naming convention, **not an implementation of Earth's full MGRS zone and 100-kilometer lettering standard**. The reference document contains the formulas, adjoining-sheet examples, edge aliases, DM reading rules, LLM reading rules and remaining questions. The indoor and outdoor pass-through drafts now point to it.

## Reference materials

- Archived reference **[REFERENCE_MAPS/Black_Mesa_Facility.txt](https://github.com/Mastenship/Map-Generator/blob/main/REFERENCE_MAPS/Black_Mesa_Facility.txt)** (source: user-provided `Black_Mesa_Facility(1).txt`, preserved byte-for-byte): deliberately simple historical baseline for room connectivity, sensory detail, occupants' personal traces, and emergent evidence of a containment disaster; not a target complexity level. Room-local coordinates and overall geometry still need formalization.

- Uploaded **merged_output.txt**: previous world-generator COTs (physical foundations, terrain, climate, hydrology, biomes, assets, settlements, transport, landmarks, indoor structures); reference for ideas, not an architecture we must preserve.

- Existing GitHub **Mastenship/On-The-Top-Constraint-ChaOS**: has ChaOS WIP notes, but no dedicated map-generator notes area; keep the new effort distinct.

## Open design questions

- Minimum canonical world/geometry schema?

- How granular is DM approval and how do revisions propagate?

- How should historical causal relationships be stored?

- Exact conventions for shared walls, openings, thickness, levels and transforms?

- Where do automatic spatial calculations end and DM adjudication begin?

- How is genuinely unknown environmental detail represented?

- What is the minimum useful DM editor/viewer?

- How should project notes be versioned when design stabilizes?

## Notes discipline

New entries should distinguish **Problem / Candidate / Consequences / Decision status**. Use **Open**, **Proposed**, **DM Accepted**, and **Rejected**; do not misclassify assistant suggestions as settled choices.