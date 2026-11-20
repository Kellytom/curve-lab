# CHARACTER — finding curves with the character of the stored collection

The operator's mark: curves like the ones already in the database — loops, flats, a
symmetry the eye can see — and rational throughout. This is the search that looks for
them, and what it found.

## The method

1. **The walk, sampled finely.** One triangle turn a station (16.26° for 7-24-25, 4.09°
   for 56-783-785), so a curve has 20 to 90 exact stations instead of 13. Thirteen
   stations draw stars; twenty and more draw curves.
2. **Whole-number polynomial maps** of the walk's `X` and `Y`: eighteen of them, from
   `(X, Y)` to the cube, the four-fold fold, the pinch and the saddle.
3. **Measurement**, on the drawn polyline: reversals (loops), inflections (flats),
   crossing pairs, mirror gap, rotation gap, aspect, extent, and the mean turn between
   stations (smoothness).
4. **Score** — loops and flats first, then crossings, symmetry and smoothness; a dot or
   a smear is penalised.

## What came out

The mature shapes are all **the astroid family**: `x = X(1 − Y²)`, `y = Y(1 − X²)` on
the thin triple, and the pinch `x = X − X³`, `y = Y + Y·X²`. Both are smooth, exactly
symmetric (mirror gap 0.0001), and have four to eight loops with no crossings — the
calm, weighted shapes rather than the star-like smears.

Candidates, with the numbers: `workbench/character-candidates.json`.
Montage: `workbench/character-curves.svg`.
Full scored table: `workbench/character-curves.json` (48 curves).

| curve | triple | stations | loops | flats | crossings | aspect | score |
|---|---|---|---|---|---|---|---|
| the lens | 56,783,785 | 90 | 4 | 8 | 0 | 1.00 | 14.42 |
| the pinch | 56,783,785 | 90 | 8 | 8 | 0 | 2.83 | 14.17 |
| the four-fold | 56,783,785 | 90 | 8 | 8 | 0 | 1.00 | 14.15 |
| the four-fold | 5,12,13 | 17 | 7 | 7 | 0 | 1.00 | 11.56 |
| the lens | 7,24,25 | 24 | 2 | 8 | 0 | 0.99 | 10.98 |
| double fold | 5,12,13 | 17 | 7 | 0 | 4 | 1.01 | 10.84 |

## The two-lap finding

A single lap of a thin triple leaves a small gap — the walk never closes — so the
figure has a visible break where the last station meets the first. Drawing **two
laps** closes it: the second retraces the first closely enough to hide the seam.

The measurement must stay on **one lap**: counting crossings on two laps counted
every crossing twice (154 where the truth was 0). The counter now takes one lap and
the drawing takes all of them.

## What this says

- **Fine sampling is the whole difference.** The same map on thirteen stations is a
  star; on ninety it is a curve with a waist and a cusp.
- **The thin triple is the lever**, and it costs denominators: `785^(2k)` is exact and
  unreadable, which is why the drawing converts at the boundary and the notes carry the
  fractions.
- **Symmetry is common here, crossings are rare.** The walk is itself symmetric, so
  symmetric maps stay symmetric; maps that cross (`the cross`, `the leaf`) need a coarse
  walk, which is what made them look like stars.

## Next

1. Add three of these to the registry through `add-registry-curves.mjs`, with the exact
   walk parameters.
2. Search *asymmetric* maps for the figures the collection has that are not symmetric.
3. Score against the stored metrics (crossings, inflections) rather than a made-up score.
