# SC-HANDOFF-int — the sidechat's handoff (DeepSeek2)

Written 2026-11-24 at the operator's handoff request, before a context reset.
**Identity (operator, 2026-11-24): the sidechat = `deep2` = DeepSeek2 — one agent.** DeepSeek1
is the other. The `s` files, `data/said-deep2.json` and git for this agent's own work are mine;
the `f` family (`next-fhandoff-int.md`, `state/HANDOFF-int.md`, `state/PLAN-int.md`,
`state/SPRINT-int.md`) is not.

## 1. Where the work stands

1. **The gothic desk** — `/gothic/` and `/gothic/<uid>` cut every stored curve at `t = 1/2 ∓ q`,
   show the two-panel figure and save the arch. Proof: 18 tests in `tests/js/gothic.test.ts`;
   the `/gothic/c-0008` page check; `c-0008a u-bowl-gothic` saved. **Committed and pushed in the
   handoff commit.**
2. **The glue quintic (G3)** — `/glue/` kind “quintic (G3)”; the six end conditions printed; the
   stated case at 1e-9. Proof: `tests/js/glue.test.ts` (5). **Committed and pushed.**
3. **The crossing counter in TypeScript** — `app/src/lib/crossings.ts`, brute-force parity on 50
   walks; `tests/js/crossings.test.ts` (4). **Committed and pushed.**
4. **The analysis in TypeScript** — `app/src/lib/curve-analysis.ts` + `scripts/analyse_curves.ts`;
   405/405 rows; the Python retired; `workbench/curve-analysis.json` regenerated from the TS.
   Proof: `tests/js/curve-analysis.test.ts` (2). **Committed and pushed.**
5. **root_search in TypeScript** — the twin + regenerated data; the pinned row matches the
   current Python (grid 105, bend 1.1696, inflections 2, crossings 3, places 3, grace 0.0445);
   4 tests. The Python stays for `adder_roots.py`. **Committed and pushed.**
6. **coupler_curves in TypeScript** — the twin + regenerated data; the fixed Python agrees exactly
   (49 curves); 2 tests. The Python stays for `tests/test_crossing_calibration.py`.
   **Committed and pushed.**
7. **The Tschirnhausen pieces** — six glue-ready pieces on `workbench/side-tests.html`, registered
   as Study rows (0 missing); `/gothic/` names the four source pages, `/glue/` links them.
   **Committed and pushed.**
8. **The recent-work appendix** — `/chat-display/recent-work/`. **Committed and pushed.**
9. **The identity note** — `AGENTS.md`, `state/SCmemory-int.md` and this file. **Committed.**
10. **The `f`-file blocks written earlier this session** (`state/HANDOFF-int.md`,
    `state/PLAN-int.md`, `state/REGRESSIONS-int.md`, `TODO.md`) — **uncommitted**, DeepSeek1's to
    review; the work they describe is in the commits above.

## 2. The operator's open asks, in order

1. **The TypeScript ports** — “add to your todo: transfer to typescript … and make sure you are
   writing directly in typescript not js”. Done: crossings, analysis, root_search, coupler, the
   gothic family, the glue family. **Open: the register** (542 lines). First file:
   `tests/test_regressions.py`.
2. **The gothic/glue work** — “we will use rational fraction values of the parametric” (done: the
   `t` pair); “Tschirnhausen and variations that would allow me to glue curves together” (pieces
   done; the join at the node needs the quintic's own loop mode). First file:
   `state/SPEC-glue-int.md`.
3. **“the curves we need are not stored per se …”** — extra-curves, glue, class V, side-tests
   (done as pages, links and Studies). First file: `state/SCToDo-int.md` and the pages.
4. **“keep working and dont stop to ask … i wont be here and that will block”** — the standing
   instruction; the living queue is `state/SCToDo-int.md` (the set of 2026-11-24).
5. **“make a note … sidechat = deep2 = deepseek2”** — done; the three places are named above.

## 3. Environment facts a fresh session must not rediscover

- **Identity:** sidechat = `deep2` = DeepSeek2; git is mine for my own work.
- **The fast gate's two reds are DeepSeek1's:** `data/README.md` says 403 rows where the files hold
  405, and their `TrimCurveTest` invokes `node` so `.ts` cannot load. `prepush` is therefore red;
  the operator directed this push anyway. Do not "fix" their files.
- **`.ts` and `.js` tests need separate `node --test` invocations;** one invocation mixing them
  loses the ESM detection for `.ts`. `scripts/test.py` now splits the groups.
- The analysis CLI is a slow batch (about five minutes); its test checks six rows and the pinned
  count, not the full run. `root_search`'s full search is about 60 s; its test is 0.5 s.
- `workbench/curve-analysis.json`, `root-candidates.json` and `coupler-curves.json` are
  regenerated from the TS; the Python twins agree where they still run.
- `scripts/emblem_stations.py` serialized `Fraction` bounds; they are floats now (the data audit
  is green).
- **The chat-display route is mine.** A new appendix is one markdown file in
  `app/src/data/chat-display/`; the renderer has no tables, so use lists.
- Node 24 at `~/node24`; `node --test tests/js/*.test.ts` runs the TypeScript group.
- The gothic family is `.ts` end to end; `curve-points.ts` is imported by the trim desk.

## 4. The one next action

Port `tests/test_regressions.py` (542 lines, 29 tests) to a TypeScript register. List each
test's mechanism first (subprocess to a Python module, subprocess to a Node check, a browser run,
a file/data assertion), then move one group at a time; the Python-only modules it calls stay
Python until their own ports. The pointer and the `Proves:` line are in
`next-shandoff-int.md`.
