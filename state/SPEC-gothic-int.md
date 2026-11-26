# SPEC — the gothic desk (`/gothic/`, `/gothic/<uid>`)

**Status, 2026-11-23:** first slice, built and proved end to end; the probe record was removed.

**The operator:** "use class V and make an html page so i can see each curve that is cut; model it
on http://127.0.0.1:4321/plates with the same curves but a link to a tuner that will help us cut
the curve and save the new gothic type curve."

**The operator, after the first build:** "everything that says 'rows only, no stored path' is a
high degree parametric polynomial. it is not 'stored lines'; go deeper; find the equation in the
database." It is: the record's speed pair `speedX` / `speedY`, which the plates have always
drawn with `PLATE.spine`. The desk samples that same function (see *The points come from the
record*).

**The pages:** `app/src/pages/gothic/index.astro` (the list), `app/src/pages/gothic/[uid].astro`
(the tuner).
**The maths:** `app/src/lib/gothic.js` (pure, Node-tested); the band reuses `sides` from
`app/src/lib/class-v.js`.
**The save:** `app/src/pages/api/gothic-arch.js` → `createVariant` in `app/src/lib/desk-tune.js`.
**The script:** `app/src/scripts/gothic-tuner.js`.
**The test:** `tests/js/gothic.test.js`; the live check is `scripts/check-gothic.mjs`
(the menu moves the cut, the figure redraws, the one-arm notice, no console error).
**The check:** `app/scripts/check-pages.mjs /gothic/`.

## What it is

Class V makes a pointed arch from half a Tschirnhausen: cut the half, trim each end, mirror and
join at the tip. This desk does the same on **any mirrored stored curve**: cut the middle out
symmetrically, keep the two outer arms, and join them at the cut so the join is the apex.

- **The middle is `t = 0.5`** — the stored path's middle station. The cut is a symmetric pair:
  one step back for the first cut, the same step forward for the second.
- **The step is the share** of the half, 2–35 %, 10 % by default. Because a mirrored curve has a
  mirrored speed, equal steps in `t` are equal lengths along the curve.
- **The arch is built from one arm and its mirror**, so the two sides are equal by construction;
  the parent's measured mirror gap is printed so a parent that only nearly matches is not
  claimed as exact.
- **The points come from the record.** A path record uses its stored `path`; a rows record is
  sampled from its speed polynomials `speedX` / `speedY` with the plate's own `PLATE.spine`
  (300 stations on the index, 700 on the tuner and the save). The equation is in the record; the
  card prints the stored speed pair and the tuner prints the integrated `x(t), y(t)`. Sampled:
  exact at the stations, approximate between them.
- **A mirror is not required for the cut.** The arch is built from one arm, mirrored about the
  vertical through the cut, so the join is on the axis and the two sides are equal by
  construction. The parent's measured gap says how nearly its own other half agrees; over 0.5 %
  the gap is printed and the cut is still offered as "one arm mirrored", never hidden.
- **The cut is a pair of parameters.** The menu offers exact steps `1/40 … 1/6` each side; the
  cut is `t = 1/2 ∓ q`. The drawn cut is the nearest stored station and says so when that is not
  the request; the percent of the half is only the echo. The record carries `q`, the actual `t`
  pair and `tRequested`.
- **The figure shows both ends.** The new arch is the top panel; the original is the bottom
  panel at the same scale, with the two cut points in red, the removed middle in red, the
  middle in hollow gold, and the integer hits in gold, labelled `(x, y)`.
- **Integer hits are the house's sampled rule** (`scripts/levien_integer.py`): a station within
  0.01 of a whole-number point. The tolerance is printed in the figure; a hit is never claimed
  as exact.
- **The arch is stored upright**: the points are the parent's points, mirrored by an exact
  rational map and turned by a stored angle, so the plate draws the apex up and the feet down.
- **The record is sampled and says so.** The stored points are exact; the curve between them is
  approximate. No grid is claimed.

## The two pages

- **`/gothic/`** is **every stored curve**, not only the plates set: the same cards, the same
  measured mirror line (`vertical`, `horizontal`, `y = x`, `y = −x`) and its gap, with the
  cuttable curves first (mirror, then one arm). The default order is **name**, so the page is not
  the doubles family on every visit; `stars` and `uid` are one click away. A record with no
  points is listed and says so; its door still opens and the tuner explains why it cannot be cut.
- **A saved arch says so.** A record whose `params.cut.mode` is `gothic` carries a tag with its
  cut share and `t` pair, and `?set=gothic` narrows the list to those arches.
- **`/gothic/<uid>`** draws the parent once in the first paint, then the live arch beside the
  controls: the cut menu, the name, and one save button. The readout gives the apex angle
  (180° smooth, 0° a cusp), the width and height in model units, the feet's level, the kept share
  of the curve, and the stored turn.
- **The save is the server's.** The page posts to `/api/gothic-arch`; the record, the database
  rows, the exports and the plate all happen there, so a half-made curve is never listed. A save
  adds a curve beside its parent (`c-0002` → `c-0002a`); the parent is never changed.

## Rules, each with a check

- [x] The list is every registry curve with points, not a kept subset or a typed uid list.
      Check: the page's count equals `registry.curves.length` (394 at the block), and the first
      cards are not the doubles family with the default name order.
- [x] The points come from one place: the stored path, or the plate's own sampling of the speed
      pair. Check: the test (`c-0022` is a rows record; it samples to 700 stations, is mirrored
      and builds; `c-0273`'s path is used unchanged).
- [x] The mirror is measured, not assumed: the smallest gap of the four rational axes, as a share
      of the bounding diagonal; over 0.5 % is "not mirrored". Check: the test (a parabola, a
      `y = x` curve, an odd curve and a wonky curve).
- [x] The cut is symmetric about the stored middle and the same share each side. Check: the test
      (the two arms are equal station for station).
- [x] The arch is symmetric after the turn: mirrored x, equal y. Check: the test.
- [x] The apex is the top and the feet are level. Check: the test.
- [x] A bigger share keeps less curve and changes the apex angle. Check: the test.
- [x] A half-turn-only curve is refused *as a mirror*, and offered as one arm with the gap
      printed. Check: the test (`force`), and c-0134 (gap 9.97 %, apex 12.4° at 10 %).
- [x] The cut is printed and stored as the exact `t` pair. Check: the test (`9/20 … 11/20`).
- [x] The figure has the new arch above and the original below at one scale, with the integer
      hits. Check: the test (both titles, one SVG) and the rendered page.
- [x] The saved record is a variant: the next uid, `kind: path`, `source: cut`, no grid, the
      share and the axis in `params.cut`, and a note naming the parent. Check: the API's record.
- [x] A bad uid, a missing path and a non-mirrored parent are refused with the reason. Check:
      probes against `/api/gothic-arch`.
- [x] The save was proved end to end: c-0273 at a 20 % cut became **c-0273a** with its record,
      its plate (200) and its figure, then the probe was removed; registry and database are back
      to 393/393/393.
- [x] The page has one header, one main and no self-link. Check: `check-pages.mjs /gothic/`.

## Not done

- **No batch save.** One curve, one cut at a time; the slider is the instrument.
- **The rational-`t` control is built.** The menu offers `1/40 … 1/6` each side; the cut is
  `t = 1/2 ∓ q`, the drawn cut is the nearest stored station (stated when it differs), and the
  percent of the half is only the echo. The record carries `q`, `t` and `tRequested`.
- **No exact grid.** The parent's points are exact where stored; the arch is sampled and says so.
- **The scrollwork/special diagram plates** that need a parallel rail are a later set; they are
  not this desk (see `state/DESIGN-int.md` §A parallel rail is for a special diagram).
