# READING-int — what a session loads, and in what order

This file **names files, their cost, and why they are loaded**. It never
summarises what they say. If a fact here disagrees with the file it points at,
the file wins and this list is wrong.

Read it at the top of every focused session. Then follow the tier the action
needs — no higher.

**The opening message adds to this list; it never replaces it.** When the
operator names files to read, those join Tier 0 — they are not a shorter list.
A session that reads only the files named in the message has skipped Tier 0.

## Tier 0 — every fhandon, no exceptions (~3,670 lines, of which HANDOFF is read as a tail)

| # | file | lines | why |
|---|---|---|---|
| 1 | `LTMemory-int.md` | 171 | the map, the invariants, what is settled and what is open |
| 2 | `next-fhandoff-int.md` | 7 | the default next action, when the operator has not set one |
| 3 | `state/HANDOFF-int.md` | 2,353 | current truth — **read the tail (~80 lines), not the whole file** |
| 4 | `TODO.md` | 578 | the real checklist: grades, workstreams, open decisions. `workbench/todo.html` is its generated twin; load one, never both |
| 5 | `goals.md` | 265 | the long arc and the offset tiers (also Tier 1) |
| 6 | `state/ACHIEVEMENTS-int.md` | 91 | what is proved, with the command that re-derives it; stops rework |
| 7 | `state/DESIGN-int.md` | 354 | decisions already taken on controls, pages and naming, and why; stops the same argument twice |
| 8 | `state/REGRESSIONS-int.md` | 69 | fixed faults and the test that guards each; read before changing a control, run before a handoff |

If an action names a file, that file joins the load. Nothing else joins it.

## Tier 1 — the scope anchor

Read these when the action changes direction, adds a page or module, claims a
new result, or touches a grade. They answer *what is this project*, as opposed
to *what is the next step*.

| file | lines | answers |
|---|---|---|
| `SPEC.md` | 148 | what the deliverable is |
| `docs/PROJECT.md` | 165 | scope in and out; what is deliberately not built |
| `goals.md` | 265 | the arc: plant-forms → ornament-forms, and the offset tiers |
| `docs/PHILOSOPHY.md` | 192 | glyph, full line, sections, joints — the design rules |

**Scope in one line**, so it is never absent even when the files are not open:
exact integer and rational curves on one grid; the goal is a grammar of
plant-forms that becomes the ornament grammar, not a gallery of drawings.

## Tier 2 — by action

| the action is about | load |
|---|---|
| Pythagorean field / integer cubic and G2 | `docs/PYTHAGOREAN-FAMILIES.md`, `docs/INTEGER-CUBIC.md`, `curve_lab/pyth_triples.py`, `curve_lab/pyth_cubic.py`, `curve_lab/pyth_g2.py` |
| the exact spine / pythagorean-spiral | `docs/SPINE.md`, `pythagorean-spiral/docs/AUDIT.md`, `pythagorean-spiral/pythagorean_spiral/{spiral,triples,closure,design}.py`, `curve_lab/spine.py` |
| sequence curves | `scripts/sequence_curves.py`, `tests/test_sequence_curves.py` |
| the showcase / a catalogue page | `scripts/showcase.py`, `scripts/showcase_notes.py`, `scripts/showcase_catalogue.py`, `scripts/curve_morphs.py`, `scripts/stem_variants.py`, `scripts/generators.py` (the `NAMED` table), `tests/test_exploration_pages.py`, `tests/test_curve_census.py` |
| the fleur grammar / W04 sets | `curve_lab/grammar.py`, `curve_lab/fleur_sets.py`, `scripts/fleur_grammar.py`, `scripts/fleur_sets.py`, `tests/test_fleur_grammar.py`, `tests/test_fleur_sets.py` |
| the integer cubic catalogue / offset | `scripts/integer_cubic_catalogue.py`, `scripts/integer_cubic_offset.py`, `tests/test_pyth_cubic_catalogue.py`, `tests/test_integer_cubic_offset.py` |
| an ornament proof | `scripts/plant_forms.py`, `scripts/euler_sections.py`, `scripts/{fleur,volute,cruciform}_proof.py`, `scripts/ending_fit.py`, `scripts/modulated_width_proof.py`, `tests/test_{fleur,volute,cruciform}_proof.py`, `tests/test_ending_fit.py`, `tests/test_modulated_width_proof.py` |
| offsets, rails, clearance | `docs/CLEARANCE.md`, `curve_lab/offsets.py`, `curve_lab/parallel_bezier.py`, `curve_lab/piece.py` |
| endings, terminals, flowers | `docs/JUNCTION.md`, `docs/FLOWERS-int.md`, `curve_lab/terminals.py`, `curve_lab/plant.py` |
| primal ornaments | `docs/PRIMAL.md`, `curve_lab/primal.py` |
| plant-form proof | `docs/PHILOSOPHY.md`, `curve_lab/plant.py`, `scripts/plant_forms.py` |
| the page map / breadth | `workbench/workbench.html` + `workbench/manifest.json` (365; generated — index only, do not read through) |
| the Pell / √2 hyperbola (d as a dial) | `scripts/pell.py`, `tests/test_pell.py` |
| constant width / Reuleaux | `scripts/reuleaux.py`, `tests/test_reuleaux.py` |
| PH quintics | `scripts/ph_quintic.py`, `tests/test_ph_quintic.py` |
| the septic sandbox / degrees 6 and 7 | `scripts/ph_septic_sandbox.py`, `scripts/ph_septic_panels.js`, `scripts/septic_curves.py`, `scripts/septic_samples.py`, `scripts/ph_quintic_metrics.py`, `tests/test_ph_septic_sandbox.py`, `scripts/check-ph-page.mjs`, `workbench/septic-samples.json`, `workbench/septic-curves.json` |
| PH families (all rungs) | `workbench/ph-families.html`, `scripts/ph_families.py`, `docs/PH-INTEGER.md` |
| the eleventh-power sandbox / the degree ladder | `scripts/ph_nth_sandbox.py`, `scripts/ph_nth_panels.js`, `scripts/ph_math.js`, `scripts/ph_quintic_metrics.py`, `tests/test_ph_nth_sandbox.py`, `scripts/check-nth-page.mjs`, `workbench/ph-nth-sandbox.html` |
| a curve's folder and its figure | `curves/README.md`, `scripts/curve_files.py`, `scripts/curve_svg.py`, `scripts/curve_png.mjs`, `scripts/curve_png_all.mjs`, `workbench/figures/` |
| the gallery's clean-up and order | `scripts/moved_notes.py`, `workbench/moved-curves.json`, `workbench/curve-figures.html` |
| finding curves / the census | `scripts/family_census.py`, `scripts/related_families.py`, `scripts/import_found.py`, `workbench/family-census.json`, `scripts/direction_curves.py` |
| part 2, the fitted gallery | `scripts/ph_nth_sandbox2.py`, `scripts/ph_fit_showcase.py`, `workbench/ph-fitted-curves.json`, `tests/test_ph_nth_sandbox2.py` |
| the complementary curve and its crossings | `scripts/ph_crossings.py`, `scripts/ph_nth_panels.js` (the grey curve), `workbench/ph-nth-sandbox.html` |
| finding curves by count | `scripts/ph_find.py`, `scripts/ph_quintic_metrics.py` (`inflections`), `scripts/ph_crossings.py` |
| arches from genus 1+ curves | `scripts/arches.py`, `tests/test_arches.py` |
| Maclaurin trisectrix | `scripts/maclaurin.py`, `tests/test_maclaurin.py` |
| arches and pillars | `scripts/arches_pillars.py`, `tests/test_arches_pillars.py` |
| biarcs | `scripts/biarcs.py`, `tests/test_biarcs.py` |
| qAC and discrete LAC | `scripts/qac_dlac.py`, `tests/test_qac_dlac.py` |
| the six missing families | `scripts/missing_families.py`, `tests/test_missing_families.py` |
| the discrete clothoid | `scripts/discrete_clothoid.py`, `tests/test_discrete_clothoid.py` |
| Gen-Arch / LA radials | `scripts/gen_arch.py`, `tests/test_gen_arch.py` |
| the parabola evolute / involute | `scripts/pyth_plane.py`, `tests/test_exploration_pages.py` |
| source intake | `goals.md` §Source intake, `reference/manifest.json`, `docs/CORPUS.md` |
| a W-label | `state/BACKLOG-int.md` — that label only |
| what is parked | `state/BACKBURNER-int.md` |
| unresolved curves (need a link) | `state/UNRESOLVED-int.md` |
| verification | `scripts/recheck.py`, `scripts/test.py` |
| architecture / print review | `docs/ARCHITECTURE.md`, `docs/REVIEW.md` — after the current work, not before |

## Never on a load

`docs/HANDOVER.md` (durable architecture/deploy/security only, deliberately
long), `vendor/`, `out/caps/*.svg`, `site/`, `node_modules/`, `docs/HANDOVER.html`,
`state/monitor.log`, and the `ornaments` repository except for extraction or
comparison.

Images are allowed since 2026-11-16, under 150 KB and 1000 px on the long side; check with
`sips -g pixelWidth -g pixelHeight` and downscale with `sips -Z 900` when over. The old
"engine has no image input" rule applied to large files only and is deprecated. A visual
judgement is still the operator's; a rendered check is still best verified by printed
numbers.

## Cost rule

Tier 0 is ~750 lines and no source code. Tier 1 adds ~650 when direction is in
question. Tier 2 is capped by the action: one row of the table, not the table.

If a session finds itself loading a file outside this list, either the action
needs it — say so in `state/HANDOFF-int.md` and add the row here — or it does
not, and the load is a mistake being paid for in context.
