# Backburner

## B01 — Bounding parabolas for cubic/cubic intersection

**Status:** deferred 2026-11-03. Not part of the offset/ornament path.

**What it is:** a y-monotonic cubic is replaced by a sideways parabola
`x = ay² + by + c`, bracketed by two hybrid quadratics; the strip is used to
prove disjointness or drive subdivision for curve/curve intersection. It is a
boolean-path-ops primitive, not an offset construction.

**Artifact:** `workbench/bounding-parabola.html` — interactive ends, handles,
fitted parabola, hybrid quadratics, strip, and readout.

**Sources:**
- Levien, *Parallel curves of cubic Béziers*, cusp-finding aside.
- `raphlinus/raphlinus.github.io#79` — full design and cubic-scaling claim.
- `linebender/kurbo#258` — draft prototype, `examples/cubic_fun.rs`.
- `linebender/kurbo#277` / `#274` — boolean path ops and intersection traits.

**Why parked:**
- solves curve/curve intersection, not offset rails, endings or integer hits;
- prototype is draft/unmerged and needs y-monotonic preprocessing, cusp
  handling, Fréchet fallbacks and robust root solving;
- current curve-lab work does not need a new boolean/intersection subsystem.

**Revisit when:** we need robust boolean path operations, curve/curve crossing
classification, or a cusp-bracketing primitive that cannot be handled by the
existing clearance/intersection code.

## B02 — Euler spiral to cubic Bézier via endpoint parabolas

**Status:** candidate fitted option, 2026-11-03; not implemented.

**What it is:** for an Euler spiral segment, place a sideways parabola at each
endpoint of the chord. With the chord normalized to `(0,0)–(1,0)`, the left
parabola is `x = 1/3 - (3/4)y²`; the right is `x = 2/3 + (3/4)y²`. The cubic
control points are the intersections of those parabolas with the endpoint
tangent rays. The vertex is 1/3 along the chord and the endpoint arms open to
±2/3 orthogonally.

**Why it matters:** this is a **cubic Bézier fit to an Euler spiral segment**,
not an Euler spiral made of parabolas, and not the bounding/intersection
parabola. It is simple, fast, matches the symmetric circular-arc cubic, and
scales as `O(n^5)` — better than Hermite `O(n^4)`, below the optimal `O(n^6)`.
It is a plausible fitted option for the cubic seam; the p-triple polygon and
rational rails remain the exact route.

**Source:** Raph Levien, *Cleaner parallel curves with Euler spirals*,
2021-02-19, section “Euler spirals to cubic Béziers”:
https://raphlinus.github.io/curves/2021/02/19/parallel-curves.html
