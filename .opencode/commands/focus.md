---
description: Move this session to curve-lab and surface its focused work
---

Focus this session on curve-lab, without starting any work.

1. Move this session's working directory to
   `/Users/thomaskelly/developer/curve-lab`. Use the session-move tool; do
   not `cd` in a shell, because a shell `cd` does not move the session.
2. Run the register, so this session starts by knowing what is already fixed.
   It costs a tenth of a second:

   ```sh
   .venv/bin/python -m unittest tests.test_regressions
   ```

   Then read `state/REGRESSIONS-int.md` (the faults and their guards) and
   `state/DESIGN-int.md` (settled decisions and why). The wall clock is retired;
   `scripts/ctx.py` is the only measurement now.

3. Read `next-fhandoff-int.md` at that repo root. Restate its second line — the
   one focused action — in one or two lines of your own words.
4. If `next-fhandoff-int.md` is missing or empty, read `state/HANDOFF-int.md` and
   restate the Next move section instead.
5. Stop there. Do not begin the action. The project-scoped `/fhandon` command
   is now available in this session and runs it; `/fhandoff` writes the block
   `/fhandon` reads next time.

Report only the current focus, the clock state and that `/fhandon` is available.
If the move fails, say so plainly and do not report a focus from a directory you
are not in.
