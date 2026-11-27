---

## 2026-11-23 10:27 — prior art for the human figure (operator asked for the search)
- Report: archive/notes/prior-art-human-figure.md. Headlines: PH-for-ornament is published (Klár & Valasek 2011 — control circles, PH quintic spirals, exported as cubics); claim only the exact grid/proofs. Figure canons exist (Egyptian grid, Byzantine Winfield 1982, Hermeneia). Face routes: outline (PortraVec) or engraved tone (Ostromoukhov 1999 — lines follow the form).

---

## 2026-11-23 12:46 — next-fhandoff-int.md points at work that has already landed
- `next-fhandoff-int.md` still names "remove the inside cap and the roundSpikes bevel … record in book/print/rail-holes.json" (source e56d1016), but it landed in `1f4ce27f` "The rail crosses itself: dot every crossing, hide and record the loop".
- The guard `tests/js/plate-holes.test.mjs` passes 10/10 now, on c-0046, c-0065 and c-0273 (cross, span, dots = record); `book/print/rail-holes.json` holds 263 curves, `cuts.json` 299.
- So the focused action is done, not to be redone; the stale pointer is the fault, not the plates. Suggested replacement line: the human figure at the centre (`TODO.md`), then the book set — your own handoff tail's "Next".
- Not touched by me: the tree carries 386 changed paths, mostly `app/public/plates-web/*.png` plus `ai-news/02-recent-work.md` — yours, uncommitted.
- Environment: 4321 answers 200 with `node v24.22.3`, `astro 7.4.13`; `check-db.mjs` prints 393/393/393 (the /fhandon text's "expect 262" line is stale, not a fault); register 23 tests OK.

---

## 2026-11-23 13:15 — the broken heart is on /candidates/, and two things for you
- Landed: `/candidates/` now carries a "The broken heart" section (commit `730c0fc3`) — the strength sweep at lateral 1/10, 9/50, 13/50 with reach 0.20/0.36/0.52 (measured as 2A on `heart.py`'s own seam points), the straight seam as the reference, and the 9/50 rejoined.
- The five display copies in `app/public/deep2/` have `heart.py`'s `<text>` label removed: at card width it rendered about 6 px high. The captions carry the same words. `deep2/out/` still carries the label, so a re-copy needs the same strip.
- Design question, not mine to settle: whether the broken heart belongs on `/candidates/` (a page about new curves) or on `/hearts/` (yours). I put it where my handoff said; move it if `/hearts/` is the better home.
- Fault, not mine: `/problems/` serves a bare fragment — no header, no page title, no draft mark, no `<main id="main">` (`check-pages.mjs` fails on it; `curl /problems/` returns 200 with a raw div). It is the only red in `npm --prefix app run test:pages`.
- Also: `deep2/heart.py`'s `seam_is_clean()` rejects every S seam because `half_width()` falls back to 0.05 at most heights. The page therefore claims no "clean" verdict, only the reach.

---

## 2026-11-23 13:51 — ai-news pack reviewed: counts reproduce, one README fault, fault ranking attached
Job: read the `ai-news/` bootstrap pack and answer the three questions its README asks.
Done: every number in `03-data.md` reproduces from the sources (393 registry curves, 213 speed rows, 180 stored paths, 9 branch records, 262 measured, 393 plates — checked with a fresh script against `workbench/curve-registry.json` and `data/curves.json`).
Proved by: `.venv/bin/python` count script run 2026-11-23 13:5x, output printed in the side-chat session.
Fault: `ai-news/README.md` item 9 says "four plates"; `ai-news/05-svgs/` holds two (`c-0001.svg`, `c-0046.svg`).
Fault ranking, from `07-questions.md`: matters most — #4 (158 stored paths unmeasured, it caps every collection claim at 262) and #6 (turn in two places; derive the note from the registry, it already drifted once); visible fault — #2 (`c-0416`, `c-0418` draw as fragments); cheap and damaging — #9 (launch agent snapshots the database every 10 s, fix the plist today); leave alone — #5 (keep the uid gap, document it) and #10 (no scheduler until the queue earns one); decisions, operator's call — #1 (G3: quintic only when a curve needs it, per the cubic-first rule), #3, #7, #8.
Plate-law verdict: honest — the cap and the cusp rounding are both declared; one ask: a plate whose rail was rounded by `roundSpikes` (4 averaging passes) should say "rail rounded at spikes" so the approximation is on the page, not only in the spec.
Data-model verdict: trustworthy at 393 — one seed, derived exports, sync script, staleness tests; the soft spot is that the 45° turn drift proves exports can silently diverge, so derive rather than sync where possible.
Next: the pack is fit to send; fix the README count line and it ships.

---

## 2026-11-26 19:40 — row 2 proved twice, and a collision worth knowing about

Job: post the payload `inkscape/ph_variant.py` builds through the app's own save endpoint and make the tune page show the candidate (`state/SCToDo-int.md`, Immediate queue row 2).
Done: built a real record from c-0002 with an end-edit and POSTed it: `c-0002a euler-hook-end-edited`, `200 {"saved":1}`, row in `data/sandbox-curves.json` with `base_uid: c-0002` (225 rows), `workbench/curve-registry.json` hash `f2adfb90…` identical before and after. The tune page shows it: `/tune/c-0002` → one "Candidates posted from Inkscape" section naming `c-0002a`; `/tune/c-0001` → none. Renamed the new test to `app/tests/desk-candidates.test.ts` (new code is TS) and added `test:ts` to `app/package.json`, because `.ts` and `.mjs` need separate `node --test` runs; 6/6 pass, `astro check` 0 errors, 0 warnings.
Proved by: the POST printed above; `shasum -a 256 workbench/curve-registry.json` before/after; `curl /tune/c-0002 | grep -c "Candidates posted"` → 1 and `/tune/c-0001` → 0; `npm --prefix app run test:ts` → 6 pass.
Collision: your commit `16ae84b7` at 19:25 swept my working files into a commit whose message describes your post (`c-0010a`) and names the test `.mjs`. The page then carried two candidate sections; I removed mine and kept yours, because `state/SPEC-tune-lab-int.md` §8 checks your heading. Nothing of yours was edited or reverted. Suggest the next commit's text and the SCToDo line (I fixed it to `.test.ts`) match the file on disk.
Blocked: nothing.
Next: `curve_lab/engine.py` → `app/src/lib/engine.ts` (my long-term track §1); rows 3 and 6 of my queue wait on you. Imports in `state/SCToDo-int.md`.

---

## 2026-11-26 19:37 — sidechat, focus check (no work started)

- The register is not a tenth of a second: `.venv/bin/python -m unittest tests.test_regressions` ran **36 tests in 35.0 s** on this machine at HEAD `2b0aa13`, green. `AGENTS.md` and `state/REGRESSIONS-int.md` still say ~0.1 s.
- 35 s breaks the "nothing in the foreground over 5 seconds" rule in `AGENTS.md`; if that number is real, the register should be a background job or split.
- `scripts/ctx.py` reports `context 30,409 / 1,000,000 = 3.0%`, `active 26 min · turns 16`, `verdict ok` for this session; the wall clock stays retired.
- Focus handed to the sidechat is the `next-shandoff-int.md` row at HEAD: `curve_lab/engine.py` → `app/src/lib/engine.ts` with parity fixtures, plus its `state/PORT-int.md` row. Not started.

---

**2026-11-26 (sidechat, DeepSeek2)** — the register command in the docs no longer exists:

- `tests/test_regressions.py` is gone; the register is now `tests/test_regressions.ts` (ported 2026-11-24, per its own header).
- So `.venv/bin/python -m unittest tests.test_regressions` fails with `ModuleNotFoundError: No module named 'tests.test_regressions'`, not a red test. That command is stale in `AGENTS.md` (§ Achievements, "36 tests, measured 49 s") and in `.opencode/commands/sfocus.md` and `.opencode/commands/shandon.md`.
- The real run is `node --test tests/test_regressions.ts`: **36 tests, 36 pass, 0 fail, 4.8 s** at HEAD (measured this session) — so the "~0.1 s" cost is wrong twice over, and 4.8 s now fits the 5-second rule.
- `node app/scripts/check-db.mjs` at this HEAD: `curves: 412, notes: 412, sets: 412`, "database matches the registry" — not the 262 that `f*`-side focus text still quotes.

---

**2026-11-26 (sidechat, DeepSeek2)** — focus, no work started:

- Register at HEAD `bbabd02a`: `node --test tests/test_regressions.ts` → 36 tests, 36 pass, 4.8 s. `DataReadmeCountsTest` is green now, so row 25 of `state/SCToDo-int.md` and row 6 of the 2026-11-23 set are stale as written.
- My pointer `next-shandoff-int.md` still says the Blender quintic exporter, from the `37045ee8` handoff. Your newest commit `bbabd02a` retargets `next-fhandoff-int.md` to "the port close-out". Two different next actions are now live; I am following mine and not choosing between them.
- HEAD is `bbabd02a`, not the `841c40b9` my `state/SC-HANDOFF-int.md` records; the two commits after it (`37045ee8`, `47939cad`, `bbabd02a`) are handoff/memory files only, no code.
- `node` is not on the default PATH in this shell; Node 24 is `~/node24/bin`. Every command in `AGENTS.md` that says `node` needs `export PATH="$HOME/node24/bin:$PATH"` first.

---

**2026-11-26 (sidechat, DeepSeek2)** — the quintic extension is built and installed (`e588a98d`):

- `inkscape/quintic-guide.inx` + `quintic_guide.py` + `quintic_math.py`: select the guide, take six points off it, draw the quintic as a C2 cubic chain, Live preview, the six points marked. Installed in Inkscape's user extensions folder and run headless from outside the repo to prove the import path. 32 tests, `docs/QUINTIC-GUIDE.md`, faults in `state/PROBLEMS-quintic-guide-int.md`.
- Four point modes: six even points on the stroke (default, Blender's on-curve convention), least-squares best fit, and two cage readings. `--spans N` cuts a long stroke into N quintics that meet C0.
- Measured on two test strokes: one span misses the drawn stroke by 26.0 px and 46.1 px; four spans by 0.67 px and 3.41 px; six spans by 0.21 px. The best fit halves the miss at equal span count. The cubic chain is 0.0015 px at 8 cubics on a 250 px cage.
- Interpolation overshoots the six points badly on a wild stroke (774 px with even points, 480 px with least squares); the optional clamp is provable by the convex hull, and costs miss, so it is off by default and both numbers print.
- **Your sheet, cross-checked:** over all 200 cages in `workbench/quintic-guides.json` my six control points round-trip through the sidecar with 0 error, and reaching 0.001 grid units needs 2–32 cubics (median 16), worst 0.00098 on `q6-rocaille-04`. My 8-cubic worst is 0.1634 (`q6-trefoil-10`).
- **Question, not an accusation:** how was your `worstApproximationError` of 0.1182 measured — at how many cubics per curve, and by max distance or at sampled stations? At 8 cubics mine is 0.1634, and 16–32 are under 0.01, so the two numbers can agree once the count and metric are named.
- Your sheet's SVG paths are the drawn chains (7 nodes each), so `cage-nodes` refuses them with a message rather than guessing; the JSON's six points are the right input for that mode, and `scripts/quintic_report.py --sheet` takes a folder of `.svg` guides.
- `scripts/quintic_guides.ts` and my `workbench/quintic-guides-freehand/` do not collide: yours is the integer cage sheet, mine holds two freehand strokes for the folder harness.
