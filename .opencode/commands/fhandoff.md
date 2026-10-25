---
description: Focused handoff — square the record, then write next-fhandoff.md with one action
---

Focused handoff for clothoid-lab. Work in
`/Users/thomaskelly/developer/clothoid-lab`. Do not start new feature work.

1. **Square the record first.** Read `docs/HANDOFF.md` and update it to the
   current truth: local URL/process, remote URL/revision, git state, tests,
   budget guardrail, risks, and the next move. Update `docs/HANDOVER.md` and
   `docs/HANDOVER.html` only if a durable fact changed.
2. **Choose exactly one focused action.** If `$ARGUMENTS` is not empty, use it
   as the action. Otherwise take the single next move from `docs/HANDOFF.md`.
   Do not bundle multiple tasks.
3. **Write `next-fhandoff.md` at the repo root.** It holds one fenced block with
   exactly two lines:

   ```text
   Read docs/HANDOFF.md. Read docs/HANDOVER.md only for durable detail.
   You are <the single focused action>.
   ```

   Below the fence, add one line: the source doc, the date, and the commit that
   wrote it. Change nothing else in that file.
4. **Commit only the handoff files** — `docs/HANDOFF.md`,
   `docs/HANDOVER.md`, `docs/HANDOVER.html`, `next-fhandoff.md`. Never add
   `out/play-template.svg`.
5. **Reply with at most five bullets:** current state, the focused action, any
   blocker, the commit hash, and the next command (`/fhandon`).
