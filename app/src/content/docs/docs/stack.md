---
title: "The stack"
---

> **draft A** — a working draft, not a final text.

What runs where, and the versions this app actually runs. The table is generated
by `node scripts/stack_doc.mjs`; the test `tests/test_stack_doc.py` fails when
the doc and the installed packages disagree.

## What runs where

- **Node** runs the app server and the page scripts.
- **Astro** is the app: routes in `app/src/pages`, the layout in
  `app/src/layouts/BaseLayout.astro`, the shared components in
  `app/src/components`.
- **Starlight** renders this book, under `/docs`.
- **Prisma** is the data layer, over **SQLite**. The database is the record for
  names, importance, rotation, pieces and stars; the JSON files under
  `workbench/` are seed and export.
- **The exact engine is Python**, in `curve_lab/measure.py` (grid, bend, arc,
  inflections, closest) and its neighbours. The browser and the server are
  TypeScript/JavaScript; Python stays for the exact core and the generators.

## Versions

<!-- stack:start -->
| what | version |
|---|---|
| Node | 24.22.3 |
| Astro | 7.4.13 |
| Astro Node adapter | 11.1.14 |
| Starlight | 0.43.1 |
| Prisma | 6.19.3 |
| Prisma client | 6.19.3 |
| Zod | 3.25.76 |
<!-- stack:end -->

## Commands

```sh
PATH="$HOME/node24/bin:$PATH" npm --prefix app run check   # astro check + eslint
PATH="$HOME/node24/bin:$PATH" npm --prefix app test        # the app's unit tests
.venv/bin/python scripts/test.py --full                   # the Python suite
.venv/bin/python scripts/recheck.py                       # the published numbers
scripts/prepush.sh                                        # all three, before a push
```

## Regenerate this table

```sh
node scripts/stack_doc.mjs
```

`node scripts/stack_doc.mjs --check` fails when the table and the installed
packages disagree; `tests/test_stack_doc.py` runs that check in the suite.
