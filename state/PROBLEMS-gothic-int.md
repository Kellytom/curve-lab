# PROBLEMS — the gothic desk (`/gothic/`)

Every fault this page has had: the operator's words, what was actually wrong, the fix, and the
guard. The clean description is `state/SPEC-gothic-int.md`; history never goes there.

## No faults yet — 2026-11-23

The first slice is new. The known risk to watch, recorded before it bites:

- **The symmetry test is only as good as the stored sampling.** A path sampled unevenly in `t`
  can measure a large gap on a curve that looks symmetric. If the operator sees "not mirrored"
  on a curve they know is symmetric, the measurement is wrong before the curve is — record it
  here, fix the measure, and keep the operator's curve in the set.

## 2026-11-23 — "rows only, no stored path" was the wrong reading

**The operator:** "everything that says 'rows only, no stored path' is a high degree parametric
polynomial. it is not 'stored lines'; go deeper; find the equation in the database."

**What was wrong.** The first index treated a record with no `path` as uncuttable and printed
"rows only, no stored path". Those 90 records were not missing an equation: it is in the record
as the speed polynomials `speedX` and `speedY`, and the plates have drawn them all along with
`PLATE.spine`.

**The fix.** `app/src/lib/curve-points.js` — one point source: the stored `path` if there is
one, else the plate's own `spine()` on the speed pair (300 stations to measure the mirror, 700
to cut and save). The card prints the stored speed pair; the tuner prints the integrated
`x(t), y(t)`.

**The guard.** `tests/js/gothic.test.js` — c-0022 (a rows record) samples to ≥ 500 stations, is
mirrored and builds an arch; c-0273's stored path is used unchanged. The cuttable count roughly
doubled (63 → 110 of 193 at the block).

## 2026-11-23 — the request was dropped from the saved record

**What was wrong.** The API passed `q` and `tRequested` to the variant writer, but the writer's
gothic branch copies only the fields it names, so the saved record carried `share`, `t`, `axis`
and the apex but not the requested step or the exact pair. A probe save on c-0008 showed the
gap in `params.cut`.

**The fix.** Copy `q` and `tRequested` in `planVariant`.

**The guard.** The probe record `c-0008b` was checked field by field (then removed); the API
payload and the params now carry the same four cut values. `tests/js/gothic.test.js` pins the
arch's `q` and `tRequested`.

## 2026-11-23 — the cut menu's option text was clipped

**What was wrong.** The menu labels read "1/20 each side"; the control column is narrow, so the
browser showed "1/20 ea" and the value was not readable.

**The fix.** The option text is the fraction alone; the label says "cut at ±" and the output
shows the percent echo (10 %).

**The guard.** The page check and the readout: the fraction and the percent now sit in separate
places, each short enough for its column.

## 2026-11-23 — every character rail was NaN (found by the page check)

**What was wrong.** `class-v.sides` takes its points as `{x, y}` objects; the arch stores
`[x, y]` pairs. Every rail coordinate was `NaN`, the browser logged `MNaN,NaN…`, and
`check-pages.mjs` failed `/gothic/c-0134` with a console error. The spine and the source curve
still drew, so the page looked almost right.

**The fix.** Map the arch points to `{x, y}` objects before calling `sides`; the figure's own
mapping back to pairs was already correct.

**The guard.** `tests/js/gothic.test.js` — the figure must not contain `NaN`, on the test
parabola and on c-0134 (a real, non-mirrored parent); the page check opens the route.

## 2026-11-23 — the two-panel figure's titles ran off the edge

**What was wrong.** The first two-panel figure drew one long title for each panel; at 660 px the
text ran past the right edge ("… · none", "both panels at one s…"), and the legend's last item
overlapped "integer hit".

**The fix.** Three title lines at the top (name; cut and `t` pair; apex and gap) and two at the
foot; the scale note is anchored right and shortened to "same scale". The readout's "miss by"
also lost its space and now prints "miss by 9.97 %".

**The guard.** `tests/js/gothic.test.js` pins both titles, the `t` pair and "same scale". A
clipped title is still caught by looking at the rendered figure — a test cannot see the edge.

## 2026-11-23 — the first arch was not symmetric (found by the test, before shipping)

**What was wrong.** The first build mirrored the parent's two **cut ends** and translated one arm
so the two tips met. The cut ends are each other's mirror, so they sit either side of the axis;
translating one onto the other broke the symmetry. The apex ended up off the axis, the feet at
different heights (measured: 100 % of the size on a stored curve), and the station-for-station
check failed on its first pair.

**The fix.** The class V rule: build from **one arm**, put the cut point at the origin, mirror
about the vertical through it, and turn the result 0° or 180° so the feet are below. The apex is
then on the axis by construction, the feet are level exactly, and no general angle enters the
record.

**The guard.** `tests/js/gothic.test.js` — "the arch is symmetric station for station, apex up
and feet level", on the test parabola and on five stored records; and the page prints the
measured feet level.
