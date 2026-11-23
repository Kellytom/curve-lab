# The sibling finding — measured 2026-11-23

*What the sibling map actually says about the 110 over-ceiling curves. Numbers
from `scripts/sibling_map.py` → `workbench/sibling-map.json`, and from the
station-chain measurements below.*

## 1. "Shorten the stack" does not make a sibling

Every stored family curve is `u` fixed, `v` a product of linear roots: mirrored
pairs `(r, 1−r)` and a repeated stack at ½. Factoring `v` back gives the recipe,
and shortening the ½ stack is the obvious "nearby recipe" at the ceiling.

Results over the 110 over-ceiling curves:

- **72 have such a recipe** (roots found and rebuilt); **18 match an existing
  stored curve exactly** — those are the "in-catalogue siblings" the notes
  claimed, and there are 18, not 7.
- **Every one of them misses by at least 8.5 % of the curve's size.** The best
  is `wave-middle-7 → 1of2-1of2-mid` at 8.54 %; typical is 25–45 %; the
  in-catalogue matches (e.g. `lace-1of8-1of3-3 → lace-1of8-1of3-1`) sit at
  ~25 %.
- **38 have no recipe at all**: 5 where `u` itself is over the ceiling (the
  fit family, served by the speed-space re-fit instead), 33 whose `v` does not
  factor into small-denominator rational roots (the loop family and others).

**The stack is load-bearing.** Removing a ½ root does not shave a degree off a
curve's shape — it changes the curve. A "sibling" 25 % away is a different
curve in the same family, not the same curve at a lower degree.

## 2. The speed-space re-fit agrees

`reduction/speed_fit.py` at speed 5, for the same families: wave-1of8-4
misses 122 units, wave-middle-6 77 units, the loops 10⁹⁺ — order-of-magnitude
refusals, not near-misses. Two independent methods say the same thing: the
wave, loop and lace character **exceeds the degree-11 information budget**.
No nearby exact curve carries it.

## 3. But the ceiling is not the gate for a drawing

The cubic-chain export (exact stations joined by Catmull-Rom spans — the house
rule, and what the Inkscape round trip already does) reproduces any of these
curves to any stated tolerance:

| curve | 32 spans | 64 spans | 128 spans |
|---|---|---|---|
| wave-1of10-5 | 7.5 % of size | 2.2 % | 0.56 % |
| wave-1of10-1of5-1 | 4.7 % | 1.3 % | 0.33 % |
| wave-middle-7 | 0.61 % | 0.16 % | 0.04 % |
| lace-1of8-1of3-3 | 5.6 % | 1.6 % | 0.41 % |

(The miss halves roughly as the span count quadruples — the cubic rate, as
expected.)

## 4. What this means for the plan

The 110 curves split into three honest outcomes, and only the operator can
choose between them:

1. **Five curves** (the fit family) have an exact ceiling form — the re-fit
   candidates already in the sandbox.
2. **Eighteen have in-catalogue siblings** — but they are 25 %-apart curves,
   so they are alternatives, not replacements; choosing one changes what the
   catalogue shows.
3. **The rest cannot be ≤ degree 11 without becoming different curves.** They
   are not blocked, though: as DRAWINGS they export as station chains at a
   stated miss (2 % or better at 64 spans, 0.6 % at 128). The degree ceiling
   binds the EXACT RECORD (the PH object for glyphs and exact editing), not
   the picture.

So the remaining work is a **policy decision**, not a search: for each family,
is the exact record kept at its degree (fine for drawing, drawing-only for
export), or replaced by a successor curve designed at the ceiling (new curve,
new name, same character), or dropped from the exact catalogue?
