# DATA-int — the datasets, their formats, and who touches them

Solo user, one machine. The store is files in git; there is no database and no
migration path, by the operator's decision on 2026-11-17. What makes it safe is
that every file says what it is, one loader reads it, and one check fails when
that stops being true.

## The contract

1. **Every JSON dataset under `workbench/` is an object with a `format` line**
   (`name/version`), as the first key. A list-shaped file is not allowed: give
   it `{"format": ..., "curves": [...]}` so it can grow a version later.
2. **One loader**, `curve_lab/datafile.py:load(path, expected)`. It refuses a
   missing file, bad JSON, no format, or the wrong format. Read through it, never
   with a bare `json.load`, when the caller cares whether the file is sound.
3. **One registry**, `FORMATS` in `curve_lab/datafile.py`. A dataset not in the
   table is not real: the formatter will not stamp it and the audit will not
   check it. `state/DATA-int.md` is the same list for a reader; a test keeps the
   two in step.

```sh
.venv/bin/python scripts/data_format.py --check   # is every file stamped?
.venv/bin/python scripts/data_format.py --write   # stamp what is missing (one line each)
.venv/bin/python scripts/data_audit.py            # read every file through the loader
```

`data_format.py` inserts the line after the opening brace, keeping the file's
own indentation, so the diff is one line per file. It refuses to write a file
that would not parse. Tests: `tests/test_data_audit.py`.

**When a generator rewrites a stamped file without the `format` line**, the suite
fails at `data_format.py --check`. Fix the generator (add the key first in the
document it builds) rather than re-stamping by hand, or the next run repeats it.
`ph_quintic_presets`, `ph_quintic_yours` and `septic_curves` were fixed this way
on 2026-11-17; their tests compare the written file with the generator, so they
would fail either way. The other generators are fixed on first failure.

## The visible record: `data/`

SQLite is the source of truth, but a session with no database must read the same
record. `scripts/export-data.mjs` writes one JSON file per table under `data/`,
with `data/schema.json` (field → type) and `data/manifest.json` (row count and a
hash per file). `data/README.md` is the dictionary in plain English: every field,
its meaning, its unit, who writes it, what reads it, and what is lost without it.

```sh
PATH="$HOME/node24/bin:$PATH" node scripts/export-data.mjs           # write
PATH="$HOME/node24/bin:$PATH" node scripts/export-data.mjs --check   # fail if stale
```

**The rule: whoever writes the database refreshes the copy.** The save endpoints
(`/api/curve-notes`, `/api/stars`, `/api/sandbox-curves`) call the same exporter,
so a save writes its file, and a save whose file cannot be written says so in the
response. The bulk writers do it too: `add-registry-curves.mjs` and `jobs.mjs`
write their one file, `migrate.mjs` and `restore-db.mjs` refresh everything.
`--check` refreshes first and verifies second, so it cannot fail on a copy that
was old before it started; a failure means a save landed inside the verify itself. `scripts/sync-data.sh` stages `data/` on every run.
`tests/test_data_export.py` fails when a file is stale. Every curve in
`data/curves.json` carries `formula: {plain, rational, parameter, use, search}`,
built from the stored rows (`app/src/lib/formula.js`) and checked against a
numerical integral in `app/tests/formula.test.mjs`.

## The datasets

Rows are counted by `data_audit.py` (2026-11-17).

| file | format | kind | written by | read by |
|---|---|---|---|---|
| `family-census.json` | `curve-lab.family-census/1` | cache | `scripts/curve_files.py` | `scripts/family_census.py` |
| `flowers.json` | `curve-lab.flowers/1` | cache | `scripts/stems_print.py` | `scripts/stems_print.py` |
| `curve-registry.json` | `curve-lab.curve-registry/1` | record | `scripts/curve_registry.py` | the registry and the naming pass |
| `curve-notes.json` | `curve-lab.curve-notes/1` | record | `/api/curve-notes` | the registry build |
| `curve-analysis.json` | `curve-lab.curve-analysis/1` | record | `scripts/analyse_curves.ts` | `app/scripts/load-analysis.mjs`, `scripts/similar_curves.py` |
| `curve-notes.backup.json` | `curve-lab.curve-notes/1` | backup | `/api/curve-notes`, on every write | the naming pass after a damaged read |
| `naming-todo.json` | `curve-lab.naming-todo/1` | working | `scripts/curve_registry.py` | the naming page |
| `finder.json` | `curve-lab.finder/1` | cache | `scripts/curve_finder.py` | the Astro `/finder` page |
| `finder.backup.json` | `curve-lab.finder/1` | backup | the `/finder` page, on save | `readSaved()` repair, then the page |
| `finder-stars.json` | `curve-lab.finder-stars/1` | record | `app/src/lib/finder-stars.js` | the star list on the `/finder` page |
| `finder-stars.backup.json` | `curve-lab.finder-stars/1` | backup | the `/finder` page, on save | `readSaved()` repair, then the page |
| `found-curves.json` | `curve-lab.curves/2` | record | `scripts/real_curves.mjs` | the galleries, `ph_nth_panels.js` |
| `frames.json` | `curve-lab.frames/1` | record | `scripts/frames_build.mjs` | the `/frames` page |
| `found-for-exp.json` | `curve-lab.curves/2` | orphan | — | — (no reader; archive when the public tree is cut) |
| `g3-catalogue-cache.json` | `curve-lab.g3-catalogue-cache/1` | cache | `scripts/g3_catalogue.py` | `scripts/g3_catalogue.py` |
| `g3-catalogue.json` | `curve-lab.g3-catalogue/1` | record | `scripts/g3_catalogue.py` | `scripts/g3_gate.py`, `g3_cubic_native.py` |
| `g3-diagnostics.json` | `curve-lab.g3-diagnostics/1` | cache | `scripts/g3_handover.py` | `scripts/recheck.py` |
| `g3-handover.json` | `curve-lab.g3-handover/1` | cache | `scripts/g3_handover.py` | `scripts/g3_showcase_doc.py` |
| `manifest.json` | `curve-lab.manifest/1` | index | `scripts/hub.py` | the Astro hub, `scripts/hub.py` |
| `moved-curves.json` | `curve-lab.moved/1` | record | `scripts/moved_notes.py` | `scripts/operator_list.py` |
| `near-zero.json` | `curve-lab.near-zero/1` | cache | `scripts/near_zero.py` | the near-zero report |
| `wobble.json` | `curve-lab.wobble/1` | cache | `scripts/wobble_show.py` | the `/sandbox` wobble panels |
| `mobile-curves.json` | `curve-lab.mobilecurves/1` | cache | `scripts/mobile_search.py` | the `/sandbox` mobile section |
| `coupler-curves.json` | `curve-lab.couplercurves/1` | cache | `scripts/coupler_curves.py` | the `/sandbox` coupler section |
| `bezier-knots.json` | `curve-lab.bezier-knots/1` | cache | `scripts/bezier_knots.py` | the `/sandbox` looped-Bezier section, `scripts/add_found_curves.py` |
| `emblem-stations.json` | `curve-lab.emblem-stations/1` | cache | `scripts/emblem_stations.py` | the emblem sheet: the fish, sprig, rosette and band panels, their stations and bounds |
| `nurbs-inventory.json` | `curve-lab.nurbs-inventory/1` | cache | the session's degree sweep | the NURBS-readiness analysis (`state/SC-NURBS-int.md`) |
| `speed-fit-census.json` | `curve-lab.speed-fit-census/1` | cache | `reduction/speed_fit_census.py` | the R1 decision: which over-ceiling curves a speed-space re-fit serves (the fit family) and which need a sibling |
| `sibling-map.json` | `curve-lab.sibling-map/1` | cache | `scripts/sibling_map.py` | the sibling decision: per over-ceiling curve, the same-construction recipe at the ceiling and its miss in units, or why none exists |
| `hybrids.json` | `curve-lab.hybrids/1` | cache | `scripts/hybrid_figures.py` | the `/hybrids` page, `scripts/promote_saved.py` |
| `wonkies.json` | `curve-lab.wonkies/1` | cache | `scripts/make_wonkies.py` | `/hybrids-wonk/`, `scripts/make_doubles.py` |
| `doubles.json` | `curve-lab.doubles/1` | cache | `scripts/make_doubles.py` | `/hybrids-wonk/`, `/hybrids/` |
| `hybrid-rejected.json` | `curve-lab.hybrid-rejected/1` | record | `scripts/record_rejected.py` | the rejected record; a later search must read it |
| `mirror-doubles.json` | `curve-lab.mirror-doubles/1` | cache | `scripts/make_mirror_doubles.py` | the mirror report: which ends meet |
| `hybrid-candidates.json` | `curve-lab.hybrid-candidates/1` | cache | `scripts/hybrid_candidates.mjs` | `scripts/hybrid_rank.py` |
| `hybrid-formulas.json` | `curve-lab.hybrid-formulas/1` | cache | `scripts/hybrid_formulas.py` | `scripts/hybrid_rank.py` |
| `pm-reform.json` | `curve-lab.pm-reform/1` | cache | `scripts/pm_reform_probe.py` | the `/prime-mover` page |
| `root-candidates.json` | `curve-lab.rootcandidates/1` | cache | `scripts/root_search.py` | the root search report |
| `operator-list.json` | `curve-lab.operator-list/1` | record | `scripts/operator_list.py` | the lab's seed list, `tests/test_operator_list.py` |
| `ph-11th-fitted-curves.json` | `curve-lab.ph-fitted/1` | cache | `scripts/ph_11th_sandbox2.py` | part 2 of the sandbox |
| `ph-fitted-curves.json` | `curve-lab.ph-fitted/1` | cache | `scripts/ph_fit_showcase.py` | `scripts/ph_nth_sandbox2.py` |
| `ph-quintic-presets.json` | `curve-lab.ph-quintic-presets/1` | cache | `scripts/ph_quintic_gallery.py` | the quintic gallery |
| `ph-quintic-yours.json` | `curve-lab.ph-quintic-yours/1` | cache | `scripts/ph_quintic_yours.py` | the quintic gallery |
| `real-curves.json` | `real-curves/1` | record | `scripts/real_curves.mjs` | the lab, the book, `plate_math.js` |
| `root-family.json` | `curve-lab.root-family/1` | cache | `scripts/ph_root_search.py` | `scripts/ph_root_search.py` |
The desk's decisions left this folder for `data/sandbox-curves.json` (see the
visible record above): one flat object per row, read by `promote_*.py`,
`record_rejected.py`, `make_wonkies.py` and `make_mirror_doubles.py`, written by
the save endpoint through `app/src/lib/data-export.js` and checked by
`tests/test_data_export.py`.
| `sandbox-adders.json` | `curve-lab.sandbox-adders/1` | cache | `scripts/sandbox_curves.py` | the `/sandbox` page (the adders and the quadrature drawings) |
| `sandbox-parametric.json` | `curve-lab.sandbox-parametric/1` | cache | `scripts/sandbox_parametric.py` | the parametric adder |
| `parametric-candidates.json` | `curve-lab.parametric-candidates/1` | cache | `scripts/parametric_search.py` | the complex-coefficient search history |
| `septic-curves.json` | `curve-lab.septic-curves/1` | cache | `scripts/ph_11th_sandbox.py` | the septic sandbox |
| `septic-samples.json` | `curve-lab.septic-samples/1` | cache | `scripts/septic_samples.py` | `scripts/ph_septic_sandbox.py` |
| `starred.json` | `starred/1` | runtime | `POST /api/stars` (`app/src/lib/stars.js`) | the Astro book gallery |
| `starred.backup.json` | `starred/1` | backup | `POST /api/stars`, on every write | the book gallery after a damaged read |
| `character-candidates.json` | `curve-lab.character-candidates/1` | cache | `scripts/character_search.py --write` | Fig. 5 on `/prime-mover/` |
| `character-curves.json` | `curve-lab.character/1` | cache | `scripts/character_search.py` | `workbench/character-curves.svg` |
| `circle-split.json` | `curve-lab.circle-split/1` | cache | `scripts/circle_split.py --write` | Fig. 9 on `/prime-mover/`, `tests/test_circle_split.py` |
| `lattice-mobile.json` | `curve-lab.lattice.mobile/1` | cache | `scripts/lattice_circle_mobile.py` | the mobile probe |
| `lattice-mobile-fine.json` | `curve-lab.lattice.mobile.fine/1` | cache | `scripts/lattice_circle_mobile.py` | the mobile probe |
| `lattice-mobile-quiet.json` | `curve-lab.lattice.mobile.quiet/1` | cache | `scripts/lattice_circle_mobile.py` | the mobile probe |
| `lattice-spirograph.json` | `curve-lab.lattice.spirograph/1` | cache | `scripts/lattice_spirograph.py` | the spirograph probe |
| `pm-deep.json` | `curve-lab.pm.deep/1` | cache | `scripts/pm_deep_search.py` | the prime-mover search record |
| `pm-product.json` | `curve-lab.pm.product/1` | cache | `scripts/pm_product_probe.py` | the product probe |
| `pm4-curves.json` | `curve-lab.pm4.curves/1` | cache | `scripts/pm4_search.py` | the four-fold probe |
| `prime-mover-sweep.json` | `curve-lab.prime.mover.sweep/1` | cache | `scripts/sweep_prime_mover.mjs` | the prime-mover sweep |
| `circle-plots.json` | `curve-lab.circle-plots/1` | cache | `scripts/circle_plots.py --write` | Fig. 9 on `/prime-mover/` |

**Record** means the file is the authority for a number the site shows.
**Cache** means it is derived and can be rebuilt by its script. **Runtime** means
a running page writes it. **Orphan** means nothing reads it.

## The runtime file

`workbench/starred.json` is **tracked**, seeded with an empty `starred/1` object,
and overwritten by the save endpoint when the operator stars a design. The write
is atomic and validated (`app/src/lib/stars.js`); git is the backup. Commit it
after a save if the stars matter to the next session — nothing does that
automatically, by design: the page must not need git to save.

## Known oddities, recorded not fixed

- `found-for-exp.json` (168 rows) has no writer and no reader.
- `ph-11th-fitted-curves.json` and `ph-fitted-curves.json` are the same size and
  row count under the same format; they may be duplicates. Not merged, because
  two different sandboxes name them.
- `starred.json` is empty today: no stars have been saved to disk yet.
