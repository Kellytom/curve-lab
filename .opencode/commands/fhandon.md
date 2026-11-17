---
description: Focused handon — read next-fhandoff-int.md and carry out its one action
---

Focused handon for curve-lab. Work in
`/Users/thomaskelly/developer/curve-lab`.

1. Before any tool call, write one sentence naming the focused action you are
   about to carry out, so the operator can see you are on the right thing.
2. Bring up the single server — but **never run it in the foreground**. It
   prints "already serving" and exits 0 when the port is taken, and blocks
   forever in `serve_forever` when it is not, so a bare call hangs the session.
   Start only if the port is down, and background it:

   ```sh
   curl -s -o /dev/null --max-time 2 http://127.0.0.1:8003/ || \
     ( .venv/bin/python scripts/serve.py >"$TMPDIR/curve-lab-serve.log" 2>&1 & )
   curl -s -o /dev/null -w '%{http_code}\n' --max-time 3 http://127.0.0.1:8003/
   ```

   Expect `200`. If it is not 200, say so in one line and carry on — a dead
   server is a fact for the handoff, not a reason to stop reading.
3. Run the register before touching anything — it costs a tenth of a second and
   it is the only guard against undoing a fix that took hours:

   ```sh
   .venv/bin/python -m unittest tests.test_regressions
   ```

   Read `state/REGRESSIONS-int.md` alongside it: the row says what the fault
   looked like to the operator, and the test says what still guards it. If the
   action you are about to take would change a behaviour listed there, stop and
   say so rather than changing it quietly.
4. Read `state/READING-int.md` **first**. It is the authoritative list of what
   to load, in order, with line costs and the never-load list. Follow its
   Tier 0 exactly; it is the whole of the session's context budget. Do not
   invent a reading order, and do not skip a Tier 0 file because the action
   looks small. Its first row is `senior-dev.md`: twelve rules, one page, read
   it before the action every time.
5. Tier 0 includes `LTMemory-int.md` (the map and invariants), `goals.md` (the
   plant-form → ornament-form arc), `TODO.md` (the checklist) and
   `state/HANDOFF-int.md` (current truth — its **tail**, not the whole file; the
   count is in `READING-int.md`).
   Read them in the order `READING-int.md` gives.
6. Add **Tier 1** — `SPEC.md`, `docs/PROJECT.md`, `goals.md`,
   `docs/PHILOSOPHY.md` — whenever the action changes direction, adds a page or
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
11. Where a browser check or a screenshot is needed, use **Playwright** via
    `node scripts/shot.mjs <url> <out.png> [w] [h] [full|viewport]`. It launches
    its own browser, so nothing has to be running first. Do not use the Review
    pane, Safari/safaridriver, or the old CDP-on-9223 daemon. Never `read` the
    PNG it writes: the engine has no image input, and one image in the history
    fails every later turn with `image input is not available on this engine`.
    Report the path and let the operator look.
12. Do the action and stop. The operator runs `/fhandoff` when they want the
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

## Context

The clock is retired and the meter is retired (2026-11-16): neither percentage
nor minute count is quoted or acted on. If context trouble returns, it is a row
in `TODO.md`. Do not reinstate a threshold here.
