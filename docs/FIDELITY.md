# Fidelity: the accepted budget

> **Important — operator decision, 2026-10-30.** A chain that imitates a
> clothoid is accepted at **1.4–1.6 per cent**. That figure was set for the
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
for a clothoid. It was accepted as good enough for ornament at print size.

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

## Where the rule came from

The operator set it on 2026-10-30, in the same conversation that produced the
promotion gate. Record it here, in `SESSIONS.md`, and in the public docs; it is
the kind of decision that is expensive to rediscover.
