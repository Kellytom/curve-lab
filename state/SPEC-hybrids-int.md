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
