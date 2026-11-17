# The founder's log

Kept from the session record: what was decided, what changed, and what is still
open. Newest last. This is the founder's view, not the engineering detail; the
detail lives in `state/HANDOFF-int.md`.

## Priority tags

Every remark carries one:

- **`[now]`** — this week. It blocks the next step, and a session turns it into
  the action with a `Proves:` line.
- **`[next]`** — this month, after the `[now]` items. It goes to
  `state/PLAN-int.md`.
- **`[later]`** — after the book, or after the Inkscape transfer. It goes to
  `TODO.md`.
- A remark with no tag is read as `[next]`. The operator sets the tags; a
  session may propose one, never silently promote it.

## Current focus — 2026-11-17

- **Real curves in the lab.** `[now]` The lab still offers four sandbox cubics;
  replace them with the saved curves, normalised to the chord, and say which
  ones will not normalise. This is the live action (B7).
- **The square and rectangle lab.** `[now]` One rule: the leg bisects the 90°
  corner, so it is 45°. Counts across and down, an a/b pattern per side, and a
  central leaf of curve a below and flipped curve b above, feet forced together.
- **The attach problem is measured.** `[now]` Arch over arch prints tips
  90° / 90°; S over arch prints 90° / 0°. Match the pair before a leaf is used.
- **Squares and rectangles only.** `[now]` Pentagons and pentagrams are parked.
- **The stroke floor is 1 point** at 1–4 inches. `[now]`
- **The book gallery has the real curves.** `[now]` 27 saved curves in
  `book/index.html`, each with its character rails; pick the set, the trim size
  and the plate count from there.
- **The JS port waits.** `[later]` The exact core and the square lab are in JS;
  the rail lab, crossings and grid wait for the operator's word.

## 2026-11-16 — the saved curves, the crossings, one exact core

- **The saved-curve buttons were emptied twice.** A failed read became an empty
  list, and the next save wrote one curve over all of them. Now a failed read is
  never a write, every save keeps a backup and a mirror, and the repository
  holds a seed list. `[now]` then, done.
- **Crossings became crossing pairs.** 100 stored counts predated the dedupe;
  one number, one definition, recomputed by a script. `[now]` then, done.
- **One exact core.** The page and the record disagreed by 143× on identical
  rows (`loop-13-15-17-mid-1`: grid 36 against 5,148) because the page squared
  a large row in doubles. The exact answer moved to Python, and the page prints
  the record's number. `[now]` then, done.
- **The lesson kept:** a number no current routine produces is a fault, even
  when it looks right. `[now]` — still the rule.

## 2026-11-17 — the cone terminal (S1)

- **Two arcs, `R = 2 × half`, meeting at the centreline tip**, with a symmetric
  mode that snaps a leaned pair onto the axis and reports the shift and the
  twist. `[now]` then, done.
- **Two bugs were visible only in the drawing** (an unnormalised tip normal and
  a loop at the tip), which is why the figure is looked at. `[next]` — keep
  looking at the rendered page, not only the numbers.
- **The "engine cannot read images" rule was false** and is gone. `[later]` —
  an image may be looked at when it is under 450 KB and 3000 px.

## 2026-11-17 — the exact PH rail and the lattice (S2)

- **`integer-105` offsets exactly.** It is PH by construction, so the rail is a
  ratio of two polynomials, not a fitted cubic. The cubic fit is measured (45
  spans, 9.2e-6) and printed as a number; no cubic is drawn. `[now]` then, done.
- **The lattice is dearer than the pitch.** Pitch 105 gives two points; the
  first interior hit is the midpoint at **grid 3360** (32× the pitch). The rails
  share that grid only at **d = 41/1120**; at 3/100 the rail needs 688,800.
  `[now]` — branches on this curve have one interior station until the grid
  grows.
- **The midpoint is a station, not a mirror.** It translates to (0, 4130), but
  the curve is not symmetric and x = 0 meets it four times. `[now]` — do not
  call a station a mirror.
- **A symmetric PH candidate exists:** `u = 1`, `v = (2t − 1)²`; exact half
  turn, horizontal tangent at the midpoint, grid 15, station (0, 5), rails
  (0, 6) and (0, 4), +rail first hit grid 5. `[now]` — the operator chooses
  whether it becomes the primary curve.

## 2026-11-17 — browser JS, the tool rule, the book plates

- **The page layer moves to JS; Python is frozen for pages.** Node is for tests
  and the existing browser checks, not a build dependency. The exact core stays
  in Python where it is debugged; `ph_offset` moved because the rail page needs
  it live. Eight JS tests pin it to the Python numbers. `[next]` — the rail lab
  controls, then crossings, then grid and bend with the 1e16 guard.
- **The book plates exist.** White ground, no text on the image, tight to the
  curve, 3000 px at 300 dpi, a two-column gallery with the label outside.
  `[now]` — choose the set and the trim size.
- **The loop plate was dropped** because its rails cross the curve; the set is
  symmetric S curves whose rails stay clear. `[now]` — the minimum set is
  symmetric character curves with clean rails.
- **The balance page is queued, not built.** A *balance station* is a lattice
  point whose tangent is vertical, horizontal or a 3-4-5 direction; a *balanced
  pair* sits on either side of a declared y = k. It is balance, not symmetry.
  `[next]` — B3 in the plan.
- **The lace knots are not ribbon material:** at 3% of their size the rail
  folds (|d·κ| = 735). `[later]` — use them as spines or endings, not plates.

## 2026-11-17 — the square, the rectangle and the leaf

- **One rule: the leg bisects the corner.** A 90° corner wants a 45° leg; the
  ends stay on the edge and the box closes at the measured side. An arch joins
  continuously, an S at a right angle. `[now]` — the lab is live.
- **The frame is a rectangle now:** counts across and down (2 × 3 for a tall
  leaf), a per-side a/b pattern (`aba`), three or five curves a side for a finer
  scale. The frame and the leaf are built separately and overlaid. `[now]` —
  choose the settings for the book.
- **The leaf is curve a below, flipped curve b above, feet forced together.**
  The tip angles are printed; an arch over an arch is 90° / 90°, an S over an
  arch is 90° / 0°. That mismatch is the attach problem, measured. `[now]`
- **Squares and rectangles only** until they are right. `[now]`
- **The stroke floor is 1 point** at 1–4 inches. `[now]` — scale down without
  losing the line.
- **Other polygons are parked** by the operator: pentagons and pentagrams wait
  until the 90° case is right. `[later]`

## 2026-11-17 — the real curves reach the gallery

- **27 saved curves now fill `book/index.html`.** Each plate draws the curve's
  own character rails: the width percent, the plus/minus strength and the
  `bow`/`s`/`taper` profile from the record. 25 have rails; `involute-fit` and
  `inflect-2` are spine-only because the base offset folds even at the 0.2%
  floor. `[now]`
- **Character rails, not parallel offsets.** The operator's call: parallel
  rails are later. `[now]`
- **A central design is at least two curves joined at the legs** — mirrored
  (the leaf) or end to end (the chain, not flipped). `[now]`
- **The lab still offers the four sandbox cubics**; B7 is next. `[now]`

## Open, in priority order

- `[now]` Trim size, plate count, ink, and whether a plate carries a caption in
  the book; the export needs the print size, not only pixels.
- `[now]` The chosen plate set: 12–24 symmetric curves, each with an
  `offsetShare` that does not fold; the two-column gallery is the contact sheet.
- `[now]` The leaf pair and the frame settings (counts, pattern, leg) chosen
  from the lab, with the tip angles equal at both feet.
- `[next]` The balance-stations page (B3), exact from the derivative polynomial.
- `[next]` One plate with a declared character offset (varying width).
- `[next]` A LibreOffice contact sheet at trim size, with a PDF proof.
- `[later]` Cubic Béziers and the Inkscape transfer.
- `[later]` The rail lab in JS, crossings, then grid and bend; `measure.py`
  last; the server only if the deploy changes.
- `[later]` Other polygons (pentagon, pentagram) — parked until the 90° case is
  right.
