# SCToDo-int — the sidechat's own todo list

I am **DeepSeek2, the junior developer and junior designer**. DeepSeek1, the
senior, sets direction, design and scope; every row here is work I can do inside
that scope, and a row that needs a design decision is a question for the senior,
not a choice of mine.

One list, one owner (me). Each item carries a `Proves:` line so it can be judged
done without re-reading anything. Work the top row; commit per item when the
gate is green; report the hash. Long items go to the background, never waited on.

---

## The next rows — set 2026-11-24

I am DeepSeek2 (the sidechat, `deep2`); DeepSeek1 is the senior. The session that produced the
gothic desk and the glue quintic ran as the main thread, so its detailed blocks are in the `f`
files; the rows below are the sidechat's living queue.

| # | row | `Proves:` | state |
|---|---|---|---|
| 1 | The gothic family to TypeScript (the last new JS, written before the 2026-11-24 rule): `gothic.js`, `gothic-tuner.js`, `curve-points.js`, `api/gothic-arch.js`, `tests/js/gothic.test.js` → `.ts`, imports updated. | the same 18 tests pass as `.ts`; no gothic `.js` remains; `/gothic/c-0008` opens with the menu and the six numbers; app check 0 errors | DONE 2026-11-24 |
| 2 | `scripts/root_search.py` → TS: the twin is written (`app/src/lib/root-search.ts`, `scripts/root_search.ts`); the Python stays for `adder_roots.py` until that moves. | the search's 60 rows match the current Python's numbers; the test pins the ranked rows | DONE 2026-11-24 — the stale data file is regenerated from the TS; the pinned row (grid 105, bend 1.1696, inflections 2, crossings 3, places 3, grace 0.0445) matches the current Python; 4 tests, 0.5 s |
| 3 | `scripts/coupler_curves.py` → TS: same algorithm, same JSON; check its importers first. | the TS output equals the current Python's `coupler-curves.json` for the same seed | DONE 2026-11-24 — `app/src/lib/coupler-curves.ts` + `scripts/coupler_curves.ts` + 2 tests; the data regenerated from the TS (20 rows of the 49 found). The Python stays for `tests/test_crossing_calibration.py` and had a real print bug (`KeyError: 'ground'`) fixed; its CLI now runs |
| 4 | `tests/test_regressions.py` → a TS register running the Node and browser checks. | the same test names and results run from the TS register | DONE 2026-11-24 — `tests/test_regressions.ts`: 36 rows, the names diffed identical to the Python twin, 35 pass and the one known red (`DataReadmeCountsTest`, DeepSeek1's `data/README.md` count). `scripts/test.py` runs it in `run_register()`. The Python twin stays until row 7 |
| 5 | The quintic's own loop mode (a declared shape, not a wider handle). | six G3 conditions at 1e-9 on a loop case; the sandbox draws it | after 1–2 — **needs the senior's decision: what the declared loop shape is** |
| 6 | The push. | `scripts/prepush.sh` green; the hash reported | BLOCKED: DeepSeek1's `data/README.md` (405 vs 406) and the hub stills |
| 7 | Retire the Python twin of the register: 60+ references in `AGENTS.md`, `TODO.md`, `CONTRIBUTING.md`, `llms*.txt`, four docs pages, `scripts/register.py` and six command files. | `grep -r test_regressions` names only the TS file; `scripts/test.py --fast` and every documented command still run a register; no row lost (the 36 names match) | MINE but BLOCKED on DeepSeek1: it edits their Tier-0 docs and the `f` commands |

## The set of 2026-11-23 (history; row 4 stays in the long-term track)

Five are mine and unblocked; five are the senior's or blocked, and are marked so
that nobody reads this list as a plan I am free to reorder. The first row is
`next-shandoff-int.md`.

| # | row | owner / state |
|---|---|---|
| 1 | "The broken heart" section on `/candidates/`: make `app/public/deep2/`, copy `deep2/out/heart-straight.svg` and `deep2/out/heart-S seam, lateral 0.18.svg` as slugs, render both with labels, sample strengths and a link to `deep2/heart.py`. | DONE 2026-11-23 |
| 2 | The same section's numbers: strengths read off `deep2/heart.py`, not recalled; one commit with row 1. | DONE 2026-11-23 — reach 0.20 / 0.36 / 0.52, i.e. 2A |
| 3 | Post-reset check-in: `scripts/mailbox.py --check --quiet` and `scripts/gate.py --fast`. | MINE, seconds |
| 4 | `curve_lab/engine.py` → `app/src/lib/engine.ts` (clothoid: Fresnel evaluation, Placed/Chain, parity fixtures from the Python chains). | MINE, next big row |
| 5 | `state/PORT-int.md` row for 4, and the test added to the npm list. | MINE, same commit |
| 6 | `print_plates.mjs` gains the pngquant step. | MINE only if the senior hands it over; otherwise ask |
| 7 | Which HTML pages merge — `/candidates/` is mine, `/extra-curves/` the senior's. | SENIOR decides; ask, do not choose |
| 8 | The human figure at the centre (`TODO.md`, prior art in `archive/notes/`). | SENIOR's ground; I measure if asked |
| 9 | The GLM AI-news task (`deep2/notes/glm-ai-news-task.md`). | BLOCKED: needs the model switch |
| 10 | `scripts/prepush.sh`, then the push. | BLOCKED: DeepSeek1's 386 changed plate paths must settle first |

---

## My long-term track — decided 2026-11-21

**My strongest ground, honestly assessed as GLM flash:** fast, disciplined work
with a clear spec and a test to guard it — ports, contracts, calibration,
measurement, documentation. Weaker ground: inventing new geometry from scratch;
that is DeepSeek1's lead and I am the measurement and search support around it.

So the order is:

**NURBS: parked 2026-11-21**, on the `nurbs` branch (worktree
`../curve-lab-nurbs/`, spec and analysis preserved). The operator's call after
the analysis: the deliverable is cubic Béziers for Inkscape and glyphs, so
NURBS is the indirect route — and no library serves the exact-fraction
requirement (`verb`, `geomdl`, three's `NURBSCurve` are all float64). The row
the analysis did earn is below.

### 1 · Python → TypeScript conversion (the long-term project I lead)

The site eventually runs free or low-cost on Netlify / Cloudflare Pages +
Durable Objects; no GitHub Actions runners (no monthly cost). The pattern is
already proven three times in this repo: `app/src/lib/stars.js`,
`curve-notes.ts`, and my `formula.js` + `data-export.js` — each ported with a
numeric check, not a hope.

- ~~First row: `curve_lab/measure.py` → TypeScript~~ **LANDED 2026-11-21**:
  `app/src/lib/measure.ts`, parity on 212 stored curves with **0 mismatches**
  (`app/scripts/parity-measure.mjs`), smoke test `app/tests/measure.test.mjs`
  pinned to the Python reference numbers. Three port faults caught by parity
  are recorded in `state/SC-NOTES-measure-port.md`.
- ~~`clearance.py` → `app/src/lib/clearance.ts`~~ **LANDED 2026-11-21**: flatten
  (de Casteljau), segmentDistance (Ericson), segmentHit, Ink gap/crossings, and
  the full measure() rule — parity 15 checks, 0 mismatches against the Python
  results on three real pieces (straight pair, curved pair, mirror) via
  `app/scripts/parity-clearance.mjs`.
- ~~`piece.py` → `app/src/lib/piece.ts`~~ **LANDED 2026-11-21**: Trace/Group/
  Piece with the validations, mirrorSpans, and the pre-built-spans path of
  build_piece (rails via the parallel fitter, terminals/caps, the mirror
  groups) — parity **4 pieces, 0 mismatches** (`app/scripts/parity-piece.mjs`).
  The desk-reality gap is flagged: the Python Trace forbids width on spans
  while build_piece's pre-built path and the tune desk's records use it.
- ~~`model.py` → `app/src/lib/model.ts`~~ **LANDED 2026-11-22**: Segment and
  Design with the same refusals and the same JSON shape (a Python-written
  design loads unchanged and round-trips); one widening, stated in the
  commit — `fromPieces` carries a null `kappa0` through instead of NaN.
  `app/tests/model.test.mjs` (6 tests), in the npm test list.
- ~~`svg.py` → `app/src/lib/svg.ts`~~ **PARTLY LANDED 2026-11-22**: the TEXT
  layer (svgNum, pathD, parseD, spanEval, gridStep, gridLines, bbox, slug,
  escapeXml, metadataDesign) with 8 tests; the LAYOUT builder `document()`
  stays in Python until the site emits design documents — the module header
  says so. Next conversion rows: `junction.py`, the rest of `svg.py`.
  `Proves:` node --test tests/svg.test.mjs (8/8).
- The NURBS-analysis row: **the rails' fit source becomes the exact analytic
  normal** — `X = x·w2 − d·y′` over `w2`, built from the speed rows with no
  backend and no square root in the storage. The rails then sit as close to
  the true offset as the fit tolerance allows, and the fit's `error_max`
  numbers are measured against the exact source instead of the backend's
  offset evaluation. `Proves:` the rail fit's `error_max` against the exact
  source is at or under the current fit's, on the same curves.
- The reducer's numbers are superseded (2026-11-22): the desk's integral was
  a running sum (register 54), so the old "c-0260 genuinely carries its
  degree" came from a wrong polynomial. Corrected: c-0260's drawing fits at
  4 pieces with a proven 0.1316-unit miss, and the speed-space re-fit
  (`reduction/speed_fit.py`) serves the fit family with essentially zero
  miss. The wave/loop/lace families still refuse it — the sibling map stays
  their answer. The census is on `/reduce/`.
  `Proves:` tests/test_speed_fit.py; workbench/speed-fit-census.json.
- Then `piece.py`, `junction.py`, `svg.py`, each with its own parity check.
- `state/PORT-int.md` is the boundary record — update it per row.
- `Proves:` per row: the parity script plus `npm --prefix app test`.

### 2 · Starlight documentation finishing (the parallel, smaller track)

The 39 doc pages are in place; what is missing is the finishing pass: draft-A
lines retired page by page as text finalises, the glossary pulled into one
place, `state/` knowledge (DATA-int, PRIME-MOVER, EXACT-NUMBERS) folded into
reader pages. Suited to me because it is style-disciplined plain English.
`Proves:` a docs build with zero "draft A" pages and `npm --prefix app run
check` green — but only when the operator says a page is final.

### 3 · Math & geometry analysis (support role, not lead)

**The smart answer to the degree-11 choke point landed 2026-11-21:**
`state/SC-NOTES-constructions.md` — the name IS the recipe (verified on all 31
lace curves: curve = 2·speed+1, speed = 2·pairs + stack), and the NURBS-ready
siblings are already in the catalogue: 7 of the 12 over-ceiling laces have an
in-catalogue sibling at speed degree ≤ 5; the other 5 are one recipe call away.
The task is selection, not reduction.

I am strongest at the *measurement and search* side: calibrated counters, the
family sweeps, the literature map (`RESEARCH-int.md`, the sin-cos note), and
the "what is named / what is ours" verdicts. The new-curve invention itself is
DeepSeek1's to lead; I run the sweeps, pin the numbers, and code what is
decided. `Proves:` a sweep with calibrated counters only.

### 4 · The foundations track (fits between rows)

- a `--check` (dry-run) mode for every script that writes files (TODO senior-dev
  item 4; two page breakages came from scripts writing without one);
- a smoke test per generator, one known number each (item 2);
- the "exact" wording audit against DESIGN-int §Trigonometry (item 3);
- the 77 empty cells of crossings × inflections, searched with calibrated
  counters only.

---

## Immediate queue (top first)

0. **DONE 2026-11-23 · The candidates page and the desk chrome** —
   /candidates/ lists the 59 new curves (53 siblings, 5 speed-fit, 1
   round-trip) with pictures, names, misses and parent links; /reduce/ and
   it now render inside BaseLayout and are in check-pages' route list; the
   card picture lives in app/src/lib/curve-thumbnail.ts for both pages.
   `Proves:` check-pages /reduce /candidates → ok; npm 100 pass.
   **Next big row: the clothoid engine** (`curve_lab/engine.py` → `engine.ts`
   — Fresnel-based clothoid evaluation, Placed/Chain, parity fixtures from
   the Python chains; it is what junction's spans and every grammar piece
   stand on).
0. **DONE 2026-11-23 · The sibling map and its candidates** — the operator's
   call applied: no curve lost; the 53 distinct new curves at the ceiling
   posted to the sandbox with their miss in units; the 18 in-catalogue ones
   linked from their desks; the finding written in
   `state/SC-SIBLING-FINDING-int.md` (the stack is load-bearing; the ceiling
   binds the record, not the drawing).
   `Proves:` tests/test_sibling_map.py (6); scripts/sibling_candidates.py
   prints 53 POST 200; /reduce/c-0086 links its sibling to /reduce/c-0065.
1. **DONE 2026-11-22 · The Inkscape round trip, hardest part first** — the
   drag→action map, proven through Inkscape 1.4.4's own runtime and file
   precision; the variant proposal; register rows 54/55.
   `Proves:` tests/test_ph_actions.py (14) + test_ph_roundtrip.py (7, fixture
   `tests/fixtures/through-inkscape-c-0002.svg`) + test_ph_variant.py (5),
   and the send/receive extensions registered and run under Inkscape's own
   inkex.
2. **The variant proposal meets the save endpoint** — POST the payload from
   `inkscape/ph_variant.py` through the app's save path (not the registry
   directly), and the tune page shows the candidate. `Proves:` a posted
   variant appears in `data/` with `base_uid` set and the registry untouched.
3. **The snap UI inside Inkscape** — the dialog path (send/receive) works
   headless; the live handle-drag flow needs a hand session in Inkscape to
   bind the node-edit event to `apply_snap`. `Proves:` a drag→save→receive
   loop performed in the GUI, the report printed.
4. **`print_plates.mjs` gains the pngquant step** (`--quality 90-99 --speed 1`)
   so the next export lands compressed — flagged to DeepSeek1; mine if handed
   over. `Proves:` a regenerated plate is within 2% of the swapped-in set's
   size for the same uid.
5. **Post-reset check-in:** read `state/SC-READING-int.md` tier 0, confirm the
   mailbox paths, run the gate. `Proves:` `scripts/mailbox.py --check --quiet`
   → ok, and the gate green.
6. **`gallery.test.mjs` red on the dirty tree** — DeepSeek1's in-flight work;
   mine to fix only if they hand the files over. `Proves:` the test green.

## Parked (decided, not started)

- The comparison page's floor rungs stay marked BROKEN unless the operator
  reopens the floor; the 3-colour set survives in git history (`44c2ae9b`).
- `state/PNG-COMPRESSION-int.md` carries the final numbers; no more passes
  unless the set is re-exported.

## Done this cycle (context, not a list to repeat)

Counters calibrated; the visible record (`data/`) built and guarded; the
compression studied end to end and the 90-99 set printed, swapped, committed;
the audit written (plain-English twin included); the reset files
(`SC-READING-int.md`, `SCmemory-int.md`) placed; five test guards in git.
