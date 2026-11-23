# SCmemory-int — the sidechat's own memory

Written for the reset. Read it first. It is the things a fresh context cannot
know: who I am, what was decided, what broke and how it was fixed, and what is
still open. Updated whenever a session learns something the hard way; newest
entries at the bottom of each section.

## Who I am

- **DeepSeek2, the side chat.** DeepSeek1 is the controller: it decides what is
  work, reviews diffs, writes the handoff. It does not commit — **I own git**
  (since 2026-11-20): commit and push when `scripts/prepush.sh` is green, report
  the hash, never force-push `main`, never `git add -A`.
- The operator is the top authority. Their latest words override older notes,
  and their yes is needed for pushes that were not pre-approved, for internet
  beyond an approved job, and for brew (which is banned outright — see AGENTS).
- Replies: plain English, `---` between exchanges, links on their own lines at
  the end, never open a page for the operator.
- **The `s` family is mine, the `f` family is not** (operator, 2026-11-23). My
  admin is `state/SC-HANDOFF-int.md`, `next-shandoff-int.md`,
  `state/SCToDo-int.md`, `state/SCmemory-int.md`, `state/SC-READING-int.md`, and
  `/sfocus` + `/shandoff`. `next-fhandoff-int.md`, `state/HANDOFF-int.md`,
  `state/PLAN-int.md`, `state/SPRINT-int.md` and the `f*` commands are
  DeepSeek1's; I do not read them, and the repo `AGENTS.md` Tier 0 does not
  apply to me.

## The environment, as learned the hard way

- **Node 24 lives at `~/node24/bin`** — put it on PATH or `npm`, `node` and the
  page checks run the wrong version or nothing.
- **The Astro dev server dies silently** and Astro's own daemon may claim it is
  running. `npx astro dev status`, then restart with
  `npm --prefix app run dev`; a stale lock says "already running" while nothing
  listens. Verify with `curl`, not with the daemon's word.
- **No brew installs** — this Xcode is too old for bottles, so brew compiles
  from source (an `oxipng` install pulled LLVM + rust for nothing). Vendor
  prebuilt binaries or pip wheels instead. GitHub release downloads were
  refused three times in one hour (`Connection reset by peer`) — retry, or
  report the tool as missing and stop.
- **The zopflipng pip binding returns `(png_bytes, status)`**, not bytes — the
  first timing run mistook the tuple for a 2-byte PNG.
- **pngquant comes from `pip install pngquant-cli`** (binary at
  `.venv/bin/pngquant`, version 3.0.3).
- **The mailboxes are `archive/notes/deep-to-side.md` and
  `archive/notes/side-to-deep.md`** — not `docs/`, whatever a prompt says.
  Over 400 lines the mailbox check fails: `scripts/mailbox.py --rotate 8`
  moves the oldest entries to `mailbox-history.md`, losslessly.
- **`scripts/test.py`**: default loop ~91 s, `--slim` engine only, `--full`
  ~5 min with the slow page tests. Never judge green from `tail -4`; grep for
  `FAILED`.
- Two gate tripwires fire after almost any doc edit: `tests.test_llms`
  (run `scripts/llms_full.py`) and the reading-list counter (run
  `scripts/reading_counts.py`). They are not faults; they are the refreshers.

## What the project is, in one line

Exact integer and rational curves on one grid; the deliverable is a grammar of
plant-forms that becomes the ornament grammar. 397 curves, one database, one
visible record.

## Decisions made this cycle (2026-11-20)

- **The curves are Pythagorean-hodograph (PH) curves** — `speedX`/`speedY` are
  the hodograph pair. Use the field's names: PH curves, offset curves, reach,
  crunode/tacnode/acnode. The middle fold is a **high-order contact**, not a
  cusp (the speed never vanishes: `u = 2(t−½)² + ½`).
- **The visible record is `data/`** — one JSON file per table, written by
  `scripts/export-data.mjs` (and by the save endpoints); `--check` refreshes
  first and verifies second; whoever writes the database refreshes the copy.
- **Every curve carries `formula: {plain, rational, parameter, use, search}`**,
  integrated exactly from the speed rows with BigInt fractions.
- **The plates run `pngquant --colors 3`** (operator's pick after seeing the
  ladder): 31.1 MB → 5.9 MB, originals kept on disk at
  `workbench/plates-orig/` (gitignored). **Still open: the operator saw the
  greys wash out on busy plates and was re-judging the rungs on
  `http://localhost:4321/png-comparison.html`** — the honest higher rungs are
  16 colours + 90-99 (≈ same size as 3 colours) and plain 90-99.
- **`scripts/print_plates.mjs` should gain the pngquant step** so the next
  export lands compressed (flagged to DeepSeek1, not done).
- **Counters are calibrated** (`tests/test_crossing_calibration.py`): the pins
  are `c-0262` = 9, `c-0260` = 19, `c-0253` = 6, Chebyshev arc `T3×T5` = 2. Two
  older pins were replaced with the reason in TODO.md: `c-0070` reads 1 (if 11
  was right, name the curve), and `(p−1)(q−1)/2` counts the *closed* Lissajous,
  not our open arc.
- **The operator asked five test scripts out of git, then clarified** they meant
  test *PNGs*; the five are back in git (`c83fc803`) and the gitignore covers
  PNG study outputs instead (`app/public/png-study/`, `workbench/png-study/`).
- **The comparison page is `app/public/png-comparison.html`** — every rung,
  click-to-zoom. The images behind it are gitignored, served from disk.

## Standing rules, learned 2026-11-21

- **No more internet.** Pushes to GitHub are therefore on hold: a push needs
  the network. Commit locally when the gate is green and hold the push until
  the operator says internet is back.

## Open at reset time

1. **The plate quality rung** — the operator was judging wash-out curve by
   curve; the set currently in git is the 3-colour print.
2. **`app/tests/gallery.test.mjs` fails on a dirty tree** — DeepSeek1's
   in-flight plate work (AppNav, gallery.js, old_plates_export); not mine.
3. **`workbench/ph-nth-sandbox*.html` twins** — dirty, unowned.
4. **The mailbox prompt path** — the sidechat prompt once pointed at
   `docs/deep-to-side.md`, which does not exist; if it does again after reset,
   fix it to `archive/notes/`.
5. **The three slow page tests** still run only in `--full` (~60 s each) —
   a future split could cache their fixtures.

## Faults that cost time, so they cost it once

- **A study's own fidelity columns can lie** — the PNG study printed max diff 0
  where a direct recomputation said 14. The saved files were the evidence; the
  columns were thrown away. Measure from the files, not from the run's report.
- **An interrupted compression pass double-processed plates.** The fix was to
  restore the originals from the backup and re-run once from source. Any bulk
  pass over files must be restartable, or backed up first.
- **`workbench/sandbox-curves.json` had two owners and broke `/sandbox`** —
  resolved: the desk's decisions live at `data/sandbox-curves.json` (flattened
  rows, no JSON-in-JSON), the sandbox drawings at `workbench/sandbox-adders.json`.
- **A brew install is not a no-op** — it began a 30–60 minute LLVM build. Kill
  it, note AGENTS, move to a vendor binary.

## At this restart — 2026-11-21 late (read first)

The operator restarted this side chat after seeing two things on `/reduce/c-0260`: a **green
horizontal line** and numbers with **e 16**. Both are the reduction desk's (`/reduce/` is
DeepSeek2's page). What is known:

1. **The desk contradicts itself on `c-0260`.** Proven miss bound **0.00 %** of size, actual
   miss at the stations **108.82 %**, and the page says the actual is "always ≤ the bound".
   Nothing on the page is trustworthy until this is fixed. Likely causes, in order: the bound
   sums the wrong (empty or already-truncated) coefficient tail; or the coefficients and the
   measured miss are in different units/intervals (a missing scale factor). The next step is a
   test, over every desk, asserting `actual ≤ bound + 1e-9`, plus a positive finite bound when
   the tail is non-empty.
2. **The green line must be proved non-degenerate.** If the reduced y range is near constant
   while the exact is not, the fault is the evaluation (wrong parameter range, wrong Chebyshev
   nodes, x/y pieces crossed), not the drawing. Also check `c-0260`'s own shape first: its speed
   rows are `u = [1, 0, …]` with a huge `v`, and its plate is 3000×88, so the record may be a
   sliver rather than the loop its name claims.
3. **The numbers.** The desk formats every measure with `toExponential(2)` at
   `app/src/pages/reduce/[uid].astro` (the `fmt` line). The operator's taste, in their words:
   "i like numbers like 5, 25, 3125." A plain formatter is written and tested but **left
   uncommitted** for you: `app/src/lib/plain-number.js`, `app/tests/plain-number.test.mjs`
   (add it to `app/package.json`'s test list). Take it or copy its rule: an integer prints as an
   integer, a fraction in plain decimal, never an exponent.
4. **The plates changed while you were away.** DeepSeek1, at the operator's request: the preset
   is **1 % / 2.5 / 0.1** (the first two curves, `c-0001` and `c-0001a`); a placeholder zero in a
   note now falls through to the desk row (register 50); the fold guard now sees the character
   bow station by station (`c-0001` 1 % → 0.7 %, fold 0.89; register 51). Commits `468361a2` and
   `c96dda7f`. The whole set is re-rendered. Do not overwrite `scripts/lib/plate-row.mjs`,
   `workbench/plate_math.js` or their tests without reading those two registers.
5. **The split is in `state/PLAN-int.md`.** The operator, 2026-11-21: "deep1 will do the side
   curves (rails, offsets, whatever) and deep2 will continue working on nurbs and curve flow
   from here to inkscape and back." DeepSeek1 owns **all** the side curves, including the rail
   law, the fold guard, the preset, the partners, the plates and the scrollwork exceptions.
   You own the **NURBS reduction and the Inkscape round-trip**: `app/src/lib/reduction/`,
   the chebyshev/parallel-bezier code, the `/reduce/` desk. The plain-number formatter and its
   test in the tree are yours; read `docs/SIDE-CURVES.md` before touching a side curve.
6. **The gate.** `scripts/gate.py --status` (dev :4321 and built :4322, database, git),
   `--fast` 3 s, `--commit`, `--pages [--changed] [--read-only] [--url 4322]`, `--full`.
   The page checks print every failure in one pass (`app/scripts/check-all.mjs`). Use the built
   server while DeepSeek1 edits; the dev server reloads and aborts navigations.

## 2026-11-22 · the round trip and the re-fit landed (this session)

- **Inkscape 1.4.4 is installed** and drivable headless. Extensions run under its bundled
  python: `PYTHONPATH=/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions
  /Applications/Inkscape.app/Contents/Resources/bin/python3 ph_extension.py /tmp/blank.svg
  --mode=send|receive ...` (a blank input svg is required even for needs-document=false).
  Gotchas: the .inx namespace must be `http://www.inkscape.org/namespace/inkscape/extension`
  (the `/extensions/1.0` one is silently skipped); inkex 1.4 has no top-level `Element`; the
  script must call its own `Extension().run()`; unknown CLI params need `add_arguments`
  entries; re-copy `inkscape/*.py *.inx` to the user extensions folder after every edit.
- **The round trip is closed**: send (inkex) → Inkscape load/save (metadata survives; path
  drift 4.8e-05 units) → drag → receive snap (the drag→action map; one action explains all
  moved nodes; refusals in curve units) → acted recipe → variant proposal → sandbox candidate
  (`c-0002a` posted, HTTP 200). Modules: `inkscape/ph_actions.py`, `ph_svg.py`,
  `ph_handles.py`, `ph_variant.py`, `ph_extension.py`. Docs: `docs/INKSCAPE-ROUNDTRIP.md`.
- **The speed-space re-fit exists**: `reduction/speed_fit.py` (float search, exact rational
  verdict), census on `/reduce/` and `workbench/speed-fit-census.json` (registered format).
  The fit family reduces to speed 5 with essentially zero miss (catenary-fit 0.000005 units);
  the wave/loop/lace families refuse it. Five candidates POSTed to the sandbox
  (`c-0016-s5` … `c-0018-s5`), each verified position 11 / rails 9.
- **Registers 54, 55, 56** are the session's faults: the desk's running-sum integral; the
  round trip's translate-in-every-coefficient; the re-fit's verdict floor being 6-dp
  quantization. Read them before touching the desk, `ph_actions.position_of`, or
  `speed_fit.quantize`.
- **The conversion track** landed `model.ts` (6 tests) and the `svg.ts` TEXT layer (8 tests):
  `document()` stays in Python until the site emits documents. `state/PORT-int.md` carries
  the row table.
