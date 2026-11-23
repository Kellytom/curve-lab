# SPEC — the cut desk (`/cut/`, `/cut/<uid>`)

**Status, 2026-11-23:** built and used; cuts saved end to end at dot 1 of c-0274, then removed.

**The pages:** `app/src/pages/cut/index.astro` (the list), `app/src/pages/cut/[uid].astro` (one curve)
**The maths:** `app/src/lib/cut-doubles.js` (pure, node-tested)
**The save:** `app/src/pages/api/cut-double.js` → `createVariant` in `app/src/lib/desk-tune.js`
**The script:** `app/src/scripts/cut-desk.js`
**The test:** `tests/js/cut-doubles.test.mjs`; the page check is `app/scripts/check-pages.mjs /cut/`

## What it is

The operator, 2026-11-23:

> "i dont really like many of the double-wonkies because they are too anthropomorphic or
> zoomorphic. many of them i want to cut at the big blue dot."

A double-wonk is a wonk curve cut where it crosses `y = x` and mirrored back, so it carries a
seam of cusps; the plate marks each cusp with a bigger blue dot. This desk is where those dots
are cut at, one curve at a time.

## Two kinds of cut

- **At a dot (a cusp).** The cusp splits the path into two arcs; the long one is kept unless
  the short one is asked for. The dot numbers on the page are the plate's blue dots.
- **Across a line.** The red dashed line is horizontal through the middle of the curve as the
  plate draws it. The runs on the top (or bottom) of that line are kept. A side with more than
  one run is more than one curve — c-0274's top half is two petals — so the runs are stored as
  branches, each an open curve; no run is closed into a shape and no two runs are joined by a
  chord. The line is horizontal on the plate, so the cut is made with the record turned and the
  kept runs turned back to the record's frame.

## The rule

- **A cusp is the plate's own rule**, on the source stations: the turn between the station
  before and after is over 165°. The desk and the plate must agree — the desk imports the same
  function the figure work does, and a test pins it.
- **A cusp splits the path into two arcs.** The long arc is the figure; the short one is the
  lobe the cusp closes. A cut keeps one and drops the other.
- **The desk turns the record as its plate does.** `turnPoints` is the plate's own turn, and a
  test compares the two; a desk that drew the stored points unturned showed c-0274 at 45° off
  the plate (operator, 2026-11-23). The dots are turned with the curve.
- **The parent is never changed.** A cut is a new record with the next uid beside its parent
  (`c-0288` → `c-0288a`), written by the tuning desk's own writer, so it lands on `/plates`
  beside its parent with its plate rendered.
- **The cut is sampled and says so:** the record's `kind` is `path`, its `source` is `cut`, its
  conversion says the points are the parent's, exact there and approximate between them, and
  its note names the parent, the cusp and the arc kept.
- **The side curves are chosen before saving.** The four values (width %, plus, minus, profile)
  are on the form; the two previews are drawn with them, and the saved record's database row
  carries them. After saving, the curve's own `/tune/<uid>` changes them.
- **The name is checked, and can be changed later.** A cut's name must be free — records,
  aliases and desk rows all count — and it is refused with the owner named, never silently
  suffixed. `/tune/<uid>` carries a rename that changes the name in the registry, the database
  rows, the exports and the figure, keeps the old name as an alias, and refuses a name already
  used (`planRename`, `POST /api/rename-curve`).
- **A zero is unset.** A parent with width, plus or minus at 0 (the note migration's
  placeholder) gives the cut the preset values, not a spine-only plate.

## The pages

- **`/cut/`** lists the records the data says are cuttable: a name beginning `double-` with
  stored points. Each card is its plate, its uid and name, and how many cusps it has; a curve
  with no cusp is listed and says so.
- **`/cut/<uid>`** draws the curve once, in the page's first paint, with the cusps numbered in
  the plate's blue and the red dashed line across its middle; the form's numbers are the
  picture's numbers. It offers the dot or the line, the arc or the side, a name, and one
  button. Under it, **the cut the form chooses** is drawn with its side curves — the kept arc
  at a dot (with the units kept and dropped), or the chosen line half — so the choice is made
  from the result, not from a description. A dot choice never previews the line's halves:
  the operator, 2026-11-23: "does not cut at the dotted line. it cuts at 1 and 2 the blue
  dots, remember? algorithmically, not looking at the plot and cutting it in half."
- **The save answers before the renders.** The record, the database rows and the exports are
  written in the request; the plate and the figure render in a detached child
  (`scripts/render_saved_curve.mjs`) and land on `/plates` and `/figures` a moment later.
  Waiting for them in the request made the button say "cutting…" for minutes, which the
  operator read as no way to save (2026-11-23).
- **The save is the server's.** The page posts to `/api/cut-double`; the record write, the
  database rows, the exports and the plate all happen there, so a page that fails half way
  cannot leave a half-made curve.
- **The result is named in place:** the status line gives the new uid and name, the kept and
  dropped lengths in model units, and a link to the new plate.

## Rules with a check each

- [x] The doubles come from the data, never a typed list. Check: `tests/js/cut-doubles.test.mjs`
      (fifty or more, every name begins `double-`).
- [x] The cusps match the plate's dots. Check: the same test finds c-0288's cusps at the plate's
      165° rule.
- [x] A cut keeps an arc that meets the cusp at one end. Check: the same test.
- [x] Long and short are the two different arcs of the same dot. Check: the same test.
- [x] The two arcs add up to the path. Check: the same test.
- [x] A line cut keeps only the runs on one side, each open. Check: the same test (a diamond,
      and c-0274's two petals above and one body below).
- [x] A side with two runs is two branches, not one path. Check: the same test; a cut saved to
      the registry carries `branches` (c-0274's top half: 2 runs, 78 points).
- [x] A bad uid is refused, not written. Check: `POST /api/cut-double {"uid":"nope"}` → 404.
- [x] A cut gets the presets when the parent's values are zero, so its plate has a band.
      Verified on c-0288 → a record with width 1.5, plus 2.5, minus 0.1 and a drawn band.
- [x] The page has one header, one main and no self-link. Check: `check-pages.mjs /cut/`.

## Not done

- **No batch cut.** One curve, one dot at a time; the operator asked for a quick desk, not a
  batch tool.
- **No undo on the page.** A mistake is a record; `scripts/remove_curve_records.mjs --match
  '<name>' --write` takes it out cleanly.
- **The "too anthropomorphic" judgement is the operator's**, not a measured test: the desk
  offers the dots and shows what each cut keeps.
