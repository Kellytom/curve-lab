# READING-int — what a session loads, and in what order

This file **names files, their cost, and why they are loaded**. It never
summarises what they say. If a fact here disagrees with the file it points at,
the file wins and this list is wrong.

Read it at the top of every focused session. Then follow the tier the action
needs — no higher.

## Tier 0 — every fhandon, no exceptions (~750 lines)

| # | file | lines | why |
|---|---|---|---|
| 1 | `LTMemory-int.md` | 127 | the map, the invariants, what is settled and what is open |
| 2 | `next-fhandoff-int.md` | 5 | the one action; nothing else decides priority |
| 3 | `state/HANDOFF-int.md` | 846 | current truth — **read the tail (~80 lines), not the whole file** |
| 4 | `TODO.md` | 254 | the real checklist: grades, workstreams, open decisions. `workbench/todo.html` is its generated twin; load one, never both |
| 5 | `goals.md` | 240 | the long arc and the offset tiers (also Tier 1) |
| 6 | `state/ACHIEVEMENTS-int.md` | 37 | what is proved, with the command that re-derives it; stops rework |

If an action names a file, that file joins the load. Nothing else joins it.

## Tier 1 — the scope anchor

Read these when the action changes direction, adds a page or module, claims a
new result, or touches a grade. They answer *what is this project*, as opposed
to *what is the next step*.

| file | lines | answers |
|---|---|---|
| `SPEC.md` | 143 | what the deliverable is |
| `docs/PROJECT.md` | 165 | scope in and out; what is deliberately not built |
| `goals.md` | 240 | the arc: plant-forms → ornament-forms, and the offset tiers |
| `docs/PHILOSOPHY.md` | 106 | glyph, full line, sections, joints — the design rules |

**Scope in one line**, so it is never absent even when the files are not open:
exact integer and rational curves on one grid; the goal is a grammar of
plant-forms that becomes the ornament grammar, not a gallery of drawings.

## Tier 2 — by action

| the action is about | load |
|---|---|
| Pythagorean field / integer curve family | `docs/PYTHAGOREAN-FAMILIES.md`, `docs/INTEGER-CUBIC.md`, `docs/SPINE.md`, `curve_lab/pyth_triples.py`, `curve_lab/pyth_cubic.py`, `curve_lab/pyth_g2.py`, `curve_lab/spine.py` |
| offsets, rails, clearance | `docs/CLEARANCE.md`, `curve_lab/offsets.py`, `curve_lab/parallel_bezier.py`, `curve_lab/piece.py` |
| endings, terminals, flowers | `docs/JUNCTION.md`, `docs/FLOWERS-int.md`, `curve_lab/terminals.py`, `curve_lab/plant.py` |
| primal ornaments | `docs/PRIMAL.md`, `curve_lab/primal.py` |
| plant-form proof | `docs/PHILOSOPHY.md`, `curve_lab/plant.py`, `scripts/plant_forms.py` |
| the page map / breadth | `workbench/workbench.html` + `workbench/manifest.json` (365; generated — index only, do not read through) |
| source intake | `goals.md` §Source intake, `reference/manifest.json`, `docs/CORPUS.md` |
| a W-label | `state/BACKLOG-int.md` — that label only |
| what is parked | `state/BACKBURNER-int.md` |
| verification | `scripts/recheck.py`, `scripts/test.py` |
| architecture / print review | `docs/ARCHITECTURE.md`, `docs/REVIEW.md` — after the current work, not before |

## Never on a load

`docs/HANDOVER.md` (durable architecture/deploy/security only, deliberately
long), `vendor/`, `out/caps/*.svg`, `site/`, `node_modules/`, the generated
`workbench/*.html` other than the page under change, `docs/HANDOVER.html`,
`state/monitor.log`, and the `ornaments` repository except for extraction or
comparison.

## Cost rule

Tier 0 is ~750 lines and no source code. Tier 1 adds ~650 when direction is in
question. Tier 2 is capped by the action: one row of the table, not the table.

If a session finds itself loading a file outside this list, either the action
needs it — say so in `state/HANDOFF-int.md` and add the row here — or it does
not, and the load is a mistake being paid for in context.
