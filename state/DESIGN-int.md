# DESIGN-int — decisions already taken, and why

Read before changing a control, a page or an ordering. Each line is a decision,
the reason it was made, and its status. **Settled** means do not re-open it
without the operator saying so in words. **Open** means it is a live question.

Dates are the day the decision was made. Where the operator asked for it, the
entry says so.

## Speed numbers (the boxes and their sliders)

- **Two sliders per speed number: mantissa and decade.** Settled 2026-11-14, by
  the operator. The mantissa slider (red) sets the size 0–10, the decade slider
  (blue, 64 px) sets the power of ten −2…6. Reason: large numbers are quick to
  reach; the mantissa alone cannot get to 1000 or 0.01 without the buttons.
  Twenty-four sliders at degree 11 is correct, not a bug.
- **The sign lives in the number box, not the slider.** The slider carries size
  only; the `−` button flips the sign. Reason: a slider through zero would make
  zero sit in the middle, which reads as "set to middle" when the value is
  nothing.
- **Scale buttons stay beside the sliders** (`√2`, `×1.1`, `e`, `×1`, `×10`,
  `×100`). Reason: the decade slider is coarse; these are the exact snaps.
- **The power labels follow the step, written as fractions.** At step ½ the six
  boxes read `t^0`, `t^1/2`, `t`, `t^3/2`, `t^2`, `t^5/2`; at step ⅓ they read
  `t^0`, `t^1/3`, `t^2/3`, `t`, `t^4/3`, `t^5/3`. The worked formula under the
  page and the closing line use the same names. Reason: a box labelled `t^2`
  that carries `t^1` is a lie. Fractions, not decimals, so `t^5/2` never becomes
  the rounded `t^2.5`. Settled 2026-11-14.
- **The exponent step is a slider with named buttons** on the experimental page
  only: 1, ½, ⅓, ¼, plus any value between (0.75 gives `t^0.75`, `t^1.5`,
  `t^2.25`). Settled 2026-11-14.

## The roots panel and the ruler

- **A flat spot is a root.** The wording on the page and in this repo: a root of
  the y speed is where the stroke runs horizontal. Settled.
- **Mirror is on by default.** One click at `1/9` places `1/9` and `8/9`.
  Reason: symmetry has to be put in on purpose; a random row almost never has
  it. Settled.
- **Dots stack for multiplicity.** Three dots at `1/2` is the triple flat, which
  is what makes the long flat middle. Settled.
- **Click the line to add; click a dot to remove that copy; shift-click clears
  the stack.** Settled 2026-11-14, by the operator ("click on the dot again and
  it disappears"). Dots sit clear of the line so the line stays clickable.
- **`fill the numbers` multiplies the roots out** and picks the rung that fits
  (five spots → degree 11, six → degree 13). Reason: the row is the polynomial
  the spots multiply to; nobody should type it by hand.
- **A fractional bow scales both rows** by its denominator, and the status line
  says so. Reason: a common scale leaves the shape alone and keeps every number
  whole.
- **Ruler positions are fractions with denominators 2, 3, 4, 5, 6, 7, 8, 9, 10
  and 12**, mirrored about `1/2`. Settled.
- **Sliders for `copies at 1/2` (0–6) and `bow` (−4…4)** sit under the ruler.
  Settled 2026-11-14.

## Pages

- **`ph-nth-sandbox.html`** — part 1: the degree ladder, a gallery of the seeds
  and whatever the finder wrote.
- **`ph-nth-sandbox-2.html`** — part 2: the **Knotlike curves** section first,
  then everything else.
- **`ph-nth-sandbox-exp.html`** — experimental, **no gallery at all**, exponent
  step defaults to ½. Reason: a curve under test must not sit among the ones we
  keep. Settled 2026-11-14, by the operator.
- **The knotlike section leads with the operator's six pasted curves**
  (`wave3`, `knot`, `bud`, `knot-2`, `wave5`, `hersheys copy`), tagged *yours*,
  then the finds tagged *found*. Reason: the finds are compared against them,
  not instead of them. Settled 2026-11-14.
- **Order inside the finds: most meetings with the partner copy first, then the
  cheapest grid, then the lowest bend.** Reason: meetings is the knot measure;
  among equals the cheap grid is the better curve. Settled 2026-11-14.
- **Moves are stored by name in the generator**, never by hand-editing the page:
  `DEMOTE`/`AFTER` for the block below figure 42, `MOVES` for single moves. A
  render-time sort used to undo them; there is none now — the order the page
  shows is the order the generator wrote.

## Fractional exponents (the experimental page)

- **The ladder runs to 30 numbers per axis** (speed degree 14, position degree
  29) and the experimental page opens there, so step ½ reaches `t^7` — fifteen
  rows instead of six. Reason: halving the step halves the top power, so double
  the rows to get back to it. Settled 2026-11-14, by the operator.
- **No grid and no inflection count off whole powers.** The page prints
  `grid n/a` and `inflections n/a`. Reason: a fractional exponent has no integer
  grid and no polynomial Wronskian, so those numbers do not exist. Settled
  2026-11-14.
- **Bend, closest and openness are measured from the curve** when the step is
  not 1.
- **Negative `t` uses the odd extension** `sign(t) |t|^(k·step)`, and the readout
  says so in words. Reason: a fractional power of a negative number is complex;
  this is a declared choice, not a silent one.
- **Mirror symmetry holds only at step 1.** Measured: mirror gap 0.0000 at step
  1, 0.42 at ½, 0.41 at ⅓, as a share of the curve's size. Reason: the speed is
  a polynomial in `t^s`, and mirroring `u` about ½ is the same as mirroring `t`
  about ½ only when `s = 1`. Do not promise balanced knots at fractional steps.
- **A fractional step cannot be symmetric at all, not merely less so.** Measured
  over 569 random rows at steps 1, ½, ¾, 3/2 and 2: not one came within 1e-3 of
  its own mirror or half turn. The reason is arithmetic, not sampling: symmetry
  needs the parameter point `t = 2^(-1/s)`, which is irrational for every
  rational step except 1. So half powers are for *new shapes*, never for
  balanced knots. Settled by measurement 2026-11-14.
- **The x row may carry its own mirrored roots.** This is the axis that adds
  loops while keeping the mirror exact: both rows are mirrored, so the curve
  stays symmetric. It produced knots with 20 meetings where the best earlier
  family reached 16, so it is the preferred way to widen the search.

## High-order tail terms loosen the knot

The low powers set the knot; a small tail at the top powers (measured on the
operator's find: `t^11` to `t^14`, coefficients of order one) opens it up and
costs the mirror.

| tail scale | crossings | knot share | mirror gap |
|---|---|---|---|
| 0 (the lace) | 13 | 4% | 0.00 |
| 0.5 | 8 | 9% | 0.28 |
| 1 (the find) | 8 | 19% | 0.51 |
| 2 | 7 | **43%** | 0.55 |
| 4 | 5 | 3% | 0.16 |
| 8 | 4 | 1% | 0.44 |

So: doubling the tail takes the knot from 19% to 43%; quadrupling it destroys the
crossings instead of loosening them. The symmetry is gone from the first step —
that is the point of the axis, and it is the only lever found so far that makes a
knot bigger without flattening the whole figure. The find is kept as
`loose-knot-tail14` in the knotlike section.

## Tweaks that keep the mirror

A row is even or odd about t = 1/2, and a tweak keeps the mirror only if it has
the same parity as the row it touches. Measured on the operator's curve: x is
even (reads the same from the far end), y is odd (reads as its own negative).

Patterns that hold the mirror, as additions at the given powers, times a size:

| row | powers | numbers |
|---|---|---|
| x (even) | t1, t2 | -1, +1 |
| x (even) | t2, t3, t4 | +1, -2, +1 |
| x (even) | t3 … t6 | +1, -3, +3, -1 |
| y (odd) | t1, t2, t3 | -1, +3, -2 |
| y (odd) | t2 … t5 | -1, +4, -5, +2 |

The operator's own habit — +0.1 on one power, −0.1 on the next — is the first
row: it works because the two changes cancel when the row is read backwards.

Multiplying a whole row by `1 + size(t − t²)` also holds the mirror, and it is the
stronger lever (crossings 13 → 19 at size 0.2). Two traps, both hit and fixed:
the product is two powers longer than the row — trimming it to the old length
drops the terms that balance the change, which is exactly the lopsided curve; and
it must be done in powers, not in boxes, because at step 1/2 a box is half a
power and the factor would centre at t = 1/4.

The experimental page carries these as buttons; the primary curve redraws at once
and `window.phNthSymmetry()` reports the mirror gap, which is 0.0000 for every
pattern above at steps 1 and 1/2.

## What a tweak costs in grid

The tweak sizes are fractions, and the fraction decides the integer grid the curve
needs. Measured on the operator's curve at step 1, adding `x: t1,t2`:

| size | grid after | factor |
|---|---|---|
| 1 | 6,930 | ×2 |
| 1/4 | 22,176 | ×6.4 |
| 1/2 | 27,720 | ×8 |
| 1/8 | (cheaper than 1/4 in every case tried) | — |
| **1/3** | **86,625,000,000,000** | ruined |

1/3 is not an arithmetic limit but a machine one: a third cannot be written
exactly in binary, so every coefficient becomes a long decimal and the grid
explodes. **Only halves, quarters, eighths and whole numbers are offered**, and
the page says why. The multiply by `1 + size(t − t²)` is the most expensive
(1/2 took the grid to 5,765,760) because the factor is used twice.

The status line reports the grid after every tweak, so the cost is visible rather
than discovered later.

## A tweak is a share of the coefficient, not an absolute step

An absolute size changes every coefficient by the same amount. A share takes a
fraction of the coefficient itself, which keeps a mirrored pair balanced: the pair
has equal magnitude, so a quarter of 16 moves both ends by 4.

Measured on the default curve at step 1, adding `x: t1, t2`:

| share of the 16 pair | tweak | x becomes | grid |
|---|---|---|---|
| 1/16 | +1 | 3, -17, 17 | 6,930 |
| 1/8 | +2 | 3, -18, 18 | 3,465 |
| **1/4** | **+4** | 3, -20, 20 | **693** |
| 1/2 | +8 | 3, -24, 24 | 3,465 |

All keep the mirror exact. The grid is a least common multiple over the whole
position polynomial, so a share can lower it — 1/4 made the curve five times
cheaper — as well as raise it, which 1/16 did. That is the operator's gcd
instinct confirmed: the numbers have to be read together, not one at a time.

The panel offers both levers, an absolute fraction and a share of the x pair, and
the status reports the grid after every tweak.

## A rung hides numbers, it never deletes them

Moving to a lower degree keeps every coefficient above the new rung in a stash and
shows zeros in the new boxes; moving back restores them. Measured: a value of 777
in the top box at degree 29 survives degree 11 and returns on the way up. The rule
is the same everywhere in this project: a view may hide data, never destroy it.

## Optical versus real (matters for the Bezier conversion)

Some controls move the camera and leave the numbers alone. Others change the
numbers. Only the second kind may be exported.

**Optical — the rows are untouched, so these must never reach an export:**
`zoom`, `focus the knot`, `show only the knot` (the `t from` / `t to` window),
`rotate -45`, `hide the grey curve`, `rails`, `character offsets`, the terminals.

**Real — these rewrite the rows:**
the flat spots and the fill buttons, `copies at 1/2`, `bow`, the exponent step,
typing in any box, and `rebuild without the legs`.

Rule for the Bezier step: read `terms` from the record and convert those. Never
convert what the plot shows, because the window can crop the stroke and the
zoom changes nothing at all. If a curve with no legs is wanted, it must come from
`rebuild without the legs` (exact, checked against a Python reference to the
integer) or from different flat spots — not from the window.

Measured note: on the curves tried, the self-crossings run across nearly the
whole `t` range (for example t 0.081 to 0.919), so no shorter exact span holds
them and the rebuild honestly reports the whole curve. Legs are shortened by
moving the flat spots, not by cutting `t`.

## Searching and naming

- **Symmetry is built in by choosing roots, never by hoping.** A row from
  mirrored roots is symmetric by construction; a random small-integer row
  essentially never is (1,500 draws, 0 hits).
- **Names state the construction**: kind + every mirrored pair + the middle
  count. `lace-1of9-3` = a lace (four or more self-crossings), pair at 1/9 and
  8/9, three roots at 1/2. `2x` marks a repeated pair. Settled.
- **The finds are split by batch.** Part 2 keeps the earlier family; the
  experimental page's foot carries only the newer batch, tangliest first, odd
  shapes included. Reason: a page for looking at new shapes should not be a
  second copy of the kept collection. `found-curves.json` marks each row
  `batch: first` or `batch: new`. Settled 2026-11-14, by the operator.
- **The "x row roots" axis turned out to be the bow, sampled finer.** A row like
  `[7, -25, 25]` is `7(1 - 3.57 t(1-t))`, a bow of 3.57 — between the old
  hand-picked 2 and 4. So the gain came from trying bow strengths that were not
  on the list, not from a new construction. The bow slider now reaches ±12 for
  that reason.
- **Finds land in `workbench/found-curves.json`**, which the galleries read at
  load. A row proportional to an existing seed is skipped.

## Process

- **No internet, no CI, no push without the operator saying so.**
- **Generated pages may be read.** Reading the built page is how a claim about
  the page is checked; the DOM is the evidence, not the generator's list.
- **A number in a report is measured, not recalled.** Counts, positions and
  order come from the DOM or from a script's printed output, with the command
  named.
