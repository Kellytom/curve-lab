# SPEC — the hybrid desk (`/hybrids/`)

One page for every candidate of the hybrid family, so they can be judged, kept,
put aside or rejected — without filling the collection with rejects.

## What the page is for

The family is `x = C(t)^p`, `y = S(t)^q`, where `C(t) = (1 − t²)/(1 + t²)` and
`S(t) = 2t/(1 + t²)` are the rational circle. The middle-term polynomial `P` of
`(x + y)^n` is used in 2D only: as a tint (colour use) or as a radial scale
(radius use). The desk exists to look at all of them at once and decide.

## Words it owns

- **candidate** — one (`p`, `q`, `block`, `use`) combination, with its figure.
- **decision** — `keep`, `later` or `reject`; one per candidate, stored by name.
- **colour use** / **radius use** — the two uses of `P` (tint / scale).
- **block** — which middle terms of `(x + y)^n` are included.
- **crossing pairs** — the measure, counted as pairs, never as places.

## Layout

- The app shell: one header, one `<main id="main">`, the draft mark, the sentence
  "this page is the hybrid desk", no self-link.
- A count line: how many candidates, how many kept / later / rejected.
- A grid of cards, one per candidate, in a fixed order (colour sheet first, then
  each radius sheet, `p` then `q`).
- Each card: the figure, the id, the crossing-pair count, and three buttons.
- The formula and the station rule printed once at the foot.

## Rules, each with the check that fails without it

1. **Every candidate has a figure.** `scripts/hybrid_figures.py` writes one SVG per
   candidate into `app/public/hybrid-figures/`; `workbench/hybrids.json` lists them.
   Check: the page has one card per entry in `workbench/hybrids.json`, and every
   `<img>` answers 200.
2. **A decision is saved, not just coloured.** Pressing a button writes
   `{name, decision}` to `/api/sandbox-curves`. Check: keep one, reload, it is still
   kept.
3. **A save never erases another decision.** Each candidate is its own row, keyed by
   name. Check: decide two candidates, reload, both survive.
4. **No page errors.** Check: the browser run reports none.
5. **The numbers are exact where they exist.** The crossing count is the router's,
   written by the generator; the card prints the generator's number, it does not
   re-derive it.
6. **The drawing says what it is.** The foot states: stations are exact ratios,
   the join between them is a line, and no sin or cos is used.

## Not on this page

- No editing of `p` or `q`; the family is fixed by the generator. A kept candidate
  becomes a registry record in a separate step.
- No second store: the decisions live in the same `SandboxCurve` table the sandbox
  uses.

## Promotion — a keep becomes a record

Order: **decide → promote → name → star**.

`app/scripts/export-sandbox.mjs` writes `workbench/sandbox-curves.json` (the visible copy
of every decision). `scripts/promote_hybrids.py` turns each `keep` into a registry record:
uid, name `hybrid-<p>-<q>-<block>-<use>` (colour: `hybrid-<p>-<q>-colour`), `params`, the
`formula` object, the exact `grid`, the measures in the note, and the drawn path. Then
`app/scripts/add-registry-curves.mjs` puts it in SQLite and `node scripts/curve_pngs.mjs
--only <uid>` draws its figure.

Rules:
- a keep is promoted once; the candidate id is kept as an alias, so the desk and the record
  can always be matched;
- the record's note names the construction, the crossing pairs, the station rule and the
  grid, so it can be rebuilt without the desk;
- the guard is `tests/test_hybrids.py`: every keep in the exported decisions has a registry
  record, every candidate has a complete `formula`, and every figure is on disk.

## The record's shape — mature from the first promotion

A promoted hybrid carries the same field set as a mature curve, with placeholders at rest,
so nothing downstream has to guess what is missing:

```
rotation 0 · pieces 1 · borderUid null · perSide 9 · borderTurn 0
offsets 0 · widthPct 0 · plus 0 · minus 0 · profile null
importance 0 · starred false
params { p, q, block, use, stations, uStep, stationRule }
formula { plain, internal, rational, middle, parameter, use, search }
grid 1/G (exact) · measures in the note
```

The same fields are columns on `Note` (`formula`, `params`, `grid`, `stationRule` added
2026-11-20), so a later edit is a database edit, not a file rewrite.

**The one thing still missing for character rails.** A rail is drawn by
`plate_math.group` from `speedX`/`speedY` polynomial rows, and a hybrid is a rational
curve stored as a path. So `offsets: 1` on a hybrid has nothing to draw yet: the rail
needs a path-based construction. The placeholders are in place; the construction is
future work and will be its own spec.

## The space for the improved formula

The collection holds several algorithms today: polynomial speed rows (268 records), sampled
paths, the prime mover's walk and the hybrid rational curve. They will be re-expressed in
the rational form eventually, so **every** record carries the slot now:

```
conversion: {
  algorithm,    rows | path | prime-mover | hybrid
  status,       native | pending | converted
  target,       x = C(t)^p, y = S(t)^q  (the rational form)
  formulaNext   null until the improved formula is written
}
```

`scripts/reserve_conversion.py` added it to all 272 records (a null is a deliberate
placeholder, not missing data). The guard is
`tests/test_hybrids.py::test_every_record_reserves_the_conversion_slot`, so a new record
cannot arrive without the space.

## Deciding a card: decision, stars, name

The card carries the naming desk's three judgements, saved as one row:

- **decision** — keep / later / reject;
- **stars 1–10** — the naming desk's importance widget (`data-imp`, `.on`), not a new one;
- **name** — typed in the card, kept as `curveName` in the row (the row's key stays the
  candidate id, so a rename cannot lose the decision).

On promotion, `curveName` becomes the record's name if it is set, otherwise the generated
`hybrid-<p>-<q>-<block>-<use>`; importance becomes the record's `importance`. The guard is
`app/scripts/check-hybrids-page.mjs`: keeps, seven stars and a typed name all survive a
reload.

## The naming desk's words and its safety, both

- The three buttons are the naming desk's: **Save**, **move to notes**, **reject**. Stored as
  `saved`, `notes`, `rejected`; a promotion takes `saved`.
- **A failed read turns saving off** (`state.readOk`), so an empty card cannot overwrite a
  real row; a failed save puts the previous value back and says so.
- **A name being typed is a draft** in this browser (`hybrid-name-drafts`), restored after a
  refresh and labelled "draft, not saved". A save clears it; a draft never hides a newer save.
- **The figures load eagerly.** 343 files at about 5 KB; lazy loading left blank cards on a
  first look, which reads as "there are no images".

## One name, one curve

A chosen name (`curveName`) is unique across the desk. The endpoint refuses a duplicate
with 409 and the owner's id, and the card shows "not saved — name … is already used by …".
`promote_hybrids.py` refuses to run at all if two `saved` candidates carry the same name.
The guard is `app/scripts/check-hybrids-page.mjs`: a second curve given the first curve's
name is refused and keeps its old value.

## The rejected record

`workbench/hybrid-rejected.json` is the memory of what has been tried and rejected: id,
`p`, `q`, use, block, crossing pairs, formulas, date. **JSON only, no SQLite**, so it is
readable and travels with the repository.

- `scripts/record_rejected.py --write` merges new rejections; nothing is ever removed.
- A rejected curve that is later saved stays on the record with `reinstated: true`.
- `scripts/sync-data.sh` refreshes both visible copies before staging.
- Guard: `tests/test_hybrids.py::test_every_rejected_candidate_is_on_record`.

## The family pages, from one template

`app/src/components/HybridDesk.astro` is the desk markup, with no candidates of its own:
give it rows and it draws the cards; give it none and it renders the empty desk. Two pages
use it, and only supply rows:

- `/hybrids/` — every candidate, from `workbench/hybrids.json`;
- `/hybrids-wonk/` — the candidates whose saved name matches `wonk-<number>`, read from the
  database at request time, so a new wonk appears without a rebuild.

A second family page is a new page file and nothing else; the cards, the save path and the
stars are the same component.

## What the desk shows now

`/hybrids/` is the shortlist, not the family: the stars that are still in play.

- **Rejects are out.** A candidate on `workbench/hybrid-rejected.json` is hidden unless its
  entry is `reinstated` (starred or saved after the record was made).
- **Named families have their own page.** A candidate named `wonk-<number>` is hidden from
  the desk and appears at `/hybrids-wonk/`; the filter is the saved name, not a list.
- **Order is by stars**, highest first, so the desk reads as a ranking.

## The wonkies

`scripts/make_wonkies.py` takes every wonk (a candidate named `wonk-<n>`) and cuts its
polygon at the **45° line `y = x`**, between one pair of crossings: two complementary halves,
**NW** and **SE**, each stopping at the cut. 56 wonkies from the 28 wonks. The stations either side of a cut are exact; the cut point is a value on
the drawn line between them, and the file says so.

`/hybrids-wonkies/` lists them with the same cards, so a wonky can be starred, named, saved
or rejected. `scripts/wonky_figures.mjs` draws them with the same figure builder.

## "wonk" is a staging label, not a family

A candidate is a wonk only while its saved name matches `wonk-<number>`. Rename it and it
leaves `/hybrids-wonk/` and appears on `/hybrids/` under its new name — it has been adopted.
Nothing tags it and nothing needs tracking: the name is the state.

## A recovered wonky joins the desk

A wonky is recovered when it is **saved** or **named**. From that moment it appears on
`/hybrids/` with the other candidates and leaves `/hybrids-wonkies/`, so the pair page is a
staging list that empties as halves are adopted. Proved: saving one wonky moved the desk
46 → 47 and its page 56 → 55, and the saved card carried its name.

## The render check is gone

The doubles were marked `render correct y / n` while the join was being fixed. All 56 are
correct now and the control is removed, so the card has one set of buttons again. The rows
keep any `renderCorrect` they were given; nothing reads it.

## The transform slot

A finished hybrid is usually turned **45° or 90°** for the page, so every record carries the
turn as a matrix, reserved now and filled when it is set:

```
transform: { degrees, matrix: [[a, b], [c, d]], exact }
```

- **90°** is a quarter turn and exact: `[[0, −1], [1, 0]]`; 180° and 270° likewise.
- **45°** is display only: `cos 45° = √2/2` is irrational, so the matrix holds the two
  entries as the strings `"√2/2"` and marks `exact: false`. No figure may claim an exact
  grid after it.
- Identity is the default on all 272 records and on every promoted hybrid; the column is
  `Note.transform`.
- Guard: `tests/test_hybrids.py::test_every_record_carries_its_transform`.

## As many pieces as the line cuts

A wonk crosses `y = x` several times, so the cut gives **4, 6 or 8 pieces**, not two:
140 wonkies from the 28 wonks. Each piece stays on one side of the line, is labelled
`NW-n` (above) or `SE-n` (below), and **stops at the cut** — the ends sit on `y = x`, where
the mirror is the point itself. The double is a piece mirrored across the line.

## Solving y = x, not scanning it

The crossing is solved from the equation. With `s = sin²θ`, `y = x` is

```
(1 − s)^p = s^q        degree max(p, q), not 2p + 2q
```

and each root gives four angles; the ones where `cos^pθ` and `sin^qθ` share a sign are the
crossings. The parameter follows from `t = tan(θ/2) = sinθ / (1 + cosθ)`.

`scripts/diagonal_crossings.py` does this with a Sturm sequence and bisection, and its
`crossings_via_sin2` agrees exactly with the direct 2p+2q polynomial on every pair checked
(`(2,2)`, `(3,3)`, `(1,3)`, `(3,4)`, `(5,5)`). No polygon is walked to find a cut; the
polygon is only split at the solved values. The wonks have two crossings each, so two pieces.

## A save always says so

The page confirms every save in the card, beside the name: `saved 12:15`, `moved to notes 12:15`,
`rejected 12:15`. The border colour changes as well, but colour alone is not confirmation — a
silent save is the fault this page exists to prevent, and a person must be able to see the
database took the press.

Guard: `app/scripts/check-hybrids-page.mjs` presses Save and fails unless the card says
"saved".

## The cut, frozen — 2026-11-20

The rule the pages now follow, in four lines:

1. the crossings are **solved** (`sin²θ` reduction, Sturm + bisection), not sampled;
2. each solved crossing is **inserted into the polygon segment it belongs to** — no rounding
   to the nearest station;
3. the pieces are the contiguous runs between the inserted points, so **no piece crosses
   `y = x`** (measured: 0 of 68);
4. a piece under 20 stations is dropped as a sliver, and a piece lying on the line is the cut
   itself, not a figure.

A curve that passes through the origin crosses `y = x` there too, so some wonks give 3–5
pieces instead of 2. The count per wonk is in the table below; that is geometry, not a fault.

| wonk | p, q | block | crossings | pieces |
|---|---|---|---|---|
| 1–16 | 1,3 … 7,1 | cubic, quintic-central, quintic-all-four | 4 | 2 |
| 17 | 1,3 | cubic + quintic | 6 | 3 |
| 18–19 | 1,5 / 1,7 | cubic + quintic | 4 | 2 |
| 20–22 | 3,1 / 5,1 / 7,1 | cubic + quintic | 6 or 4 | 4 or 2 |
| 23–28 | 1,3 … 7,1 | every term | 8 | 2–5 |

Proved by `.venv/bin/python scripts/make_wonkies.py` printing the roots, and by the check in
`app/scripts/check-hybrids-page.mjs`.

## The 45° preset on every double

Every double is displayed rotated **45°**, so each carries the matrix in its record:

```
transform: { degrees: 45, matrix: [["√2/2", "-√2/2"], ["√2/2", "√2/2"]], exact: false }
```

`exact: false` is the honest part: `cos 45° = √2/2` is irrational, so the turn is a display
transform and no figure may claim an exact grid after it. The 56 doubles in the data and in
the database carry it; **the drawings are not turned yet** — that waits on a clean formula.

**Next, and deliberate:** a clean rotated formula, for example delaying the cosine by half a
period so the turn is written into the parametric form (`x = C(t)`, `y = S(t − 1/2)`) instead
of applied afterwards. That is where the 45° becomes arithmetic, not a matrix.

## Mirror doubles from the desk

A tiny **⇋** beside the id makes a mirror double of that curve: the curve is mirrored across
the `y` axis and the two copies are joined at their ends with straight segments, then the
double is saved as `mirror-<id>` and sits **directly after** the curve it mirrors.

- The joins are measured and stored (`construction.joins`, `construction.maxJoin`); a double
  whose joins are long is honest about it rather than drawn as if it closed.
- The note reads `DW: <parent> mirrored across the y axis; the two copies meet at straight
  joins of …`.
- The card carries the same controls (Save, move to notes, reject, stars, name, turn), so a
  mirror can be rejected like anything else.
- Guard: the page check exercises the desk; the mirror endpoint refuses a curve with no
  points and returns the join lengths.

## Turns on the desk

Every card has `45 · −45 · 90 · −90 · 0`. A turn is applied to the drawing and stored as
`transform: { degrees, matrix, exact }` — 90 is exact, 45 is `exact: false` because
`√2/2` is irrational.
