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

## The datasets

Rows are counted by `data_audit.py` (2026-11-17).

| file | format | kind | written by | read by |
|---|---|---|---|---|
| `family-census.json` | `curve-lab.family-census/1` | cache | `scripts/curve_files.py` | `scripts/family_census.py` |
| `flowers.json` | `curve-lab.flowers/1` | cache | `scripts/stems_print.py` | `scripts/stems_print.py` |
| `curve-registry.json` | `curve-lab.curve-registry/1` | record | `scripts/curve_registry.py` | the registry and the naming pass |
| `curve-notes.json` | `curve-lab.curve-notes/1` | record | `/api/curve-notes` | the registry build |
| `curve-notes.backup.json` | `curve-lab.curve-notes/1` | backup | `/api/curve-notes`, on every write | the naming pass after a damaged read |
| `naming-todo.json` | `curve-lab.naming-todo/1` | working | `scripts/curve_registry.py` | the naming page |
| `finder.json` | `curve-lab.finder/1` | cache | `scripts/curve_finder.py` | the Astro `/finder` page |
| `finder.backup.json` | `curve-lab.finder/1` | backup | the `/finder` page, on save | `readSaved()` repair, then the page |
| `finder-stars.json` | `curve-lab.finder-stars/1` | record | `app/src/lib/finder-stars.js` | the star list on the `/finder` page |
| `finder-stars.backup.json` | `curve-lab.finder-stars/1` | backup | the `/finder` page, on save | `readSaved()` repair, then the page |
| `found-curves.json` | `curve-lab.curves/2` | record | `scripts/real_curves.mjs` | the galleries, `ph_nth_panels.js` |
| `found-for-exp.json` | `curve-lab.curves/2` | orphan | — | — (no reader; archive when the public tree is cut) |
| `g3-catalogue-cache.json` | `curve-lab.g3-catalogue-cache/1` | cache | `scripts/g3_catalogue.py` | `scripts/g3_catalogue.py` |
| `g3-catalogue.json` | `curve-lab.g3-catalogue/1` | record | `scripts/g3_catalogue.py` | `scripts/g3_gate.py`, `g3_cubic_native.py` |
| `g3-diagnostics.json` | `curve-lab.g3-diagnostics/1` | cache | `scripts/g3_handover.py` | `scripts/recheck.py` |
| `g3-handover.json` | `curve-lab.g3-handover/1` | cache | `scripts/g3_handover.py` | `scripts/g3_showcase_doc.py` |
| `manifest.json` | `curve-lab.manifest/1` | index | `scripts/hub.py` | the Astro hub, `scripts/hub.py` |
| `moved-curves.json` | `curve-lab.moved/1` | record | `scripts/moved_notes.py` | `scripts/operator_list.py` |
| `operator-list.json` | `curve-lab.operator-list/1` | record | `scripts/operator_list.py` | the lab's seed list, `tests/test_operator_list.py` |
| `ph-11th-fitted-curves.json` | `curve-lab.ph-fitted/1` | cache | `scripts/ph_11th_sandbox2.py` | part 2 of the sandbox |
| `ph-fitted-curves.json` | `curve-lab.ph-fitted/1` | cache | `scripts/ph_fit_showcase.py` | `scripts/ph_nth_sandbox2.py` |
| `ph-quintic-presets.json` | `curve-lab.ph-quintic-presets/1` | cache | `scripts/ph_quintic_gallery.py` | the quintic gallery |
| `ph-quintic-yours.json` | `curve-lab.ph-quintic-yours/1` | cache | `scripts/ph_quintic_yours.py` | the quintic gallery |
| `real-curves.json` | `real-curves/1` | record | `scripts/real_curves.mjs` | the lab, the book, `plate_math.js` |
| `root-family.json` | `curve-lab.root-family/1` | cache | `scripts/ph_root_search.py` | `scripts/ph_root_search.py` |
| `septic-curves.json` | `curve-lab.septic-curves/1` | cache | `scripts/ph_11th_sandbox.py` | the septic sandbox |
| `septic-samples.json` | `curve-lab.septic-samples/1` | cache | `scripts/septic_samples.py` | `scripts/ph_septic_sandbox.py` |
| `starred.json` | `starred/1` | runtime | `POST /api/stars` (`app/src/lib/stars.js`) | the Astro book gallery |
| `starred.backup.json` | `starred/1` | backup | `POST /api/stars`, on every write | the book gallery after a damaged read |

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
