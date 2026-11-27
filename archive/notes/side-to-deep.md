---

## 2026-11-21 05:30 — the piece builder is in TypeScript: parity 4 pieces, 0 mismatches

Job (operator, direct): two more hours on the conversion track.
Done, three more commits since the last entry: **`9d089c0d`** parallel-bezier.ts (the Levien rail fitter — parity 12 runs), **`31557851`** coneTerminal (the two-arc cone, parity 12 runs), **`64af7186`** piece.ts (Trace/Group/Piece, mirrorSpans, the pre-built-spans build path — parity 4 pieces, 0 mismatches across round+point, mirror+taper, hairline, arc+butt).
Flag for you: **the Python Trace constructor forbids width on span traces** while build_piece's pre-built path and the tune desk's records use exactly that — the port follows the build_piece branch (the desk reality); the constructor's restriction is yours to reconcile.
Proved by: the four parity scripts print their counts (212 curves, 15 checks, 12 runs, 36 runs, 12 runs, 4 pieces — all zero mismatches); npm run check -> 0 errors.
Blocked: nothing
Next: model.py, then svg.py.

---

2026-11-21 · sidechat · the reduce desk's numbers were computed with a broken integral — treat every verdict it printed as void

- Fault: the reduce desk (and the old version) integrated the squared speed rows with a running sum (`out[i+1] = out[i] + c/(i+1)`) instead of the antiderivative (`out[i+1] = c/(i+1)`). The audited core `curve_lab/measure.py :: curve_polynomials` (lines 147-148) does it coefficient-wise; the desk did not.
- Second fault: the desk built `u²`, `v²`, `uv` only over the speed rows' length (12 entries for c-0260) instead of the full convolution (23 entries), cutting the position polynomial short.
- Consequence: every degree, bound and verdict the desk printed is wrong. For c-0260 the true exact curve (checked against measure.py) is position degree 23 (x) and 12 (y), bbox x ∈ [−2253.5, 0], y ∈ [−13.4, 0], size 2253.6 — not "degree 25, bound 2.9e+1 %".
- Also found: my Clenshaw evaluation of the truncated Chebyshev series fails round-trip (worst 565) while direct cosine evaluation passes (worst 1.1, the float noise floor). The page will evaluate directly, not by Clenshaw.
- Consequence for R1: the "genuinely over-degree" claims for c-0072/c-0260 came from desk/twin numbers computed on broken polynomials. The census (speed degrees, 103/110 split) is unaffected — it reads the speed rows, not the integral.
- The `../curve-lab-reduction/` worktree is gone from disk (2026-11-21). The reduction branch content is only on the git branch.
- Fix in progress on the page: exact products, coefficient-wise integration, exact drawing samples from measure.ts, direct-cos evaluation, bound ladder with the float noise floor stated in the copy.

---

2026-11-21 · sidechat · operator decision: the re-fit problem may be first, and "within the dial" is retired

- Operator: "might be the hardest problem we have, so we might have to do that first. not last." The re-fit / editing round-trip (Inkscape edit → speed rows back) is promoted from parked to a candidate for first in the queue. DeepSeek1 owns the queue order.
- Operator: "dont say 'within the dial' since it is not a real expression and gives no exact meaning." Retire the phrase on pages and in handoffs. Replace with an exact unit count: "worst miss 0.13 units" (curve units, same as the bbox size row), measured exactly, accepted or refused per curve by that number.
- The re-fit gate has two honest outcomes: miss exactly zero (speed rows reproduce the edit — accept), or the smallest provable miss stated in units with its worst station (operator accepts or refuses by the number).
- The first measurable step: the walkthrough's edited c-0059, best speed rows in exact arithmetic, minimum miss printed as a unit count. Note: speed-space reduction (R1) and the re-fit are the same maths in opposite directions — the solver is shared.
- The reduce desk rewrite is complete and verified (exact bound, parity-tested, page renders in 0.21 s, verdict for c-0260 is YES at 4 pieces, bound 0.1316 units). Screenshot taken; commit + push still pending.

---

2026-11-21 · sidechat · operator's assumed solution: restricted actions in inkex, exact reconstruction

- Operator: "use inkex and restrict the user to doing certain actions on the special grid so that any action could be reconstructed in the parametric polynomial. preferably degree 7 or lower, max 11."
- This replaces the free-form re-fit as the assumed route: no approximation step at all. The editor's vocabulary is closed — each permitted action has an exact algebraic effect on the speed rows.
- Sidechat's proposed vocabulary, all exact and degree-preserving: recipe parameter edits (degree read from the name: speed = 2·pairs + stack, position = 2·speed + 1), rational translation, mirror, p-triple rotation, rational scale, and top-coefficient (end-handle) edits.
- Mid-curve node drags are not offered; a drag snaps to the nearest legal action's predicted handle position on the grid, or is refused with the miss in units.
- inkex implementation: recipe name + parameters live in SVG metadata; the extension dialog edits parameters; path data regenerates from speed rows via the ported exact core. The SVG is a view; the recipe is the truth. Round-trip is lossless by construction.
- Degree gates: prefer position ≤ 7 (speed ≤ 3), allow position ≤ 11 (speed ≤ 5). The dialog refuses parameter sets over the gate before drawing.
- Consequence for the queue: the free-form re-fit solver drops off the critical path; the restricted editor needs only already-proven arithmetic (measure.ts, piece.ts, bezier.ts).

---

2026-11-21 · sidechat · how-to doc for DeepSeek1: side curves

- Wrote docs/SIDE-CURVES.md for DeepSeek1: what a side curve is (per-construction partner, never a parallel offset), the one character-rail law (distance = base × (1 + strength × profile)), the fold guard with the bow inside it (register 51), the direct cap (distance × peak ≤ 0.9, no halving, no second construction), the 2026-11-21 preset (width 1 %, plus 2.5, minus 0.1; zero/missing width takes it, saved width wins, stored paths included; register 52), the per-family parameter table (row/mobile/double/hybrid from scripts/side_curves.mjs), exactness rules (clean d fractions, plain numbers, no drawing-only records in the registry), the file/guard map, the canvas law, the open cases (c-0260's partner is its fix), and the operator's verbatim tie-breakers.

---

2026-11-22 · sidechat · the Inkscape round trip is done end to end, inside Inkscape's own runtime

- The hardest part — the drag→action map — works: the user drags on-curve nodes in Inkscape and saves; the receiver reads the drawn nodes from the path data, matches them against the closed vocabulary (every candidate action re-draws the chain exactly), and one action must explain ALL the moved nodes. The winner rewrites the file with the acted recipe; a far drag is refused with the miss in curve units.
- Proven through Inkscape 1.4.4 itself: the extension ran under Inkscape's bundled python + inkex (`--mode=send/receive`, needs a blank input svg when run headless), the recipe metadata survived Inkscape's own re-serialization, Inkscape's path precision drift measured 4.8e-05 curve units (the DRIFT threshold is 0.001), and three drags snapped correctly on Inkscape's own file: translate (miss 4.8e-05), end-handle at t=1 (miss 6.7e-07, u[5] rewritten to −1/10), and a two-node drag explained by one action.
- Two faults found and fixed along the way, register row 55: the translate added the offset to every position coefficient instead of the constant term only (a "translation" grew as 1+t+t²+…), and the rotation/scale were each applied twice (the placed rows already carry both — the fix was deletion). Both live in inkscape/ph_actions.py, guarded by tests/test_ph_actions.py and the strengthened translation law.
- The variant write-back: inkscape/ph_variant.py builds a registry-variant PROPOSAL (never written directly — the save endpoint owns the registry). Operator rule applied: a translation is a view, not a curve — translated placements are refused as variants; rotations/scales/mirrors/end-edits bake into the rows exactly and propose parent+letter (c-0002a, "euler-hook-end-edited"). A recipe swap maps back to the sibling already in the registry.
- Extension gotchas for the record: the .inx namespace must be http://www.inkscape.org/namespace/inkscape/extension (the /extensions/1.0 one is silently skipped); inkex 1.4 has no top-level Element export; the script must call its own Extension().run(); unknown CLI params need add_arguments entries. My copies live in the user extensions folder; re-copy inkscape/*.py *.inx after every edit.
- Tests: tests/test_ph_actions.py (14), tests/test_ph_roundtrip.py (7, with tests/fixtures/through-inkscape-c-0002.svg — Inkscape's own serialization as the fixture), tests/test_ph_variant.py (5). 26 green before the gate.

---

2026-11-22 · sidechat · the round trip is closed: the acted curve is now a sandbox candidate

- The variant proposal was POSTed through /api/sandbox-curves (HTTP 200, {"saved":1}): candidate `c-0002a` "euler-hook-end-edited" sits in the sandbox table with base_uid c-0002, the acted top coefficient (speedX[5] = −0.1), transform exact:true, origin "inkscape-roundtrip". 155 rows in the table; awaiting your promotion flow (/names or the desk) — it is a genuine product of the round trip, not a test row.
- The receive extension gained --variant (prints the proposal) and --post <url> (POSTs it to the sandbox endpoint, stdlib urllib). The full loop: registry → send (Inkscape runtime) → Inkscape load/save → drag → receive+snap → acted recipe → variant proposal → sandbox candidate.
- One design rule surfaced and applied: a translation is a view, not a curve — translated placements are refused as variants (the offset stays in the SVG); rotations, scales, mirrors and end-edits bake into the rows exactly.

---

2026-11-22 · sidechat · the speed-space re-fit exists, and the census answers R1's open question

- The next hardest thing was the speed-space re-fit — find speed rows of degree 5 (position 11, rails 9 — both gates legal) that best reproduce a curve designed at a higher degree. Built as `reduction/speed_fit.py`: a float64 Gauss-Newton search (the machinery is not the claim) whose result is quantized to exact Fractions and JUDGED exactly (L² is a rational; station misses are exact squared distances). Guarded by `tests/test_speed_fit.py` (5 tests, including the recovery-at-own-degree law on a 5e7-coefficient curve).
- The census (`reduction/speed_fit_census.py` → `workbench/speed-fit-census.json`, 110 over-ceiling curves, seconds): the FIT family reduces cleanly to speed 5 — catenary-fit **0.0000 units**, euler-fit 0.0012, gumdrop 0.0016, involute-fit 0.0408, logspiral-fit 0.3929. The wave/loop/lace families genuinely reject it (wave-1of8-4 misses 122 units, the loops 1e9+). The speed-space re-fit handles exactly the curves the sibling map was for in the fit family; the wave/loop families stay the sibling map's job.
- Register row 56: the first verdict floor was quantization in normalized coordinates (6 dp of a normalized row = 50 units on a 5e7 coefficient; the derivative is quadratic, so the own-degree recovery reported l2 2e11). Fixed to 15 places; the recovery law guards it.
- For the prefer-7 track: c-0002 (euler-hook) at speed 3 misses 0.0196 units, c-0059 (lace-1of10-3-2) at speed 3 misses 2.12 — the hook can live at position 7, the lace cannot.

---

2026-11-22 · sidechat · the speed-space candidates are in the sandbox, and the index shows the census

- Five speed-5 candidates POSTed to /api/sandbox-curves (all HTTP 200): `c-0016-s5` catenary-fit-speed5 (miss 0.000005 units of 3.291), `c-0017-s5` euler-fit (0.001182 of 0.5285), `c-0011-s5` gumdrop (0.001622 of 4.7457), `c-0015-s5` involute-fit (0.040755 of 20.1168), `c-0018-s5` logspiral-fit (0.392942 of 41.3245). Each verified by the exact core: position degree 11, rails 9 — both gates legal. Awaiting your promotion decision; the miss is recomputed on the stored six-decimal rows, so the record's number is the record's curve.
- Note on grids: the fitted rows' grids are large (1.4e16), but so are the PARENTS' (catenary-fit 9.0e16, euler-fit 1.8e17) — the fit family is decimal by construction. Snapping the rows to 1/100 would cost catenary-fit 0.0129 units and euler-fit 0.0115; not done, the six-decimal rows are the honest record.
- /reduce/ now carries the census: every over-ceiling curve with its speed → 5 miss in curve units, sorted smallest first, plain decimals (the operator's 5/25/3125 rule). Five curves can live at the ceiling by the re-fit alone; the rest say so in units. The page renders in 0.08 s; the census is a cache (missing file → dashes, never a broken page).

---

2026-11-22 · sidechat · heads-up: the reading-counts cache is burning gate runs

- Three consecutive prepush runs failed ONLY on tests.test_reading_counts, each time because state/HANDOFF-int.md and state/DESIGN-int.md grew between the refresh and the suite run (3,602→3,626 and 1,022→1,034 in one cycle). My commits refresh the counts immediately before committing, but your live edits land inside the suite's four-minute window.
- If you are mid-session on those files, running `.venv/bin/python scripts/reading_counts.py` after your last edit (or before your next push) would stop it. Nothing else in the suite is red; my blocks are green apart from this cache.

---

2026-11-23 · sidechat · the sibling finding: the stack is load-bearing; the ceiling binds the record, not the drawing

- Operator direction: tackle the sibling recipes for the ~100 wave/loop/lace curves. Built `scripts/sibling_map.py` → `workbench/sibling-map.json` (registered format): factor v back into its roots, rebuild from the same construction with a shorter ½ stack, score with the exact station miss. Also fixed the factorisation's tolerance (repeated roots come back as ±1e-4 complex pairs; a 1e-6 gate rejected every stack).
- Measured result: 72 of 110 have such a recipe, 18 match stored curves exactly (the "7 laces" note undersold it), but EVERY candidate misses by ≥ 8.5 % of the curve's size (best: wave-middle-7 at 8.54 %); typical 25–45 %. The speed-space re-fit agrees (122, 77, 10⁹ units). Two independent methods: the wave/loop/lace character exceeds the degree-11 information budget; no nearby exact curve carries it.
- The reframe: the cubic-chain export (already the round trip's drawing rule) reproduces ANY curve at any stated miss — 64 spans: 0.16–2.2 % of size; 128 spans: 0.04–0.56 %. The ceiling binds the EXACT RECORD (the PH object for glyphs/exact editing), not the picture.
- So the remaining 80 % is a POLICY decision, not a search: per family — keep the exact record at its degree (drawing-only export), replace with a designed successor at the ceiling (new curve, same character), or drop from the exact catalogue. Written up in `state/SC-SIBLING-FINDING-int.md` for your call.

---

2026-11-23 · sidechat · the operator's call: keep every curve; the near versions become NEW curves

- Operator: "i dont want to lose a curve, but at the same time if there are curves we can make that are interesting and fit in the 5 or 7 or 11 degree limits that are even 25% different, i would like those curves." So: no replacement, no deletion — the sibling recipes become additions.
- `scripts/sibling_candidates.py` proposed the 53 DISTINCT new curves from the sibling map (72 recipes, 18 already stored as themselves, deduplicated: the same v-roots under a different u are different curves and get a discriminator). All 53 POSTed to /api/sandbox-curves (200, unique names): `wave-1of2-1of2-mid` … `wave-3of4-1of2-mid`, each with its miss against its parent in curve units (0.02–30 units), degree and rails verified from the rows.
- The 18 in-catalogue siblings (e.g. wave-5of12-5 ↔ wave-5of12-3, miss 29 units) are named, not duplicated.
- Sandbox table now 213 rows: 53 sibling-map candidates + the 5 speed-fit + c-0002a round-trip variant + the pre-existing rows. All await your promotion flow; nothing enters the registry from my side.

---

2026-11-23 · sidechat · your last three commits carry three red tests (not mine)

- `tests.test_draft_label`: `workbench/side-tests.html` lacks the "draft A" label — 1 of 152 pages.
- `tests.test_hybrids`: c-0398's record has no conversion slot (plus its neighbours in the same record).
- `app` book-kept: "the manifest is exactly the kept set" is red after the data sync commits.
Each is in files you own; I have not touched them. The gate run that caught them also included my green junction port, which I am pushing separately.

---

## 2026-11-23 09:46 — the candidates page, the junction row, and the mailbox heading rule
- /candidates/ is live: the 59 new curves (53 sibling candidates, 5 speed-fit, 1 round-trip variant) with pictures, names, misses and parent links; the gallery links to it.
- Contact, fillet and junction ported to TypeScript (contact.ts, fillet.ts, junction.ts) with the ruler numbers pinned; npm 100 pass.
- Mailbox rule learned the hard way: entries must use the template heading "## YYYY-MM-DD HH:MM — subject" — with the wrong separator the parser treats the newest recognised entry as the last one and the read swallows a hundred lines (tests.test_mailbox caught it).
- Still red in your commits, untouched by me: side-tests.html lacks the draft label; c-0398 has no conversion slot; the book manifest check after the data syncs.

---

## 2026-11-23 10:23 — the operator's biggest open problem: a human figure at the centre
- Operator: "the biggest problem i have right now is that all the curves are good so far, but i need a human face or figure or statue or something symbolizing human form in the center. it would be the Blessed Virgin or Christ, or maybe the sacred heart and the immaculate heart."
- Logged in TODO.md with the honest framing: the first representational problem; fitted spans on the same grid from a measured public-domain reference; the test is whether the figure reads as human at 300 dpi. DeepSeek1's ground — the operator may hand it over.

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
