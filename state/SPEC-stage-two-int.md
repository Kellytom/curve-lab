# MERGED into the prime mover (2026-11-19)

This page was consolidated into `/prime-mover/`; `stage-two.astro` is a redirect. What follows is kept as the record of what stage II was.

# SPEC — stage II, the curves (`/stage-two/`)

The clean description of one page: what it is for, what it shows, and the rules it
must keep. Every fault goes in `PROBLEMS-stage-two-int.md`, never here.

**The page:** `app/src/pages/stage-two.astro`
**The engine:** `app/src/scripts/stage-two-curves.js`
**The shared driver:** `app/src/scripts/prime-mover-driver.js`
**The check:** `app/scripts/check-stage-two-page.mjs`

## What the page is for

Stage I supplies a prime mover: a point on the circle at every station, exact, with
coordinates `X` and `Y`. **Stage II turns those two numbers into a curve.**

The curve is a polynomial of `X` and `Y` with whole-number coefficients:

    px = p(X, Y)
    py = q(X, Y)

Because `X` and `Y` are ratios of whole numbers and the coefficients are whole
numbers, every curve point is a ratio of whole numbers. Nothing is sampled on the
way in; the only sampling is the straight line drawn between one exact station and
the next, and the page says so.

## The spirograph (Fig. 2)

Two vanes from **one** generator, `R = (24 + 7i)/25`:

    outer   a·Rᵏ          one turn a station
    inner   b·R^(m·k)     m turns a station, m a whole number
    curve   the sum of the two

The ratio `m` must be whole, or the pattern never repeats — two different p-triples
have an irrational ratio and produce a smear, not a spirograph. Every station is
exact, because `R` has length exactly one.

The figure draws the sum in ink, the outer vane in orange and the inner in blue, so
the shape can be read back to the arms that made it. Ratio chooser: 3, 5, 7, 9.

Rules: three paths (sum, outer, inner); the title names the ratio and the station
count; the ratio chooser changes both.

## The presets

| preset | px | py | what it shows |
|---|---|---|---|
| **the circle** | `X` | `Y` | the prime mover itself — the baseline |
| **the S** | `X` | `Y − Y³` | the fold that turns a circle into an S |
| **the loop** | `X − X³` | `Y` | a loop where the walk turns back on itself |
| **the leaf** | `X·Y` | `Y` | two lobes, joined at the axis |
| **the crest** | `X` | `X·Y` | a wave that leans with the height |

Each is whole-number arithmetic on ratios, so each stays exact. The presets are
named for what they look like, not for the polynomial degree.

## What the page shows, top to bottom

1. **A title and a lead** saying that this page feeds the prime mover into a
   polynomial.
2. **One chooser** — the preset. The walk is **fixed**: the twelve hit points of
   `walker(k)`, so there is no step chooser to send it somewhere else.
3. **Fig. 1, the curve** — the preset's curve through the exact stations, with the
   circle drawn faintly behind it as the baseline. The figure carries its own title,
   names the preset and the step, and has x and y axes.
4. **A readout** — clicking a station names its `i`, `x` and `y` in exact ratios.
5. **The station table** — `i`, `px`, `py` for the first stations, every value a
   whole number or a ratio of two whole numbers.

## Inherited from the prime-mover spec

Read before this page was built, and carried over:

| invariant | from |
|---|---|
| every number a whole number or a ratio, no decimals | prime mover, rule 1 |
| no rounded number places a point | prime mover, rule 2 |
| a reference circle carries no lines of its own | prime mover, rule 7 |
| the figure names itself, with x and y axes | prime mover, Fig. 4 rule |
| the plot is square, one scale on both axes | prime mover, Fig. 4 rule |
| no control does nothing | prime mover, rule 6 |
| one minus sign (U+2212), never a hyphen | prime mover, rule 8 |
| `i` is only a tag or the dial, and the column says which | prime mover, rule 10 |

### Drawn as curves, not as zigzags

Every plotted sequence joins its exact stations with a **cubic Bézier chain**
(Catmull-Rom through the points). The stations are exact; the line between them is
**approximate**, and the figure says so. Straight segments between correct points are
still a wrong picture.

## The rules the page must keep

1. **Every curve point is an exact ratio.** The table holds no decimals.
2. **The baseline circle is always drawn**, faintly, so the deformation is visible —
   and it **carries no lines of its own**. No chords, no radii, no walk drawn on it.
   It is a reference, not a drawing: the only line in Fig. 1 is the mapped curve.
   (Same rule as the prime mover's ring: a line that carries no information is
   decoration, and decoration across a circle hides the one thing the circle is for.)
3. **Both choosers drive the drawing and the table** — change either and the figure
   changes.
4. **The figure names the preset and the step inside it.**
5. **No control does nothing.**
6. **No complex step, no imaginary unit.** Curves are `px` and `py`, never `z`.
7. **One minus sign:** U+2212, never a hyphen.
8. **The drawn line between stations is a sampled line**, and the page says so.

## Not on this page yet

- Saving or exporting a curve.
- Offsets, widths, or two-tone fills on these curves.
- A free choice of polynomial coefficients: the presets are fixed.
- Keyboard access to the stations.

## How to change this page

1. Change this file first.
2. Rewrite `stage-two-curves.js` whole for a structural change; patch a single line.
3. Run the gates: `node app/scripts/check-stage-two-page.mjs`,
   `.venv/bin/python scripts/check_no_imaginaries.py`,
   `npm --prefix app run check`.
4. Record any fault in `PROBLEMS-stage-two-int.md` with its guard.
