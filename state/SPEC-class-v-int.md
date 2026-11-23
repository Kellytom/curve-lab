# SPEC — class V, the gothic arch (`/class-v/`)

**Status, 2026-11-23:** first slice; the stroke and its side curves are continuous and tested.

**The page:** `app/src/pages/class-v.astro`
**The maths:** `app/src/lib/class-v.js`; the drawing: `app/src/scripts/class-v-sandbox.js`
**The test:** `tests/js/class-v.test.mjs`
**The check:** `app/scripts/check-pages.mjs /class-v`

## What it is

The operator: "take a simple Tschirnhausen and cut it in half. slice 1/4 or less off each
side and joint them again. this will make a design like a gothic arch, pointed at the top, with
two curved parts that join."

- **Half a Tschirnhausen:** `x = t² − 3, y = t(t² − 3)`, `t` from 0 to a length the operator
  sets (2.4 by default).
- **Trim:** up to a quarter of the half's parameter range is taken off each end; the slider is
  the share, so 10 % is a tenth at each end.
- **Mirror and join:** the half is mirrored across the vertical line through the join point.
  Joining at the **tip** gives the pointed arch; joining at the **node** gives the round head
  from the same halves.
- **Side curves:** the plate's law — outside at the ask, inside capped at 0.9/κ — with the
  distance **tapering to zero at a cusp**, so the band closes at the point instead of crossing
  it, and at the feet the caps close it too.
- **Readout:** the apex angle (180° smooth, 0° a cusp), width, height and foot height.

## Rules with a check each

- [x] The arch is one stroke: no step over 5 % of its width. Check: the test.
- [x] Both side curves are continuous: no rail step over 5 % of the width. Check: the test.
- [x] The feet are at the same height, on opposite sides. Check: the test.
- [x] A different trim gives a different apex angle. Check: the test.
- [ ] A row of arches with equal spacing (the frame use) is not built yet.
