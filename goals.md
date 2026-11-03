# Goals

The long arc: **plant-forms first, ornament-forms after.** The plant-form is the
first complete ornament: one full line, two rails, an ending, growth marks and
branches. The grammar is the deliverable, not one drawing.

## Plant-forms

Build a plant-form in this order. Each step must be visible in the proof page;
none may be skipped by drawing a pretty outline over a missing rule.

1. **Take a stalk.** One stem curve from the catalogue (a LAC, PH, Euler or
   recovered spine). The stalk is the centreline; it is not the outline.
2. **Make the two-sided offsets.** Use the exact/numeric offset route; the two
   rails stand off the stalk. Separate neighbouring curves by **2 × offset plus
   a little breathing room** so no two offsets touch or cross. A width is not a
   style: the offset distance is a declared number and the same number is used
   by the ending and the branches.
3. **Give it an ending.** Every stalk ends in one of:
   - a **flower** from the flower grammar (cardioid, trifolium, quadrifolium,
     astroid at present);
   - a **seagrass / leaf ending**;
   - if there is no flower or head, a **simple cone terminal**: two arcs of
     **radius 2 × the offset**, one from each rail, meeting in the middle at the
     centreline tip. Tangent to the rail at the base, pointed at the middle —
     a cone, not a blunt cap. **No bare tip.**
4. **Mark the integer-lattice hits.** Draw the points where the stalk centreline
   crosses the **integer lattice** in model space. Map those hits to the page;
   do not snap the stalk to the page grid.
5. **Add the growth mark.** At a lattice hit, put a small **pyramid on each side
   of the parallel curves** — a simple vine thorn. The base sits on the offset
   rail; the apex points outward. It is a mark, not a new curve family: small,
   local, and only at the lattice hits.
6. **Branch at some growth points.** At selected hits, branch off with smaller
   curves. Lower branches are **bigger than upper branches**; the scale falls
   with height. A branch inherits the offset, ending and terminal rules; it may
   carry its own lattice marks.
7. **Prove the form.** A plant-form page/print showing the stalk, both rails,
   the chosen ending, the lattice hits, the growth marks and at least one
   branch — with the offset distance and terminal radius written on it.

## Geometry rules

- **mm internally; +y up.** Flip at SVG/page output and say where.
- The **integer lattice** is in model space. The page grid is a ruler, not the
  lattice.
- Offset separation is **2 × offset + breathing room**; a catalogue of offsets
  is a set of non-touching curves, not a pile.
- The **cone terminal radius is 2 × offset**. The two arcs are tangent to the
  rails at their bases and meet at the centreline tip. The construction must
  state where the arc centres sit; the goal is a cone, not an approximate
  rounding.
- **Growth marks only at integer-lattice hits.** One pyramid on each rail at a
  hit; no marks between hits.
- **Lower branches bigger than upper branches.** The exact scale law is open;
  the monotonic rule is not.
- **No bare tip:** flower, seagrass, or cone terminal.
- Exactness follows the offset tier: PH/rational offsets may be exact; sampled
  curves are fitted. Do not claim exactness without a rail and its error.

## Ornament-forms

After the plant-form grammar is proved, apply the same construction — full line,
two rails, endings, lattice growth marks, branches — to ornament that is not
botanical: scrolls, volutes, fleur/cruciform, the recovered plates, the primal
studies, and the archetypal ornaments. The plant-form is the first ornament; it
is not a separate art project.

## Order of work

1. **Offset catalogue.** `workbench/stem-library-offset.html`, OffS1…: the
   formulaic offsets first, then the LACs via `design_from_spans` →
   `build_rail`; two-sided offsets; every pair separated by 2 × offset plus
   breathing room. Add multiple stems only after the base is settled.
2. **Cone terminal.** Add the two-arc, radius-2×offset cap to the terminal
   layer (`curve_lab/terminals.py` or a plant terminal module), with a proof of
   tangency and a test that rejects a bare tip.
3. **Growth-mark grammar.** Lattice-hit detection, the pyramid pair, and the
   rule that marks only sit at hits.
4. **Branch grammar.** Select hits, scale the branch down with height, and give
   the branch its own ending/terminal.
5. **Plant-form proof.** One complete stalk → offsets → ending → lattice marks →
   branch, then a small orchard of variants.
6. **Ornament-forms.** Reuse the grammar on the ornament families.

## Existing pieces

- `scripts/stem_library.py` and `workbench/stem-library.html` — the stalk
  catalogue (S and SM cards).
- `curve_lab/offsets.py` — `build_rail`, `cusp_ranges`, the offset machinery.
- `curve_lab/terminals.py` — `butt`, `point`, `arc`, `round`, `taper`; the new
  cone terminal belongs here unless it needs a plant-specific module.
- `curve_lab/piece.py`, `curve_lab/clearance.py` — `Piece`, `Trace`,
  `piece_clearance()`.
- `workbench/flowers.html`, `scripts/stems_print.py` — the flowers sheet and
  the stem/ending placement.
- `docs/FLOWERS-int.md`, `docs/PHILOSOPHY.md`, `docs/CLEARANCE.md`,
  `docs/JUNCTION.md` — the durable prose.

## Source intake

The ornaments pages are the source material. They are not all parallel-offset
sources: a rail is not a parallel offset unless the two rails are equidistant.
The source pages live at `http://localhost:8001/` while `../ornaments` is
served; the readers are `scripts/extract-spirals.py` and
`scripts/extract-terminals.py`.

| source | plates | spines / outlines | state |
|---|---|---|---|
| `LAC-log-asth-curve.html` | 31 | 31 spines / 31 outlines | **Wired.** `workbench/spirals/lac.json`, `workbench/terminals/lac.json`; LAC spines are S35–S65. The rails/terminals are not yet in the offset page. |
| `stage-two.html` | 20 | 20 spines / 20 outlines | **Wired** to `stage-two.json` (spirals and terminals). Not yet in the stem catalogue or the offset page. |
| `stage-three.html` | 4 | 4 straight spines / 4 serif outlines | **Not wired.** The spine is a straight `data-line` path, so the cubic-spine reader returns 0; the four outlines are serif/terminal studies and belong in the terminal intake. |
| `stage-four.html` | 10 | 16 spines / 0 outlines | **Not wired.** The reader can see the 16 cubics but tags them unknown. It is a **width-modulation** study: the page explicitly says the rails are not equidistant, so it is **not** a parallel-offset source. |
| `lattice-curves.html`, `curve-sandbox.html`, `etc.` | ? | ? | **Not inventoried.** Inspect before adding; classify spine / rail / terminal / integer first. |
| `generators.html` + `scripts/generators.py` | 4 presets + 25 named | integer PH / exact curves | The integer curves are in the stem library; their **offset rails** are missing. |
| `pythagorean-spiral/` | exact spine | integer 3-4-5 lattice | Exact integer source; offset/terminal not built. |
| `workbench/stem-library.html` SM23–SM26 | 4 | integer **p spacing** | Not integer curve solutions; these are integer sequences for the p knob. |
| `ornaments` 3125 lattice | all plates | integer **coordinates** | The coordinates are on the 3125 lattice; that is not the same as an integer solution to a curve. |

**Rule.** Before adding a source, record: spine or rail; exact or fitted; the
offset tier; the integer status; the plate count; and where the result lands.
Do not call a page an offset source because it draws a width.

## Bring up to speed

A curve is **up to speed** when it has: (1) two-sided offsets, exact or fitted
with the error stated; (2) a clearance check at **2 × offset plus breathing
room**; (3) an integer/exact status, or an explicit “fitted, not exact” mark;
(4) a page/card and an ending or terminal; (5) a test or recheck.

The named example — **the parallel parabola** — is a useful boundary. The
evolute page shows the parabola’s **evolute** (the semicubical parabola) and the
normal offsets, but it does not yet show a **parallel-parabola** card or a rail
catalogue. The offset of a parabola is algebraic but not rational (the parabola
is not PH), so this is a fitted rail, not an exact one.

| item | offset / parallel | integer / exact | where it is now | what is missing |
|---|---|---|---|---|
| **Parallel parabola** | fitted; algebraic, not rational | integer points on the parabola, not on its parallel | `lac-parallel.html` (evolute + normal offsets) | a parallel-parabola card/rail, 2× clearance, and a stated fit error |
| **Parallel ellipse** | fitted | rational points on the ellipse; not an integer parallel | `lac-parallel.html` (astroid evolute) | parallel-ellipse card/rails |
| **Parallel hyperbola** | fitted | rational points; not an integer parallel | none | the whole family |
| **Parallel semicubical / Neile** | fitted; cusp | algebraic; cusp | `lac-parallel.html` | offset card and cusp/fold handling |
| **Parallel cycloid** | fitted | transcendental | `lac-parallel.html`; stem S69 | offset catalogue and clearance |
| **Parallel astroid / hypocycloid** | fitted; cusps/folds | algebraic | `lac-parallel.html`; S17 | offset catalogue with fold ranges |
| **Parallel catenary / tractrix** | fitted | transcendental | `catenary.html`; S66 | tractrix and offset catalogue |
| **Parallel log spiral** | exact: another log spiral | transcendental | `lac-parallel.html`; S67 | verify the exact factor; card |
| **Parallel circle involute** | exact: another circle involute (same base circle, shifted parameter) | transcendental | `lac-parallel.html`; S68 | exact test/card |
| **Parallel clothoid / Euler** | fitted: the offset is not a clothoid | transcendental | `lac-parallel.html`; S30/S31 | rail and error |
| **Parallel LAC** | fitted via `design_from_spans` → `build_rail` | not exact | S35–S65; `lac-parallel.html` | `stem-library-offset.html` |
| **Parallel PH** | exact rational | integer presets/named | `generators.html`; stem presets | exact offset rail page |
| **Parallel rational named curves** | fitted in general | some PH, some not; classify | stem library S05–S29 | classification and rails |
| **Parallel squircle / heart** | fitted numeric | non-rational | `hearts.html` | rails and error |
| **Parallel Pythagorean spiral / 3-4-5** | exact arcs/lines; verify joins | exact integer lattice | `pythagorean-spiral/` | rails and terminals |
| **Cone terminal** | R = 2 × offset | — | `curve_lab/terminals.py` | construction and test |
| **Growth marks / branches** | from the rails | lattice hits | `goals.md` only | grammar and proof page |

**Order.** The offset catalogue is first: formulaic curves, then parallel conics
(parabola, ellipse, hyperbola), then the classical evolute families, then the
LAC/PH/integer rails, then terminals and branches. The source intake is not
finished; Stage III and IV are deliberately not claimed as wired.

## Open decisions

- The integer lattice is model-space integer; confirm whether it is the design
  box or the page frame.
- The exact cone-terminal construction: arc centres, tangency points, and
  whether the two arcs meet at a true point or a tiny tangent join.
- Growth-mark size: fixed model size, or proportional to the local offset /
  branch scale.
- Seagrass/leaf ending grammar: blade count, taper, and how it joins the rails.
- Branch selection and scale law: which lattice hits branch, and the monotonic
  lower-bigger rule as a formula.
- Which flower forms are legal endings; the flowers page currently offers four.
- Whether the offset page and the plant-form proof are one page or two.
