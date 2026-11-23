# SPEC — side pillars (`side-pillars.html`)

**Status, 2026-11-23:** spec only; nothing built. Written from the operator's words below.

**The page:** `workbench/side-pillars.html`, built by `scripts/side_pillars.py`
(the operator named the page with `.html`; a product version would port to `/side-pillars/`)
**The maths (when built):** `scripts/side_pillars.py` in Python, or `app/src/lib/side-pillars.js`
if the page moves to Astro
**The test:** `tests/test_side_pillars.py` (Python) or `tests/js/side-pillars.test.mjs` (Astro)
**The check:** `app/scripts/check-pages.mjs /side-pillars` when it has a route

## What it is

The operator, 2026-11-23:

> "instead of joining several curves as we will do along the top horizontally with glue curves,
> we will treat the sides differently … they will be thin thin pillars, with some expression to
> the pillar itself, and with bases and capitals, to focus on the pillar itself, it is thin
> because it is just a page or illustration border, not a real architectural pillar. what it
> does have is expression, just like a roman pillar. it will be slightly wider at the middle,
> and thinner at the top than the bottom; all the classical rules found on the internet but much
> thinner."

So the border has two different jobs:

- **The top (and bottom): curves joined end to end** by the glue connector (`/glue/`), because a
  horizontal run of curve work is a line of strokes that must meet.
- **The sides: a pillar, not a joined curve.** One thin pillar per side, with a base, a shaft
  and a capital. The pillar is the border; it is not load-bearing architecture.

The page exists to judge the pillar's proportion and expression, not to fix a building.

## One line, not an outline

The operator, same day, as the fallback:

> "if we have to, we will make it just one line, the outside edge of the pillar. on the right it
> will be the right line, on the left it will be the left line."

- **One line per pillar.** The pillar is drawn as a single polyline. Start with this, not with a
  closed outline: a border line is what the page needs, and one line cannot fill or fold.
- **The line is the outside silhouette.** On the right side of the page it is the right edge; on
  the left side it is the left edge. The inner edge is not drawn; the field inside the border is
  empty paper.
- **Base and capital read as steps in that one line:** the line steps out at the base, runs up
  the shaft with the swell, and steps out at the capital. No second line, no fill, no shading.
- **A closed outline is a later option, not the first one.** If the operator asks for it, it is
  the same three profiles mirrored about the axis, and the spec gets a section for it.

## The geometry, in words first

**Thin.** The pillar's foot is a small share of the page's height — 1/48 by default, about 2 %
of the height. A real Roman order is about 7 to 10 diameters tall; this one is about **48
diameters** tall, and the page prints that number so the thinness is visible rather than
asserted.

**Taper.** The top is thinner than the foot. Default: the top is 41/50 of the foot's width, so
the shaft loses 18 % of its width from foot to top.

**Entasis, the swell.** A Roman shaft is not a straight taper: it swells slightly, and the
fullest part sits about a third of the way up. The swell is measured against the straight line
from foot to top:

- at the swell station (1/3 of the height) the shaft is **wider than the straight taper line**;
- the foot is still the **widest single point** of the shaft.

Both of the operator's sentences hold at once. Making the middle the widest point of the whole
pillar would make it a barrel, which is not a Roman pillar; if the operator wants that, it is a
different figure and a different spec.

**Base and capital.** The classical parts, much reduced:

- **base:** a plinth and a torus, together 3/2 of the foot width tall;
- **shaft:** the taper with the swell;
- **capital:** an echinus and an abacus, together 2 foot widths tall; the abacus is wider than
  the shaft at that height, as it is in the classical orders.

The page prints each part's height in foot widths, so the proportion can be read without
measuring the picture.

## The numbers (defaults, all ratios)

| quantity | default | unit |
|---|---|---|
| page height H | the figure box | model units |
| foot width `d0` | H / 48 | model units |
| top width `dt` | 41/50 × `d0` | model units |
| swell station | 1/3 of H | share of height |
| swell above the taper line | 3/100 × `d0` | model units |
| base height | 3/2 × `d0` | model units |
| capital height | 2 × `d0` | model units |
| height in diameters | 48 | diameters |

- Every value is a ratio of whole numbers. A slider may set a share; the share is stored as a
  fraction and printed as a fraction, with the decimal only as a readout.
- The shaft profile is a **quadratic Bézier** from the foot station to the top station with the
  swell point as the middle station: rational control numbers, so the swell is exact.
- **No `cos` or `sin` of a general angle** (project rule). If a later version rounds the torus
  with arcs, the arcs use rational circle points (p-triples); until then the torus is the Bézier
  approximation and the page says "approximate between the stations".

## Layout

- The page carries the shell margin (`app-shell.css`); it invents no margin of its own.
- **Left half:** the figure, full width of the box. Two pillars, one at each edge, drawn with
  the one-line rule; between them, a faint dash of the top border shows where the glue-connected
  curve run meets the pillars at a plain corner.
- **Right half / foot:** the readout. Foot, top and swell widths as shares of the height; height
  in diameters; base and capital heights in foot widths; the swell measured against the taper
  line. Raw numbers at the foot of the page, not in the reading order.
- **Labels inside the figure:** a figure number and title (`Fig. P1 — the side pillar`), the x
  and y axes of the model, a key naming the line (the outside edge), and the four measured
  values printed at their stations. A reader must not need the caption to read the figure.
- The figure fills its box: the canvas aspect comes from the pillar's own height and width.

## Controls (each one must change a measured number)

| control | changes | check |
|---|---|---|
| height in diameters (24–96) | `d0` for a fixed H | the readout's diameter count changes |
| top/foot ratio (0.70–0.95) | `dt` | top width changes, foot does not |
| swell (0–6 % of `d0`) | the Bézier's middle control | swell-above-line changes, endpoints do not |
| swell station (1/4–1/2 H) | where the swell sits | the station readout moves |
| base height (1–3 `d0`) | the base steps | base height in the readout |
| capital height (1–3 `d0`) | the capital steps | capital height in the readout |

No control is decorative: the page's own check fails if any of the six leaves every printed
number unchanged.

## Rules with a check each

1. **Thin.** `d0 / H ≤ 1/24` at every setting; default 1/48. Check: the test sweeps the
   diameter control and fails above the ceiling.
2. **Taper.** `dt < d0` by at least 5 %. Check: the test compares the two widths.
3. **Entasis.** At the swell station the shaft is wider than the straight line between foot and
   top, and the swell is at most 6 % of `d0`. Check: the test measures both.
4. **Foot is the widest point of the shaft.** `d0 > d` at every station above the foot. Check:
   the test samples the profile.
5. **Base and capital stand proud of the shaft.** Their widest step is wider than the shaft at
   the same height. Check: the test compares the steps with the profile.
6. **One line per pillar.** The figure holds exactly one polyline per pillar and no fill. Check:
   the test counts paths and refuses a closed path.
7. **The outside edge.** The right pillar's line lies at or outside its axis on the right; the
   left pillar's on the left. Check: the test signs the offsets.
8. **Nothing is cut by the frame.** The line's bounding box plus the stroke sits inside the
   figure box. Check: the test compares the box with the canvas.
9. **The page is generated.** `workbench/side-pillars.html` is written by
   `scripts/side_pillars.py`; a test rebuilds and compares (register row 18's rule: compare after
   dropping the build-stamp line). Check: `tests/test_side_pillars.py`.
10. **The page carries no rules.** Its `<script>` is one import; the maths lives in the
    generator/library named above and is linted or tested. Check: the page has no inline maths.
11. **The picture is a curve, not a zigzag.** The shaft is a quadratic Bézier; the stations are
    exact and the drawing between them is stated as approximate. Check: the test reads the path
    command (`Q`, not a chain of `L` through sampled points).
12. **The readout says what it measures.** Each number names its unit ("width, share of the
    height", "height, in foot widths"). Check: the page text contains the unit words.

## Inherited from the last specs (`SPEC-glue-int.md`, `SPEC-class-v-int.md`)

- The four values of a plate's character are not used here: a border pillar is one line, with no
  side curves. The pillar's "expression" is its silhouette, not a band.
- Fractions, not decimals, wherever a value is exact; degrees only as a readout of a rational
  turn. This page has no turns, so it prints no degrees.
- Directions and rational points come from p-triples, never from `cos`/`sin` of a typed angle.
- A figure is fitted to its data, uses the full box, and carries its labels inside it.
- A page is generated by one script; the generated HTML is never edited by hand.
- Links are given as text in the reply; the agent never opens a page for the operator.

## What it does not do yet

- **No pair with the real top border.** The dash is a context note; the horizontal run of glue
  curves is not drawn to scale.
- **No flutes, no volutes, no ornament.** The operator asked for expression through proportion
  first.
- **No page integration.** It is a study page; whether the pillar ships as the book's border is
  a later decision.
