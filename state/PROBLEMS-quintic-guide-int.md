# PROBLEMS — Quintic from Guide (the Inkscape extension)

Every fault this extension has had, in the order it was found. The clean
description lives in `docs/QUINTIC-GUIDE.md`; this file is the fault log, so the
same mistake is not made twice.

---

## 1. The C2 solve mixed two parameterisations — 467 px gap at every joint

**Found:** 2026-11-26, first run of the chain tests.

**What was wrong:** the tangent solve used the de Boor relation in its
Hermite form (`1/h` and `1/h²` coefficients), while the control points were
built with the Bézier form (`h/3`). The two differ by a factor of `h²`, so the
solved tangents were wrong and the chain was not C2: the second derivative
jumped by **467** at the first interior joint, and the measured miss fell only
like O(h²) instead of O(h⁴).

**Fix:** derive the relation from the Bézier second derivatives directly, which
gives `h[j-1]d[j-1] + 2(h[j-1]+h[j])d[j] + h[j]d[j+1] = 3(Δ[j-1] + Δ[j])`, and
solve a full `n+1` tridiagonal system with the two clamped ends as identity
rows. Measured after the fix: C2 gap 0, and error falls ×17 per doubling.

**Guard:** `tests/test_quintic_math.py`, `StationTest.test_the_chain_is_c2_at_every_interior_joint`
and `StationTest.test_the_chain_leaves_and_arrives_on_the_quintics_own_tangents`.

---

## 2. The error was measured to a polyline, so it had a 0.02 px floor

**Found:** 2026-11-26, when the "error falls with more segments" test failed at
8 segments: the measured error went **up** from 4 to 8.

**What was wrong:** each cubic was flattened into 16 chords and the distance was
taken to those chords. At small errors the chord sag (about 0.02 px at drawing
scale) became the answer, which is larger than the 0.001 px the exercise is
about — a floor above the target.

**Fix:** measure to the cubic itself: coarse scan for the basin, then
golden-section inside it. The floor is now ~1e-7 px and convergence is clean.

**Guard:** `ErrorTest.test_the_measured_error_falls_at_least_eightfold_per_doubling`.

---

## 3. Interpolation through six points overshoots by up to 774 px

**Found:** 2026-11-26, reading back the sidecar for a real guide.

**What was wrong:** not a code bug — a property. A quintic that passes through
six points is free to balloon between them: on the 400 px test guide the six even
points land outside the drawing by **774.39 px** and the least-squares control
points by **480.21 px**, and the curve is visible as a huge loop away from the
stroke. Blender's "Auto Clamped" handle type exists for this reason.

**Fix:** a **Clamp inside the six points** option that pulls every control point
into the box of the six points. The Bézier convex-hull property then holds the
whole curve inside that box, so the clamp is provable rather than cosmetic. It
is off by default, because clamping changes the shape the operator asked for,
and the overshoot is printed every run so the choice is never silent.

**Guard:** `OvershootTest.test_interpolation_can_leave_the_drawn_box_and_the_clamp_stops_it`
(1001 points of the clamped curve against the box).

---

## 4. A repeat run with identical settings writes no file

**Found:** 2026-11-26, headless: the second pass over its own output produced a
0-byte file, which read as "the extension deleted everything".

**What was actually wrong:** nothing. `inkex` compares the incoming and outgoing
documents and skips the write when they are byte-identical. Useful in the GUI
(no spurious saves on every live-preview tick); confusing in a shell redirect.

**Action:** recorded here so the next session does not debug it again. Test
replace-not-stack with a changed parameter, and expect no file when nothing
changed.

---

## 5. An optimiser aimed at a coarse measurement found the measurement's errors

**Tried:** 2026-11-26, before building the reducer — move the four interior
sample positions to minimise the miss, so the six points would be the best six
*on* the stroke.

**Result:** it collapsed the interior positions onto each other (0.399, 0.4,
0.799, 0.8) and reported a worse curve as better: max miss 68.24 px where even
spacing gave 4.48 px. The objective measured distance to the quintic on a
24-point grid, and a wild quintic gives that grid spurious near-hits, so the
optimiser found the grid's errors before it found the curve.

**Decision: not built.** Even spacing and the least-squares fit cover the need,
they are linear and fast, and the numbers in `docs/QUINTIC-GUIDE.md` show the
fit halves the miss without any search. Recorded so the next session does not
spend an afternoon on it again. If the search is ever wanted, the objective must
be distance to the cubic (as `measure_max_error` and `distance_to_quintic` now
do), never to a flattened grid.

---

## 6. An unknown mode silently fell back to the default

**Found:** 2026-11-26, in a shell loop comparing five modes — all five printed the
same answer. zsh does not word-split an unquoted variable, so `--pointmode=even
--spans=1` arrived as ONE argument and the mode string was `even --spans=1`. The
code's branch chain fell through to the default and every run drew the same
curve with a straight face.

**Fix:** the mode is validated against the four the dialog offers, and anything
else is refused with a message naming the four. A wrong input is never a quiet
default.

**Guard:** there is no test for a shell quoting slip; the guard is the refusal,
which shows up as an error line instead of a plausible picture.

---

## 7. Arc-length stations made the chain worse, and exposed a knot bug

**Tried:** 2026-11-27, `arclength_knots` in `quintic_theory.py`: put the chain's
stations at equal arc length instead of equal *t*, since a quintic moves at uneven
speed.

**Result:** worse, by 4–15×. Wild cage, 4 cubics: 0.950 px uniform against 3.759 px
arc-length; 8 cubics: 0.055 against 2.114. Equal arc length lengthens the *largest*
interval in `t`, and a cubic spline's error is set by the largest interval, not the
average one.

**Second fault, found by the first:** `measure_max_error` picked the segment with
`int(t * n)`, which is only correct for uniform knots. With arc-length knots it
measured each sample against the wrong stretch and reported 47 px for a chain that
was fine. It now takes the knot list and locates the segment by bisection.

**Kept:** uniform stations are the default; `cubic_chain(knots=...)` remains for
callers that know better. Recorded so the idea is not re-litigated from memory.

---

## 8. Cutting at the sharpest bends also lost

**Tried:** `curvature_cuts`: slide each span cut to the highest curvature within a
window, since that is where a cubic chain needs freedom.

**Result:** through the installed extension, 3 spans, best fit — even cuts 0.419 px
(freehand) and 0.890 px (wild); curvature cuts 0.632 px and 1.365 px. The cut makes
one stretch longer in arc length, and a longer stretch is harder for six points.

**Kept:** the option, but **even cuts are the default**; the guide says so with the
numbers. The first in-process measurement had suggested a 46 % win, which is why the
number is now taken through the extension and not through a scratch script.

---

## 9. My own record format was thrown away for the shared schema

**Found:** 2026-11-27, when the curve-lab side published
`workbench/quintic.schema.json` (`curve-lab.quintic/1`) and
`state/RESPONSIBILITIES-int.md` §7.

**What was wrong:** I had invented `curve-lab.quintic/1`-ish shapes twice — a
`control_svg_y_down` sidecar, then a `control`/`curves` variant with a Python
validator of my own. Two readers, two formats, one of them mine. That is exactly the
fault the operator's instruction ("you have to work together on a shared data
structure") was pointing at.

**Fix:** the writer emits the schema's shape (envelope, `spans[].points`, `frame`,
`joins` with residuals); the numbers I need moved to a separate `-report.json` that
is not the contract; the validator now checks the schema's required keys and
`additionalProperties` rather than inventing them. `state/QUINTIC-CONTRACT-int.md`
records my side of it.

---

## 10. The sheet file breaks its own envelope

**Found:** 2026-11-27, by the reader-side check.

`workbench/quintic-guides.json` carries three top-level keys the schema forbids:
`note`, `order` (a list of point names where the schema wants the integer 6) and
`worstApproximationError`. `tests/js/quintic-data.test.ts` passes because it checks
curves and spans, not the envelope.

**Not fixed here**, deliberately: the schema belongs to the other side, and dropping
or accepting those keys is a meaning change (a format bump), not an edit I make.
Reported in the mailbox with the exact command that shows it.

