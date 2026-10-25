---
description: Focused handon — read next-fhandoff.md and carry out its one action
---

Focused handon for clothoid-lab. Work in
`/Users/thomaskelly/developer/clothoid-lab`.

1. Read `next-fhandoff.md` at the repo root, and nothing else yet.
2. Its first line names the docs to read. Read them, in order, and stop reading
   when they tell you to.
3. Its second line is the single focused action. Do that action, and only that
   action.
4. Keep `docs/HANDOFF.md` current as you work, so a freeze costs one step and
   not the session.
5. Do the action and stop. The operator runs `/fhandoff` when they want the
   focused handoff refreshed; it is not run automatically.

If `next-fhandoff.md` is missing or empty, read `docs/HANDOFF.md` and ask for the
single focused action instead of inventing one.

This is the opening command. `/fhandoff` is its twin at the other end of the
same session, but the two are not linked: `/fhandon` picks up the focused work
and stops; the operator calls `/fhandoff` to put it down and write the block
`/fhandon` will read next time.
