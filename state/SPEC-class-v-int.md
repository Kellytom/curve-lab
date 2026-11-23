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

## Two types

- **A · slice** — the original: trim up to a quarter off both ends of the half, join at the far
  tip, mirror. Apex 43.1° at a 10 % trim.
- **B · shortcut** — cut the curve **before the middle**, drop the middle, and continue at the
  mirrored point on the other side. The cut point is the apex: the first curve stops there, the
  point is the nadir, and the second part carries on. Apex 65.1° at a 25 % cut; a cut nearer the
  start gives a sharper point.
- **The pair is shown together** below the live panel, A first and then B, and with B selected the
  A result stays as a faint dashed arch behind it.

## The four rules that keep the two sides identical

1. Cut at the curve's own middle (the stored path's middle station), never at an arbitrary place.
2. Trim the same share at both ends of the half.
3. Join on the axis, so the apex lies on the mirror line.
4. Mirror, never rotate. A rotation points both arms the same way; a mirror makes them face each
   other. With all four, left and right are equal by construction — the test checks every station.

## Rules with a check each

- [x] The arch is one stroke: no step over 5 % of its width. Check: the test.
- [x] Both side curves are continuous: no rail step over 5 % of the width. Check: the test.
- [x] The feet are at the same height, on opposite sides. Check: the test.
- [x] A different trim gives a different apex angle. Check: the test.
- [x] A and B are mirror-symmetric station for station. Check: `tests/js/class-v.test.mjs`.
- [x] The cut point sets the shortcut's angle: nearer the start is sharper. Check: the test.
- [x] The pair (A then B) is drawn under the live panel. Check: the headless capture reports two
      figures.
- [ ] A row of arches with equal spacing (the frame use) is not built yet.
