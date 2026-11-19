---
description: Focused handon — read next-fhandoff-int.md and carry out its one action
---

Focused handon for curve-lab. Work in
`/Users/thomaskelly/developer/curve-lab`.

1. Before any tool call, write one sentence naming the focused action you are
   about to carry out, so the operator can see you are on the right thing.
2. Bring up the app — but **never in the foreground**. The app is Astro on
   **4321** and runs on **Node 24** (`~/node24`). The generated lab pages have
   their own Python server on 8003; start that one only when the action reads
   those pages.

   ```sh
   curl -s -o /dev/null --max-time 2 http://127.0.0.1:4321/ || \
     ( PATH="$HOME/node24/bin:$PATH" npm --prefix app run dev -- --host \
         >"$TMPDIR/curve-lab-app.log" 2>&1 & )
   curl -s -o /dev/null -w '%{http_code}\n' --max-time 5 http://127.0.0.1:4321/
   ```

   Expect `200`. If it is not 200, say so in one line and carry on — a dead
   server is a fact for the handoff, not a reason to stop reading.

   A 200 is not enough after an upgrade: the daemon survives quitting OpenCode,
   and an old Astro can still hold the port. Read its identity:

   ```sh
   curl -s --max-time 3 http://127.0.0.1:4321/api/health
   ```

   It must say `"node":"v24` and `"astro":"7.`. If it does not, the server is
   from an older stack: stop it
   (`PATH="$HOME/node24/bin:$PATH" npm --prefix app exec astro dev stop`), start
   it again with the block above, and check the health line once.

3. Run the register before touching anything — it costs a tenth of a second and
   it is the only guard against undoing a fix that took hours:

   ```sh
   .venv/bin/python -m unittest tests.test_regressions
   ```

   Read `state/REGRESSIONS-int.md` alongside it: the row says what the fault
   looked like to the operator, and the test says what still guards it. If the
   action you are about to take would change a behaviour listed there, stop and
   say so rather than changing it quietly.
3b. Check the database against the registry: `node app/scripts/check-db.mjs`.
   Expect 262 curves, 262 notes, 262 sets. A mismatch is a defect to name before
   the action, not a detail to discover later.

4. Read `state/READING-int.md` **first**. It is the authoritative list of what
   to load, in order, with line costs and the never-load list. Follow its
   Tier 0 exactly. Do not
   invent a reading order, and do not skip a Tier 0 file because the action
   looks small. Its first row is `senior-dev.md`: twelve rules, one page, read
   it before the action every time.
5. Tier 0 includes `LTMemory-int.md` (the map and invariants), `goals.md` (the
   plant-form → ornament-form arc), `TODO.md` (the checklist) and
   `state/HANDOFF-int.md` (current truth — its **tail**, not the whole file; the
   count is in `READING-int.md`).
   Read them in the order `READING-int.md` gives.
6. Add **Tier 1** — `SPEC.md`, `app/src/content/docs/docs/project.md`, `goals.md`,
   `app/src/content/docs/docs/philosophy.md` — whenever the action changes direction, adds a page or
   module, claims a result, or touches a grade. Scope is otherwise one line, and
   it is at the foot of the Tier 1 section.
7. `next-fhandoff-int.md`'s first line names the docs to read. Read them, in
   order, and stop reading when they tell you to.
8. Its second line is the single focused action. Do that action, and only that
   action. Its third line, `Proves:`, is the finish line — do the action until
   that is true, then stop; do not stop short of it and do not keep going past
   it. If `Proves:` cannot be satisfied, stop and say why instead of widening
   the action.
9. Keep `state/HANDOFF-int.md` current as you work, so a freeze costs one step and
   not the session. One line of failure beats a silent retry: record what you
   rejected and why.
10. **Commit the action's own work** once `Proves:` is satisfied. Stage only the
   paths the action touched — generator, page, module, test, doc — and write a
   message that names the action. Do not bundle the handoff record; that is
   `/fhandoff`'s job. A finished action left uncommitted is the one thing a
   reboot, a crash or a `git checkout` can still destroy.
11. Where a browser check or a screenshot is needed, run Node under the same
    `~/node24` path, and use **Playwright** via
    `node scripts/shot.mjs <url> <out.png> [w] [h] [full|viewport]`. It launches
    its own browser, so nothing has to be running first. Do not use the Review
    pane, Safari/safaridriver, or the old CDP-on-9223 daemon. An image may be
    looked at when it is under 450 KB and 3000 px on the long side; check with
    `sips -g pixelWidth -g pixelHeight` and `ls -l`, and downscale with
    `sips -Z 2400` only when a limit is actually broken.
12. Do the focused action to its `Proves:` line, commit it, and report in one
    line. Then the session may take the next unlanded row of `state/PLAN-int.md`,
    one action at a time, committing each — **how many is the operator's call.**
    Stop when they say stop, when a row is blocked, or when a `Proves:` line needs
    a decision nobody has made. The operator runs `/fhandoff` when they want the
    focused handoff refreshed; it is not run automatically.

If `next-fhandoff-int.md` is missing or empty, read `state/HANDOFF-int.md` and ask for the
single focused action instead of inventing one.

If a file you needed is not in `state/READING-int.md`, add the row when the
action ends — the list is the only place the reading order is maintained.
Never restate what a listed file says inside `READING-int.md`; it names files,
it does not summarise them.

This is the opening command. `/fhandoff` is its twin at the other end of the
same session, but the two are not linked: `/fhandon` picks up the focused work
and stops; the operator calls `/fhandoff` to put it down and write the block
`/fhandon` will read next time.

## How long a session runs

The operator decides. Nothing here limits context use or asks for a budget; the
2026-11-16 meter measured the wrong thing (OpenCode, while Chrome was the
pressure) and is retired. Work the plan, report as each action lands, and stop
when the operator says stop.
