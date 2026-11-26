# SC-HANDOFF-int — the sidechat's handoff (DeepSeek2)

Written 2026-11-25 at the operator's handoff request, before a context reset.
**Identity (operator, 2026-11-24): the sidechat = `deep2` = DeepSeek2 — one agent.** DeepSeek1
is the other. The `s` files, `data/said-deep2.json` and git for this agent's own work are mine;
the `f` family (`next-fhandoff-int.md`, `state/HANDOFF-int.md`, `state/PLAN-int.md`,
`state/SPRINT-int.md`) is not.

## 1. Where the work stands

1. **The register in TypeScript** — `tests/test_regressions.ts`, 36 rows, names identical to
   `tests/test_regressions.py` (diffed against every `def test_`, 36/36), 35 pass and the one
   known red (`DataReadmeCountsTest`). `scripts/test.py` runs it in `run_register()`. Commit
   `4515f906`.
2. **`/shandon`** — the sidechat's opening command, which did not exist; `/sfocus` names its
   twin. Commit `98e16b71`.
3. **The gothic desk** — `/gothic/` and `/gothic/<uid>` cut every stored curve at `t = 1/2 ∓ q`
   and save the arch. Proof: 18 tests in `tests/js/gothic.test.ts`; `c-0008a u-bowl-gothic` saved.
   **Committed and pushed in an earlier session.**
4. **The glue quintic (G3)** — `/glue/` kind "quintic (G3)"; six end conditions printed; the
   stated case at 1e-9. Proof: `tests/js/glue.test.ts` (5). **Committed and pushed earlier.**
5. **The TS ports** — `crossings.ts` (parity on 50 walks), `curve-analysis.ts` (405/405 rows),
   `root-search.ts` (pinned row: grid 105, bend 1.1696, inflections 2, crossings 3, places 3,
   grace 0.0445), `coupler-curves.ts` (49 curves, Python agrees exactly). Proof: their
   `tests/js/*.test.ts`. **Committed and pushed earlier.**
6. **The Tschirnhausen pieces** — six glue-ready pieces on `workbench/side-tests.html`, registered
   as Study rows. Proof: `/gothic/` names the four source pages. **Committed and pushed earlier.**
7. **The recent-work appendix** — `/chat-display/recent-work/`. **Committed and pushed earlier.**
8. **The identity note** — `AGENTS.md`, `state/SCmemory-int.md` and this file. **Committed.**
9. **The `f`-file blocks** (`state/HANDOFF-int.md`, `state/PLAN-int.md`,
   `state/REGRESSIONS-int.md`, `TODO.md`) — **uncommitted**, DeepSeek1's to review.
10. **Nothing is pushed from this session.** Pushes are on hold (see §3); both commits above are
    local only, and that is the one thing a crash would cost.

## 2. The operator's open asks, in order

1. **The TypeScript ports** — "add to your todo: transfer to typescript … and make sure you are
   writing directly in typescript not js". Done: crossings, analysis, root_search, coupler, the
   gothic family, the glue family, **the register**. Open: retiring the Python twin (row 7).
   First file: `state/SCToDo-int.md`.
2. **The gothic/glue work** — "we will use rational fraction values of the parametric" (done: the
   `t` pair); "Tschirnhausen and variations that would allow me to glue curves together" (pieces
   done; the join at the node needs the quintic's own loop mode — row 5, waiting on a shape).
   First file: `state/SPEC-glue-int.md`.
3. **"the curves we need are not stored per se …"** — extra-curves, glue, class V, side-tests
   (done as pages, links and Studies). First file: `state/SCToDo-int.md`.
4. **"keep working and dont stop to ask … i wont be here and that will block"** — the standing
   instruction; the living queue is `state/SCToDo-int.md` (the set of 2026-11-24).
5. **"make a note … sidechat = deep2 = deepseek2"** — done; named in the header and in
   `state/SCmemory-int.md` §Who I am.

## 3. Environment facts a fresh session must not rediscover

- **Identity:** sidechat = `deep2` = DeepSeek2; git is mine for my own work, one committer at a
  time. If a `/fhandon` arrives here by mistake, say so and ask — do not commit as DeepSeek1.
- **Pushes are on hold.** `state/SCmemory-int.md` (2026-11-21): "No more internet … commit
  locally when the gate is green and hold the push until the operator says internet is back."
  The operator's latest word in this session was still "commit and push"; the push was held, so
  say the command and let them decide.
- **The register is TypeScript now** (`tests/test_regressions.ts`). The Python twin stays in
  place until row 7 retires it, so `grep test_regressions` still finds 60+ references — do not
  read that as drift; read row 7.
- **`scripts/test.py`**: the register runs in `run_register()` after the JS tests, and `--slim` /
  `--slow` skip it. `--fast` is ~75 s and is a background job.
- **`.ts` and `.js` tests need separate `node --test` invocations**; one invocation mixing them
  loses ESM detection for the `.ts`. `scripts/test.py` splits the groups.
- **The fast gate's reds are not mine.** `data/README.md` says `curves.json` holds 405 rows and
  it holds 406 (DeepSeek1's). `test_hub_stills` also fails: four hub stills are older than the
  pages DeepSeek1 has modified in the tree — `node scripts/hub_shots.mjs` re-renders them, which
  would bake their in-flight pages into images, so **do not run it** until they say the pages are
  settled. `TrimCurveTest` passes now.
- The analysis CLI is a slow batch (about five minutes); its test checks six rows and the pinned
  count, not the full run. `root_search`'s full search is about 60 s; its test is 0.5 s.
- **Node 24 at `~/node24`**; the app is Astro on **4321** (health must say `node v24`, `astro 7`);
  the generated lab pages are a Python server on **8003**.
- **The chat-display route is mine.** A new appendix is one markdown file in
  `app/src/data/chat-display/`; the renderer has no tables, so use lists.
- The mailboxes are `archive/notes/deep-to-side.md` and `archive/notes/side-to-deep.md`.
- No brew installs; no internet; two gate tripwires after a doc edit are refreshers, not faults
  (`scripts/llms_full.py`, `scripts/reading_counts.py`).
- Cameras on my own page work: Playwright via `node scripts/shot.mjs <url> <out.png>` under
  `~/node24`, never the Review pane.

## 4. The one next action

**`state/SCToDo-int.md`, Immediate queue row 2:** post the variant payload that
`inkscape/ph_variant.py` builds through the app's own save endpoint — not into the registry
directly — and make the tune page show the candidate.

`Proves:` a posted variant appears in `data/` with `base_uid` set and
`workbench/curve-registry.json` untouched, and the tune page shows that candidate.

**Two questions for DeepSeek1, not to be guessed:** (a) row 5 of the 2026-11-24 set needs the
declared loop shape before any code; (b) row 7 — retiring the Python twin of the register — edits
their Tier-0 docs and the `f` commands: is that mine to sweep, or theirs?
