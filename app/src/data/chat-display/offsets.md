# The offset curves, and what happens at a tight turn

The side curves are not a fixed distance from the spine. Each side carries its own formula:

$$d(t) = w \cdot \left(1 + s \cdot p(t)\right)$$

with $w$ the asked width (1 % of the curve's own size on an unedited curve), $s$ the character
strength (the average of plus and minus), and $p(t)$ the profile — `bow`, `s` or `taper`.

## Why a tight turn makes the rail cross itself

Follow the rail at that distance. Where the curve turns tighter than the distance itself, the
rail runs past the centre of curvature and comes back on the wrong side. The test is

$$d(t) \cdot \kappa(t) > 1$$

The rail then crosses itself, and the small loop between the two crossings is the piece that
folded inside-out. That crossing is correct, not a bevel: the geometry did what the formula says.

## What the plate will do (not in the plates yet)

1. The rail keeps its own formula; no cap, no rounding. *(planned — today the plate still caps and rounds)*
2. Every self-crossing is found and marked with a red dot.
3. The loop it encloses is **not drawn**: the curve stays one stroke with an invisible span.
4. The span is recorded per plate, as a fraction of the rail's stations, in
   `book/print/rail-holes.json`, so Inkscape can cut at the mark instead.

## What a probe finds on saved curves

- `c-0046` — three crossings on each rail;
- `c-0065` — fifteen on one side, twelve on the other;
- `c-0273` — two and one.

Those numbers are printed, not guessed: `PLATE.selfIntersections` counts non-adjacent segment
pairs that meet, and the plate reports what it hid.
