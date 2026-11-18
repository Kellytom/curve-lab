---
description: Focused start — park the pending /fhandon direction, take the operator's direction, then run the /fhandon steps
---

Focused start for curve-lab. Work in
`/Users/thomaskelly/developer/curve-lab`.

This is `/fhandon` with a direction change in front of it. It does three things in
order: it **parks** the action the last `/fhandoff` wrote, it **writes** the
action from the operator's words, and then it **runs the `/fhandon` steps** on
that new action. The parked action is not lost: it goes on a stack and
`/fstart return` puts it back.

`$ARGUMENTS` is the direction. If it is empty, ask for one line and stop; do not
guess a direction.

## 1. Park, return, or take the direction

- **`/fstart return`** (also `resume`): pop the newest entry from
  `state/parked-focus-int.md`, write its block back to `next-fhandoff-int.md`,
  delete that entry from the stack, commit both files, and continue at step 3.
  If the stack is empty, say so in one line and stop — do not invent an action.

- **`/fstart <direction>`**: before anything is overwritten, copy the current
  `next-fhandoff-int.md` into `state/parked-focus-int.md`:

  ```text
  ## parked 2026-11-17T03:20Z — by /fstart

  ```text
  <the three-line block exactly as it was>
  ```

  Source: <its Source line, verbatim>
  ```

  Newest entry first. Never delete a parked entry except by `/fstart return`;
  the stack is the operator's queue of directions they still mean to take.

  If `next-fhandoff-int.md` is missing or empty, there is nothing to park: say
  so and go on.

## 2. Write the new direction as one action

Write `next-fhandoff-int.md` at the repo root in the same three-line form the
rest of the process uses:

```text
Read state/HANDOFF-int.md. Read app/src/content/docs/docs/handover.md only for durable detail.
You are <the single focused action, in the operator's sense>.
Proves: <the artifact and the check that make it done>.
```

Below the fence, one line: `Source: /fstart, 2026-11-17, <commit>.`

Rules that still hold:

- **One action.** If the operator's direction is broad ("make the page good"),
  say so in one line and write the smallest first action that visibly moves it.
  Do not bundle.
- **`Proves:` must be checkable** — a page, a test, a printed number, a report.
  "It looks right" is not a finish line.
- **Use the operator's words in the action** when they named the thing to change,
  so a later session can tell whether it was the same request.

Before the commit, put the direction into the rolling queue: it becomes the top
row of `state/PLAN-int.md` (marked *this session*), and the row it displaced is
marked *parked by /fstart <date>* if the stack now holds its block. A direction
that only lives in `next-fhandoff-int.md` is lost the moment the next handoff
overwrites it.

## 3. Commit the swap so it is recoverable

Two commits, so the hash in the block is real:

1. the parked stack (`state/parked-focus-int.md`) — take `git log -1 --format=%h`;
2. `next-fhandoff-int.md` alone, with that hash in its `Source:` line.

If `TODO.md` now carries an item for the direction, tick or add it and regenerate
`workbench/todo.html` with `scripts/todo.py` in the first commit.

## 4. Then be `/fhandon`

Read `.opencode/commands/fhandon.md` and carry out its steps 1–12 exactly,
treating the block you just wrote as the focused action: one sentence naming the
action before any tool call; the server up and backgrounded; the register run and
`state/REGRESSIONS-int.md` read; `state/READING-int.md` Tier 0 in its order, with
Tier 1 when the action changes direction, adds a page or module, or claims a
result; the action done to its `Proves:` line and no further; the action's own
paths committed; `state/HANDOFF-int.md` kept current as you go.

Do not restate the reading order here. `/fhandon` is the only copy of it.

## 5. Reply with five bullets at most

What was parked (or restored), the new action and its `Proves:` line, the
register result, the commit hash, and the next command (`/fhandon` continues the
same direction; `/fstart return` puts the parked one back).
