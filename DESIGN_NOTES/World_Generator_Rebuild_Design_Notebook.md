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

## Reference materials

- Uploaded **Black_Mesa_Facility(1).txt**: basic pre-created rooms, transitions, objects, sensory layers; reveals need to formalize room-local coordinates and overall geometry.

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