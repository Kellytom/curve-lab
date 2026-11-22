# SCToDo-int — the sidechat's own todo list

One list, one owner (me). Each item carries a `Proves:` line so it can be judged
done without re-reading anything. Work the top row; commit per item when the
gate is green; report the hash. Long items go to the background, never waited on.

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
- Next row: `model.py` → `app/src/lib/model.ts` (Design/Segment), then
  `svg.py` — with model.py the port can hold records end to end.
  `Proves:` the parity script prints zero mismatches.
- The NURBS-analysis row: **the rails' fit source becomes the exact analytic
  normal** — `X = x·w2 − d·y′` over `w2`, built from the speed rows with no
  backend and no square root in the storage. The rails then sit as close to
  the true offset as the fit tolerance allows, and the fit's `error_max`
  numbers are measured against the exact source instead of the backend's
  offset evaluation. `Proves:` the rail fit's `error_max` against the exact
  source is at or under the current fit's, on the same curves.
- The reducer and its Python twin agree (2026-11-21): the over-ceiling curves
  genuinely carry their degree — c-0260's proven bound stays at 1.08e+2 at 64
  pieces; c-0072's explodes. The sibling map is the answer for them
  (`state/SC-NOTES-constructions.md`); the reducer serves the mild cases.
  `Proves:` the twin runs the identical algorithm in Fraction
  (`reduction/parity/reduce_reference.py`) and prints the same verdicts.
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
