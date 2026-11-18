# Architecture overview

> **draft A** — a working draft, not a final text.
This project draws smooth decorative curves — scrolls, leaves, ribbons — and it
does so with two tools rather than one. They are good at different things, and
most of the design decisions follow from keeping them apart.

## The curve engine (`curve_lab`)

A train does not jerk into a bend; the track eases into it. That transition is a
clothoid, or Euler spiral, and the engine uses the same idea for ornament.

The engine's job is the *drawn* curve: it fits smooth clothoid segments, gives
them width, and checks that separate strokes do not collide. Its joins are G1 by
construction — the tangents meet exactly. Curvature is continuous (G2) only
where a terminal's width law or a blend supplies it; a plain corner or a
junction without a blend still has a curvature step, and the reports say so.

You use it through the web interface (`web/`), which edits a design, previews
it, reports on it, and downloads SVG.

## The spine layer (`pythagorean-spiral`)

Computers count in decimals, and a few hundred accumulated rotations leave a
closed loop a fraction off its start. The spine layer avoids that by choosing
its rotations from whole-number right triangles. A 3-4-5 triangle turns by an
angle whose sine and cosine are exactly 3/5 and 4/5, so rotating a point is
`(4x - 3y, 3x + 4y) / 5` — no trigonometry, no rounding. Every heading and
every node is rational, and a chain closes on an exact grid line.

What that buys, and what it costs:

- The **plan** is exact: the turn schedule, the closure, the apsis, the joints
  and the mirror are integer or rational facts.
- The **drawing** can be exact too, but only for chains small enough to afford
  the arithmetic. Past a few hundred chords the coordinates are computed in
  doubles, with a measured residual around 1e-13 — far below the page.
- A right angle is exact as a *cusp*, a component swap; it is not reachable by
  accumulated turning, which is a theorem, not a limitation of the code.

The spine layer is not a clothoid and does not replace the engine. It is a
polygon whose headings match a clothoid at the nodes; its position is up to a
chord away.

## How they are meant to connect

The intended pipeline, from exact plan to finished page:

```text
1. SKELETON        pythagorean-spiral
   exact spine from whole-number turns
   closure and endpoints on the grid
            |
            v  anchors and headings
2. INK             curve_lab
   smooth segments, width, rails, clearance
            |
            v  paths
3. PREVIEW         web/
   edit, measure, download SVG
```

**All four conditions hold under the operator's fidelity rule (2026-10-30).** The two tools now
meet at `curve_lab/spine.py`: a chain's own spans become ordinary clothoid
segments, so rails, terminals, clearance and the SVG writer need no second
geometry kind.

1. **Done.** `curve_lab` imports a chain and builds a `Piece`/`Trace` from its
   anchors; every fitted join lands on a chain anchor (worst 2e-14 units).
2. **Done.** `workbench/spine-sheet.html` draws a curl on the 200 × 250 mm sheet
   through `svg.document`.
3. **Done.** `piece_clearance()` measures the same build; a contact declared at
   a forked node passes, and the same gap fails without the declaration.
4. **Done.** One W03 study is drawn entirely from Pythagorean chains. P01's
   start heading (77.97°) and corners are not in any triangle's rotation group,
   so this is a chain plan, not P01's node table. It passes the operator's
   rule — worst span-end drift at most **1.6% of study height** — at **1.29%**
   with a 0.5° turn step. See `FIDELITY.md`; the study is **not** node parity
   (0.03 units for the port against 19.44 here).

There are now **two profiles** of a chain study: the exact one (one cubic per
chord, 1,164 cubics) for zooming and choosing, and the practical one (one
clothoid per structural run, 34 cubics at 0.42 mm) for output. A **pin** carries
a branch chosen on the exact curve into the practical curve as an exact vertex.
The remaining gap is surface, not wiring: the fill currently needs the spine
layer's exact miter, because the engine's rail builder crosses at per-chord
corners.

## Two systems, three ways in

The tool has two curve systems and three ways to enter them. The distinction
matters, because only two of the three are different geometry.

| way in | you supply | it solves | it produces |
|---|---|---|---|
| **spine** | a triangle, a turn schedule, a closure | an exact rational Euler polygon | a chain → `Piece` |
| **engine** | segments, points with tangents, or recovered spans | the clothoid through those constraints | a `Design` → `Piece` |
| **scroll** | an end radius, a join gap, a page and a clearance | the curvature rate and the length, plus the inflection or the return to radius `r` | a `Design` → `Piece` |

The spine is a *different* curve: a discrete polygon with exact rational nodes.
The engine and the scroll share one equation, `kappa(s) = kappa0 + kd*s`; the
scroll is a front end that turns a designer's numbers (circle radius, gap, page)
into that equation, instead of asking for `kappa0`, `kd` and a length or for a
list of points. It is the volute/scroll family, not a fourth kind of ink.

The practical consequence: a scroll should emit an ordinary `Design`, so it
inherits the rails, terminals, clearance, SVG writer and the practical curve's
pins. Today it lives in `scripts/spiral_turns.py`; the next step is to promote it
to `curve_lab/scroll.py` with tests, and then it is a first-class way in
rather than a page experiment.

## Where to look

| If you want | Read |
|---|---|
| Why the project exists and in what order | [The plan](PROJECT.md) |
| To use the browser tool | [Web application guide](WEB-GUIDE.md) |
| A plain-English term | [Glossary](GLOSSARY.md) |
| The words, and how the two sides' vocabularies map | [Glossary](GLOSSARY.md) |
| What is true today, and what is next | Current truth (`state/HANDOFF-int.md`) |
| The spine layer, step by step | [Spine guide](SPINE.md) |
| The curve model in detail | [Curve model](CURVE-MODEL.md) |
| The accepted accuracy budget | [Fidelity](FIDELITY.md) |
| The recovered plates and their formats | [Recovered corpus](CORPUS.md) |
| Work items, plates and decisions | Work items and the work board (`state/WORK-int.md`) |
| What passes, and how | [Verification](VERIFY.md) |
| What works today | Status (`state/STATUS-int.md`) |
| Who wrote the engine | [Credits](CREDITS.md) |
| The spine layer in depth | Spine explainer (`pythagorean-spiral/docs/EXPLAINER.md`) |
| How the folder is organised | [Documentation index](index.md) |

## Which tool for which job

| You want to | Use | Where |
|---|---|---|
| Sketch a curve and see it | web app | `web/`, and the app's own page |
| Download an SVG for Inkscape | web app | the download control |
| Close a loop that must meet exactly | spine layer | Spine explainer (`pythagorean-spiral/docs/EXPLAINER.md`) |
| Snap a flourish to an exact grid | spine layer | Spine explainer (`pythagorean-spiral/docs/EXPLAINER.md`) |
| Look up a term | — | [Glossary](GLOSSARY.md) |

## What this overview does not claim

- That the engine is G2 everywhere. It is not; see above.
- That a chain study is P01. It passes the 1.6% fidelity rule and is not node
  parity; see `FIDELITY.md`.
- That "exact" means the coordinates at any scale. It means the plan; the ink is
  measured.
