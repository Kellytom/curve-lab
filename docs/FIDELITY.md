# Fidelity: the accepted budget

> **draft A** — a working draft, not a final text.
> **Important — operator decision, 2026-10-30.** A chain that imitates a
> An Euler curve is accepted at **1.4–1.6 per cent**. That figure was set for the
> curvature-law fit (the chain follows the ideal Euler law to 0.8% of peak; the
> drawn cubics to 1.4%, rms 0.8%). For a **chain study** the working rule is:
> the worst span-end drift must be **at most 1.6 per cent of the study's
> height**. State the metric whenever the number is quoted. It is a budget for a
> resemblance, **not** node parity with the source drawing.

This page exists because the same question — “is this close enough?” — has now
been answered once, and the answer was nearly lost. Future work should reuse the
rule instead of re-litigating it.

## The number that was already accepted

From the spine layer's own handover:

> Measured on the curl's entry run: the chain follows κ = κ₀ + kd·s to **0.8 %
> of peak**; the drawn cubics to **1.4 % (rms 0.8 %)**. It is an Euler spiral to
> a percent and a half.

That is the precedent: about one and a half per cent, for a chain standing in
for an Euler curve. It was accepted as good enough for ornament at print size.

## Two different percentages, and why the difference matters

The original **1.4%** is a *curvature-law* figure: how far the drawn curve's
bending departs from the ideal Euler spiral over a run.

The **chain-study rule** measures something else: the distance between each
span end and the source drawing's node, as a percentage of the study's height.

They have the same magnitude and the same purpose — “close enough to read as the
same ornament” — but they are not interchangeable. A future report must say
which one it is using. Do not compare a node drift against the 1.4% curvature
figure as if they were the same measurement.

## What a chain study must report

Every chain study page and test must carry:

- the turn step (the triangle's angle),
- the chord count,
- the drift at every span end, not only the worst,
- the worst drift in units **and** as a percentage of the study's height,
- how long the build took, so the cost is visible,
- a plain statement of what the study is **not** (P01 parity, in the first case).

## The measurement (study 01, right half)

Measured in P01's own frame, start heading snapped to the nearest whole turn.
The reference is the ported P01; the study height is 1510 units.

| turn step | chords | worst drift | of height | build |
|---|---|---|---|---|
| 2° | 62 | 66.19 units | 4.38% | 0.08 s |
| 1° | 115 | 21.38 units | 1.42% | 0.08 s |
| 0.5° | 221 | 19.44 units | **1.29%** | 0.25 s |
| 0.25° | 431 | 20.76 units | 1.38% | 1.45 s |
| 0.125° | 852 | 1.67 units | **0.11%** | 9.44 s |
| 0.0625° | — | did not finish in 60 s | — | — |

The coarse steps are **not** monotone, and that is not a wall: the errors from
independently rounded corners can add or cancel, so 0.5° happens to beat 0.25°.
At 0.125° the grid is fine enough that the residual collapses to 0.11%. The
limit is cost, not principle: the exact fraction arithmetic grows with the chord
count, and 0.0625° did not finish in a minute.

So the honest statement is: **finer triangles do converge, and cost rises
steeply.** An earlier note in this repository said the drift “does not fall with
the angle”; that was wrong and has been corrected. It was based on runs that
stopped at 0.25° and on a 0.1° run that timed out.

## The rule

1. Choose the turn step and report it.
2. Build the study.
3. Measure every span end against the source.
4. **Pass** if the worst drift is at most **1.6% of the study height**; report
   the number either way.
5. If it fails, the honest options are: a finer step (with its cost), shorter
   chords, or the float hybrid. Never smooth the difference away silently.

Under this rule study 01 at 0.5° passes at **1.29%**. The same study at 0.125°
passes with a wide margin at **0.11%**, at 852 chords and about nine seconds for
the composite alone.

## What this rule does not license

- It does **not** make the chain study P01. The ported P01 matches its reference
  to **0.03 units**; the chain candidate is **19.44 units** at 0.5° — about 650
  times further. Calling the candidate “P01” would be false.
- It does **not** make the chain exact ink. The plan is rational; the chord
  lengths for arcs are rational approximations of `2R sin(α/2)`, and the page is
  floats.
- It does **not** settle the fill. A ribbon width on a per-chord chain crosses at
  the corners under the engine's rail builder; the filled shape is the spine
  layer's miter job (`ribbon.outline`).

## Two profiles, one shape

The exact profile is the chain itself: one straight design segment per chord,
and therefore one cubic per chord. At a 0.5 degree step that is 943 design
segments and **1,164 cubics** with the mirror, a 249 KB page. It is the file to
zoom into and to keep as the record.

The practical profile fits one Euler curve through each *structural run* — the part
between two of the study's corners — and subdivides a run only when the measured
error exceeds the tolerance. At 0.5 mm:

| profile | design segments | cubics with mirror | page | worst deviation |
|---|---|---|---|---|
| exact | 943 | 1,164 | 249 KB | reference |
| practical, no pin | 18 | 34 | 7 KB | 0.42 mm |
| practical, one pin | 19 | 36 | 7 KB | 0.32 mm |
| practical at 0.25 mm | 22 | 42 | 8 KB | 0.23 mm |
| practical at 1.0 mm | 16 | 30 | 6 KB | 0.92 mm |

`curve_lab/practical.py` builds it; `workbench/practical-curve.html` compares it
with the exact curve.

## Pins: choosing a branch on the exact curve

The exact curve is where you zoom in to choose a branch point. The practical
curve cannot be a fixed simplification, because a branch must land on a real
vertex with the exact heading.

A **pin** is that choice: a point on the exact chain (or its knot index) made a
hard split in the practical fit. Both sides of the pin use the chain's outgoing
heading; the rest of the curve is re-simplified within the same tolerance. The
measured pin error is about **2e-7 units**, and the tangent is continuous across
it, so the branch joins without a correction. Adding one pin costs one or two
cubics.

Workflow: choose on the exact curve → pin the point → regenerate the practical
curve → attach the branch.

## How that compares with type

A capital C in a serif face is **not** two or three cubics; that is a geometric
ring, not a letter. Measured native counts from ten installed serif faces:

| face | C | @ | & | ~ |
|---|---|---|---|---|
| Times New Roman | 21 | 55 | 45 | 14 |
| Baskerville | 19 | 46 | 42 | 12 |
| Didot | 38 | 82 | 70 | 24 |
| Bodoni 72 | 34 | 51 | 47 | 10 |
| Big Caslon | 42 | 68 | 94 | 12 |
| Charter | 18 | 56 | 32 | 16 |
| Hoefler Text | 23 | 49 | 48 | 14 |
| Iowan Old Style | 20 | 56 | 48 | 16 |
| New York | 28 | 71 | 47 | 18 |
| PT Serif | 32 | 69 | 64 | 16 |

TrueType stores quadratics, and one cubic reproduces a quadratic exactly by
degree elevation, so the count is the cubic equivalent. One serif C is 18–42
cubics; `@` is 46–82 and `&` is 32–94. The practical half at 14 Euler curves is in the
range of one serif C; the exact half at 221 is past a whole glyph, and the band
at 722 is past an `@` several times over.

## The fitter bug behind the old count

The first exact measurement was inflated by a real bug: at a segment boundary
the backend reports the *next* segment's tangent, so a corner corrupted the end
of the previous cubic and the fitter kept splitting to hide it. Reading the
tangent just inside the segment fixed it. One straight segment now takes one
cubic, not nine.

## Where the rule came from

The operator set it on 2026-10-30, in the same conversation that produced the
promotion gate. Record it here, in `state/SESSIONS-int.md`, and in the public docs; it is
the kind of decision that is expensive to rediscover.
