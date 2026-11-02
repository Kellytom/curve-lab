---
description: Focused handon — read next-fhandoff-int.md and carry out its one action
---

Focused handon for curve-lab. Work in
`/Users/thomaskelly/developer/curve-lab`.

1. Before any tool call, write one sentence naming the focused action you are
   about to carry out, so the operator can see you are on the right thing.
2. Bring up the single server. It is idempotent — if it is already up it says
   "already serving" and exits 0, so this is safe every time:
   `.venv/bin/python scripts/serve.py` → http://127.0.0.1:8003
3. Read `LTMemory-int.md` first — the map, the invariants, and what is already
   settled — then `next-fhandoff-int.md`, and nothing else yet.
4. `next-fhandoff-int.md`'s first line names the docs to read. Read them, in order,
   and stop reading when they tell you to.
5. Its second line is the single focused action. Do that action, and only that
   action.
6. Keep `state/HANDOFF-int.md` current as you work, so a freeze costs one step and
   not the session.
7. Where a browser check or a screenshot is needed, use **Playwright** via
   `node scripts/shot.mjs <url> <out.png> [w] [h] [full|viewport]`. It launches
   its own browser, so nothing has to be running first. Do not use the Review
   pane, Safari/safaridriver, or the old CDP-on-9223 daemon.
8. Do the action and stop. The operator runs `/fhandoff` when they want the
   focused handoff refreshed; it is not run automatically.

If `next-fhandoff-int.md` is missing or empty, read `state/HANDOFF-int.md` and ask for the
single focused action instead of inventing one.

This is the opening command. `/fhandoff` is its twin at the other end of the
same session, but the two are not linked: `/fhandon` picks up the focused work
and stops; the operator calls `/fhandoff` to put it down and write the block
`/fhandon` will read next time.
