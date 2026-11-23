---
description: Focus the sidechat on curve-lab, and surface its own work state
---

Focus this session (the sidechat) on curve-lab, without starting any work.
This is the sidechat's `/focus`: the main session's focus command reads the
main handoff; this one reads OUR files, so a reset lands in the right list.

1. Move this session's working directory to
   `/Users/thomaskelly/developer/curve-lab` with the session-move tool. Do not
   `cd` in a shell; a shell `cd` does not move the session.
2. Run the register — a tenth of a second, and it says what is fixed and
   guarded:

   ```sh
   .venv/bin/python -m unittest tests.test_regressions
   ```

3. Read, in this order (the sidechat's tier 0):
   - `state/SC-HANDOFF-int.md` — where the work stands and the next action;
   - `state/SCToDo-int.md` — the queue, the long-term track, the parked items;
   - `state/SCmemory-int.md` — the environment facts that cost time;
   - `next-shandoff-int.md` — the one next action, and the docs to read first;
   - `state/SC-READING-int.md` only if a question turns out to be project-wide.

   Never step outside the `s` family on a focus: `next-fhandoff-int.md`,
   `state/HANDOFF-int.md`, `state/PLAN-int.md`, `state/SPRINT-int.md` and the
   `f*` commands are DeepSeek1's, not ours.

4. Restate the handoff's **one next action** in one or two lines of your own
   words. If the handoff is missing, read `state/SCToDo-int.md`'s immediate
   queue and restate its top row instead.

5. Stop there. Do not begin the action. Say what you read and what the next
   action is; the operator or the main session decides when to start.
