# Map — the files that matter

Read `LTMemory-int.md` for the full map. This is the short one.

| path | what it is |
|---|---|
| `workbench/curve-registry.json` | the seed: every curve's uid, name, speed rows or path, turn |
| `data/curves.json` | the export: curve + note + set + metric, one row per curve |
| `data/curves-readable.json` | the same, in words: equation, measurements, turn, description |
| `app/` | the Astro app (Node 24, port 4321); `app/src/pages/`, `app/src/lib/` |
| `app/prisma/schema.prisma` | the SQLite schema: names, notes, stars, measurements |
| `curve_lab/measure.py` | **the** exact core: grid, bend, arc, inflections, closest |
| `workbench/plate_math.js` | the plate law: spine, rails, guards, the cusp rounding |
| `scripts/print_plates.mjs` | the plate SVG writer (the plate *is* the SVG) |
| `scripts/lib/plate-row.mjs` | the four plate values, and the measured 1 % preset |
| `app/src/lib/glue.js` | the glue connector: cubic with exact end slopes |
| `app/src/lib/class-v.js` | the gothic arch from a halved Tschirnhausen |
| `app/src/lib/hearts-emblems.js` | the two hearts and their letters |
| `scripts/jobq.py` | the slow-job queue (`workhorse`) |
| `scripts/said.py` | the operator's recent messages, for `/said/` |
| `state/` | the registers, the handoff, the gap report, the specs |
| `tests/` | 300+ tests; `tests/js/` holds the page maths |

## Commands that answer questions

```sh
.venv/bin/python -m unittest tests.test_regressions     # the fixed-fault register, ~5 s
.venv/bin/python scripts/test.py --fast                 # the tight loop, ~9 s
node app/scripts/check-db.mjs                           # does the database match the registry
PATH="$HOME/node24/bin:$PATH" node scripts/print_plates.mjs --svg-only   # all plates, ~20 s
PATH="$HOME/node24/bin:$PATH" node scripts/curve_gaps.mjs                # the missing-curve report
```

## The one thing to understand about the drawings

A plate is a **spine** and two **side curves**. The side curves follow one law:

    distance = min(base × (1 + strength × bow), 0.9 / κ)   on the inside of a turn
    distance =        base × (1 + strength × bow)          on the outside

The inside is the side toward the centre of curvature; only it can fold. That is per *station*,
not per side, so one rail can hug the spine while the other stays wide.
