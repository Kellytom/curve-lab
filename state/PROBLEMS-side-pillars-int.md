# PROBLEMS — side pillars (`side-pillars.html`)

The clean description is `state/SPEC-side-pillars-int.md`. This file holds every
fault the page has had: what it looked like, what was wrong, the fix and the
guard. No operator has looked at the page yet; the faults below were caught by
the tests and by the rendered check on 2026-11-23, in the build session.

## 1. One bow across the page, labels at the edges

**Symptom.** The first render showed a single dark curve from the top of the
figure to the bottom, at the centre; the two pillar labels sat at the right and
left edges where their pillars should have been.

**Cause.** The pillar path strings are in model units (x around ±150, y up from
0 to 480). They were written into the SVG as if they were already SVG
coordinates: no x offset of `+180`, and no y flip. Only the labels, guides and
the dashed border went through the `svgX`/`svgY` mapping, so the two parts of
the same figure landed in different coordinate systems.

**Fix.** The two pillar paths and the taper guides are wrapped in one group,
`translate(180 520) scale(1 -1)` — the single place where y is flipped, and the
same mapping `svgX`/`svgY` apply. `svgMarkup` says so in a comment.

**Guard.** `tests/test_side_pillars.py :: test_the_first_paint_puts_each_line_on_its_own_side`
reads the generated page and requires every x on the right path to sit between
140 and 170 (and the mirror on the left). A mapping fault moves those numbers.

## 2. The shaft's control point ignored the pillar's axis

**Symptom.** With the offset fixed, each shaft still bowed inward toward the
centre line: the Q control point was at the model centre instead of beside the
pillar.

**Cause.** `pillarPath` wrote `s * m.control.x` for the control point while the
stations already carried `axisX`. The endpoints were right and the control was
wrong, so the curve ran from the correct foot to the correct top through a point
near x = 0 — a bow the whole width of the page.

**Fix.** `axisX + s * m.control.x`.

**Guard.** `tests/js/side-pillars.test.js :: the outside edge: right on the
right, left on the left` now checks every x in each path, not just the
endpoints, and requires each line to stay within one foot width of its own axis.

**The lesson.** The first version of that test passed while the figure was
wrong: it looked at the endpoints only, and the endpoints were right. A guard
that reads two of seven numbers is a wish.

## 3. The swell ceiling was twice too loose

**Symptom.** The "foot is the widest point" rule failed at wide tapers: at top
ratio 70 the swell could be set to 8/100 of the foot and the shaft became wider
than its own foot.

**Cause.** The ceiling had been derived as `(100 − ratio)/2`, which allows a
control point at exactly the foot half-width before the *half*-width bulge was
accounted for. The correct bound, from `mid + 2·halfSwell ≤ d0/2`, is
`(100 − ratio)/4`.

**Fix.** `swellCeiling(ratio) = floor((100 − ratio)/4)`, and the slider's
maximum follows it whenever the taper moves.

**Guard.** `tests/js/side-pillars.test.js :: foot widest` samples 100 stations at
every ratio and every swell up to the ceiling, and `the swell ceiling tightens`
pins the three values (70 → 7, 82 → 4, 95 → 1).

## 4. Labels on the lines, and a swell with nothing to measure it against

**Symptom.** In the rendered page the title ran through the left capital,
"top" and "capital" sat on top of each other at the top right, "base" collided
with the foot label, and the swell was invisible with no reference line.

**Cause.** Labels were placed beside each feature's own x, which is the pillar's
edge at the top of the page where two labels meet; the figure had only 40 units
of top margin, which the title used; and the straight taper, the line the swell
is measured from, was not drawn.

**Fix.** The title and the explanation have their own 70-unit margin; all five
value labels sit in the empty field, anchored to its right edge, with a minimum
gap between them; each shaft carries a dotted straight-taper line; the page says
in words that the swell is under a pixel at this scale.

**Guard.** `tests/js/side-pillars.test.js :: the labels sit in the empty field,
clear of each other` sweeps five control settings and requires every label
inside the field and at least 12 units from its neighbour. The legend test in
`tests/test_side_pillars.py` requires the taper row and the 15 px legend.
