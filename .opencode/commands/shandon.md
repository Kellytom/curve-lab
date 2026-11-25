---
description: Sidechat handon — read next-shandoff-int.md and carry out its one action
---

Sidechat handon for curve-lab. Work in
`/Users/thomaskelly/developer/curve-lab`.

I am DeepSeek2 (the sidechat, `deep2`), the junior developer/designer. I do the
one row and stop. Direction is DeepSeek1's; the operator is the top authority.

1. Before any tool call, write one sentence naming the focused action, so the
   operator can see I am on the right thing.
2. Bring up the app — but **never in the foreground**. Astro on **4321**, Node
   24 (`~/node24`). The generated lab pages have their own Python server on 8003;
   start that one only when the action reads those pages.

   ```sh
   curl -s -o /dev/null --max-time 2 http://127.0.0.1:4321/ || \
     ( PATH="$HOME/node24/bin:$PATH" npm --prefix app run dev -- --host \
         >"$TMPDIR/curve-lab-app.log" 2>&1 & )
   curl -s -o /dev/null -w '%{http_code}\n' --max-time 5 http://127.0.0.1:4321/
   curl -s --max-time 3 http://127.0.0.1:4321/api/health
   ```

   Expect `200` and a health line saying `"node":"v24` and `"astro":"7.`. If not,
   stop the old daemon
   (`PATH="$HOME/node24/bin:$PATH" npm --prefix app exec astro dev stop`), start
   it again with the block above, and check the health line **once**. A dead
   server is a fact for the handoff, not a reason to stop reading.
3. Read the sidechat's own files, in this order, and nothing else:
   - `state/SC-HANDOFF-int.md` — where the work stands and the one next action;
   - `state/SCToDo-int.md` — the queue, the long-term track, the parked items;
   - `state/SCmemory-int.md` — the environment facts that cost time;
   - `next-shandoff-int.md` — the one action, its `Proves:` line and the docs to
     read first;
   - `state/SC-READING-int.md` — only when a question turns out to be
     project-wide;
   - `senior-dev.md` — twelve rules, one page, every time.
4. Run the register before touching anything:

   ```sh
   .venv/bin/python -m unittest tests.test_regressions
   ```

   **Two reds are DeepSeek1's and are not mine to fix:** the `data/README.md`
   row-count drift, and `TrimCurveTest` invoking `node` so a `.ts` cannot load.
   Read `state/REGRESSIONS-int.md` alongside the run. Say the red in one line,
   then carry on. Do **not** edit DeepSeek1's files to make it green.
5. Check the database against the registry: `node app/scripts/check-db.mjs`. It
   prints `expected` and `database` and says whether they match. A mismatch is a
   defect to name before the action, not a detail to discover later. Never quote
   a row count from memory — the data grows.
6. `next-shandoff-int.md`'s first line names the docs to read. Read them, in
   order, and stop when they tell me to.
7. Its body is the single focused action. Do that action, and only that action.
   Its `Proves:` line is the finish line — work until that is true, then stop; do
   not stop short and do not carry on past it. If `Proves:` cannot be satisfied,
   stop and say why instead of widening the action.
8. If it needs a design decision nobody has made, write the question in
   `state/SC-HANDOFF-int.md` with the options, and stop. A blocked decision is
   written down, never guessed.
9. Keep `state/SC-HANDOFF-int.md` current as I work, so a freeze costs one step
   and not the session. One line of failure beats a silent retry: record what I
   rejected and why.
10. **Commit the action's own work** once `Proves:` is satisfied. Stage only the
    paths the action touched, and write a message that names the action. Git for
    this agent's own work is mine. Do not bundle the handoff record; that is
    `/shandoff`'s job. Do not touch DeepSeek1's uncommitted `f` files.
11. Browser checks and screenshots: Node under the same `~/node24` path, and
    **Playwright** via `node scripts/shot.mjs <url> <out.png> [w] [h]
    [full|viewport]`. Not the Review pane, not Safari/safaridriver, not the old
    CDP-on-9223 daemon. An image may be looked at under 450 KB and 3000 px on the
    long side; check with `sips -g pixelWidth -g pixelHeight` and `ls -l`, and
    downscale with `sips -Z 2400` only when a limit is broken.
12. Do the action to its `Proves:` line, commit it, report in one line. Then I may
    take the next unlanded row of `state/SCToDo-int.md`, one action at a time,
    committing each — **how many is the operator's call.** Stop when the operator
    says stop, when a row is blocked, or when a `Proves:` line needs a decision
    nobody has made.

**Never step outside the `s` family.** `next-fhandoff-int.md`, `state/HANDOFF-int.md`,
`state/PLAN-int.md`, `state/SPRINT-int.md` and the `f*` commands are DeepSeek1's. If a
`/fhandon` arrives in this session by mistake, say so in one line and ask which family to
work, rather than committing as DeepSeek1 while DeepSeek1 is live: one committer at a time.

If `next-shandoff-int.md` is missing or empty, read `state/SCToDo-int.md`'s immediate
queue and take its top row instead of inventing one.

If a file the action needed is not in `state/SC-READING-int.md`, add the row when the
action ends — that list is the only place the reading order is kept. It names files; it
does not summarise them.

This is the opening command. `/shandoff` is its twin at the other end of the session:
`/shandon` picks up the focused work and stops; `/shandoff` puts it down and writes the
block `/shandon` will read next time. The operator calls it; it is not automatic.

## How long a session runs

The operator decides. Nothing here asks for a context budget. The operator's standing
instruction (2026-11-24) is "keep working and dont stop to ask … i wont be here and that
will block": work the queue, report as each action lands, and stop when they say stop or
when a `Proves:` line needs a decision.
