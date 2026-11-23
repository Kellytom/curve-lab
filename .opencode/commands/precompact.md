---
description: Write the in-flight state to a file, then compact safely
---

Compaction is lossy — it replaces the conversation with a summary. Do this
first: write the in-flight truth to `state/PRE-COMPACT-int.md`, overwriting it,
40 lines at most, and **only what the next turn needs** (not history — the
summary already carries history):

1. **The one next action**, exactly, in the operator's terms.
2. **Files in play** — every path being edited, and its state: uncommitted,
   committed (hash), or clean.
3. **Decisions taken this session**, one line each, with the reason.
4. **Numbers put on any page or in any record**, each with the script that
   produced it — a number without its script is not trusted.
5. **Do-nots** — files not to touch, faults already made and fixed.

Then tell the operator to run `/compact` (or let it happen automatically).
After the compaction, the FIRST action is to read `state/PRE-COMPACT-int.md`
before doing anything else — do not trust the summary alone for paths and
numbers.

When the task lands (committed and pushed), fold what still matters into
`next-fhandoff-int.md` and delete the pre-compaction file; it is a short-lived
working note, not a second handoff.
