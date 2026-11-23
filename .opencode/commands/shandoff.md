---
description: Write the sidechat's handoff before a reset — what exists, what is next
---

Write (or overwrite) `state/SC-HANDOFF-int.md` — the sidechat's own handoff,
for the session that starts after a context reset or a model switch. Keep it
under 120 lines. The sections, in this order:

1. **Where the work stands** — one numbered line per workstream, each naming
   the file or command that proves it. Only committed, pushed things count as
   standing; mark anything else "uncommitted".
2. **The operator's open asks, in order** — their words where possible, and
   for each, the file the next session should open first.
3. **Environment facts a fresh session must not rediscover** — the gotchas
   that cost time (tool flags, encoding traps, which agent owns which files).
4. **The one next action**, exactly.

Then commit and push the file (and any uncommitted work it describes) before
the reset — a handoff that exists only in the conversation is not a handoff.
