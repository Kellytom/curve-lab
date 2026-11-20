# data/ — the visible record

SQLite is the source of truth, but a session with no database must still be able
to read the record. These files are that copy: one file per table, one object
per row, no nesting tricks. They are written by one exporter
(`scripts/export-data.mjs`) on every save and by the five-minute sync.

Read them; do not hand-edit them. An edit here is lost at the next save, because
the exporter overwrites the file from the database.

## What is deliberately not here

- `app/prisma/dev.db` — the database itself. Gitignored; it is rebuilt from
  these files and from `workbench/curve-registry.json`.
- `app/data/users.json` — the local account file. It is not pushed, by the
  operator's decision; `data/users.json` below is the readable copy of the same
  table and is also not pushed.

## The files

Every file is an object with `format`, `note`, `count` and `rows`. `rows` is an
array (or, for `jobs.json`, an object with `sessions` and `jobs`).

### `curves.json` — 272 rows — `curve-lab.data.curves/1`

One object per curve: the `Curve` row, its `Note`, its `CurveSet` and its
`CurveMetric`, with the formula. The speed rows and polyline stations come from
`workbench/curve-registry.json` (the seed), not from SQLite; the database holds
the names, the notes and the measurements.

| field | type | meaning |
|---|---|---|
| `uid` | string | the permanent id, `c-0001` upward. Never reused. |
| `name` | string | the display name. Unique. Changes go through `/names`. |
| `family` | string | the family the curve belongs to (`lace`, `amper`, `ph-symmetric`). |
| `lists` | JSON array text | which lists carry it: `found`, `finder`, … |
| `aliases` | JSON array text | former display names, so a search by the old name still finds it. |
| `starred` | boolean | kept in the lab. |
| `candidate` | boolean | found but not yet promoted. |
| `createdAt` | ISO date | when the row was made. |
| `formula.plain` | string | the curve as a polynomial: `x(t) = …, y(t) = …`. Exact fractions. |
| `formula.rational` | string | the same curve stated as a rational: every coefficient is a fraction over one integer. |
| `formula.parameter` | string | what `t` is and how the stations step. |
| `formula.use` | string | what the curve is good for: nodes, inflections, bend. |
| `formula.search` | string | one line, ASCII, built for an outside search. |
| `note` | object | the editing row: importance, rotation, pieces, perSide, borderTurn, offsets, widthPct, plus, minus, profile. |
| `set` | object | the curve set: inner curve, border curve, rotation, pieces, per side, importance. |
| `metric` | object | the measurements: grid, bend, arc, chord, inflections, crossings, meeting points, bounding box, area, curvature. |

Units: `bend` is arc over chord (dimensionless); `grid` is an integer, the exact
station step `1/grid`; `bboxW`, `bboxH`, `area`, `arc`, `chord` are in curve
units; `curvatureMedian` is dimensionless (curvature times the curve's size).

Lost without it: names, stars, notes and measurements survive only in SQLite, so
a fresh clone would show numbers with no labels.

### `stars.json` — 6 rows — `curve-lab.data.stars/1`

A star in the finder: the curve a person kept.

| field | type | meaning |
|---|---|---|
| `name` | string | the curve name or an alias at the time of the star. |
| `note` | string | why it was kept, free text. |
| `spec` | JSON text | the finder settings that produced it. |
| `createdAt` | ISO date | when. |

Lost without it: the finder forgets what was kept.

### `plate-stars.json` — 1 row — `curve-lab.data.plate-stars/1`

A starred plate in the book gallery. `id` is the plate id, `note` is free text,
`createdAt` is when. Lost without it: the book gallery loses its stars.

### `users.json` — 0 rows — `curve-lab.data.users/1`

The accounts table: `id`, `name`, `email`, `role` (`viewer`/`editor`/`owner`),
`notes`, `created`, `updated`. No password field exists. Local only: this file is
written so the table is readable, but it is not pushed.

### `sandbox-curves.json` — 1 row — `curve-lab.data.sandbox-curves/1`

Every save from the sandbox and from the hybrid desk. The save *is* the decision.

| field | type | meaning |
|---|---|---|
| `name` | string | the candidate's own name; one candidate never touches another's row. |
| `data` | JSON text | the page's record as written: settings, family, and for the hybrid desk the `decision` (`keep`, `later`, `reject`) and `crossedAt`. |
| `createdAt` | ISO date | first save. |
| `updatedAt` | ISO date | last save. The latest decision wins. |

Lost without it: every keep/later/reject decision on the hybrid desk.

### `metrics.json` — 262 rows — `curve-lab.data.metrics/1`

The measurements, one row per measured curve. Same fields as `metric` above,
plus `computedAt`. A number here is produced by `scripts/analyse_curves.py`,
never typed. Lost without it: no comparison between curves, and the pages must
re-measure.

### `jobs.json` — 3 rows (1 session, 2 jobs) — `curve-lab.data.jobs/1`

`sessions`: `id`, `role`, `model`, `state` (`idle`/`working`), `job`, `lastSeen`.
`jobs`: `id`, `owner`, `files` (JSON array of paths), `state` (`queued`,
`active`, `done`, `blocked`), `createdAt`, `updatedAt`.

An active job owns its files; a second active job naming the same file is
refused. Lost without it: nobody can tell who holds a file, and two sessions
write over each other.

### `messages.json` — 6 rows — `curve-lab.data.messages/1`

The agent bus: `id`, `fromAgent`, `toAgent`, `topic`, `body`, `createdAt`,
`ackedAt`, `attempts`. Lost without it: the bus history, but not the mailbox
(which is `archive/notes/`).

## Checking it

```sh
PATH="$HOME/node24/bin:$PATH" node scripts/export-data.mjs           # rewrite data/
PATH="$HOME/node24/bin:$PATH" node scripts/export-data.mjs --check   # fail if stale
```

`--check` refreshes first and verifies second: it rewrites every file from
SQLite, then compares what it wrote with the database. So it cannot fail
because the copy was old before the check started — the only failure it can
report is a save that landed inside the verify itself, which is worth knowing.

The rule is: whoever writes the database refreshes the copy. The save endpoints
do it (one file), the bulk writers do it (`add-registry-curves.mjs`, `jobs.mjs`,
`migrate.mjs`, `restore-db.mjs` — a full refresh after a seed or a restore), and
the five-minute sync does it. `tests/test_data_export.py` runs this check.

`schema.json` is the machine-readable dictionary: file → field → type, built
from the rows that were just written.
