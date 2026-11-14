---
description: Focused handoff — square the record fast, then write next-fhandoff-int.md with one action
---

Focused handoff for curve-lab. Work in
`/Users/thomaskelly/developer/curve-lab`. Do not start new feature work.

**Be fast.** Target a minute, not a session. One batched probe instead of six
calls, and no network round-trips for facts that only change when you deploy.
Anything you carry forward instead of re-checking must be labelled carried, with
the date it was last checked.

1. **Probe once.** Read `LTMemory-int.md`, then `state/HANDOFF-int.md`, then the
   previous `next-fhandoff-int.md`. Then run a single shell block with
   `--max-time 5` that prints: `git log -1 --format=%h`, `git status
   --porcelain`, and the HTTP status of local and remote. That is the whole
   default probe. Do not run `git diff` over the tree, and do not explore.

   Also answer one question in a line, because it decides what this handoff can
   claim: **did the previous action land?** Check its `Proves:` line — if it
   named a file, does that file exist and is it newer than the handoff? If not,
   the action did not land, and the next handoff says so rather than writing a
   new one.

2. **Re-verify only what moved.**
   - **Tests:** run `.venv/bin/python -m unittest discover tests` only if
     something under `web/`, `curve_lab/`, `csrc/`, or `tests/` differs from
     HEAD. Otherwise carry the recorded count and label it carried.
   - **Register:** run `.venv/bin/python -m unittest tests.test_regressions`. If
     this session fixed a fault, the row and its test are already in the commit;
     if it deliberately changed a listed behaviour, the row is amended in the
     same commit with the reason. A red register is a defect to fix before the
     block is written, not a note to carry.
   - **Claims:** if this session proved something that was not proved before,
     run `.venv/bin/python scripts/recheck.py` and commit the regenerated
     `state/ACHIEVEMENTS-int.md`. A claim in `HANDOFF-int.md` that recheck cannot
     re-derive is a defect, not a result.
   - **Cloud:** skip `gcloud` entirely (revision, limits, budget) unless this
     session deployed or changed Cloud Run, Cloud Build, or billing. Carry the
     recorded values and label them carried.
   - **Parity:** never run `scripts/check-parity.py` here; it is its own check.
   - **Handover:** read `docs/HANDOVER.md` only if a durable fact actually
     changed, and then keep `docs/HANDOVER.html` in step with it.
   - If something is genuinely ambiguous, write the uncertainty in one line
     rather than investigating it.

3. **Update `state/HANDOFF-int.md`** to the current truth: local, remote, tests,
   git state, risks, and the next move. Keep it to edits, not a rewrite. If the
   long arc moved, update `goals.md` (plant-forms → ornament-forms).

3a. **Record what failed.** One required line under the next move:

   ```text
   Tried and rejected: <path or idea> — <why>. (or: none)
   ```

   The rejected paths are the expensive knowledge; without them the next session
   pays for the same attempt twice. If nothing was rejected, write `none`.

3b. **Tick `TODO.md`.** If the action completed a `- [ ]`, mark it `- [x]`. If it
   opened work that now needs a label, add the item. Then regenerate the twin:
   `.venv/bin/python scripts/todo.py` (and `scripts/hub.py` if the bar changed).
   An unticked box is a checklist that lies.

4. **Choose exactly one focused action.** If `$ARGUMENTS` is not empty, use it.
   Otherwise take the single next move from `state/HANDOFF-int.md`. Do not bundle
   multiple tasks.

5. **Write `next-fhandoff-int.md` at the repo root.** One fenced block with
   exactly three lines:

   ```text
   Read state/HANDOFF-int.md. Read docs/HANDOVER.md only for durable detail.
   You are <the single focused action>.
   Proves: <the artifact and the check that make it done>.
   ```

   The `Proves:` line is the finish line. It must name something checkable — a
   generated page, a test, a printed number, a clearance report. "It looks
   right" is not a finish line, and neither is a percentage without its
   reference.

   Below the fence, add one line: the source doc, the date, and the commit that
   wrote it. See step 6 for how that hash stays true.

6. **Commit, in two steps, so the hash in the block is real.**

   Allowed paths — the handoff files **and** the files this process runs on:

   - `state/HANDOFF-int.md`, `next-fhandoff-int.md`, `goals.md`, `TODO.md`,
     `state/ACHIEVEMENTS-int.md`, `state/READING-int.md`,
     `state/REGRESSIONS-int.md`, `state/DESIGN-int.md`
   - `docs/HANDOVER.md`, `docs/HANDOVER.html`
   - `workbench/todo.html` if `scripts/todo.py` rewrote it
   - `AGENTS.md`, `.opencode/commands/*.md`, `.gitignore` if they changed

   First commit everything except `next-fhandoff-int.md`. Take
   `git log -1 --format=%h` — that is the commit that wrote the handoff. Then
   write the `Source:` line with that hash and commit `next-fhandoff-int.md`
   alone. Two commits, and the provenance is true instead of off by one.

   Never add `out/play-template.svg`. Do not run the tests after committing.

6a. **Resolve untracked paths.** For everything `git status --porcelain` showed
   as `??`, do exactly one of: commit it, add it to `.gitignore`, or delete it.
   Do not leave it undecided — undecided files are how the next session's
   `git status` becomes unreadable. Root-level photographs are committed under
   `reference/` with attribution or not at all.

7. **Reply with at most five bullets:** current state, the focused action and its
   `Proves:` line, any blocker, the commit hash, and the next command
   (`/fhandon`).

## If context ran out

When the session ends because context is exhausted, record it in the block: say
"I am at the end of usable context" in one line, and list what remains as the
next action. Do not silently narrow the work and call it complete — the next
session starts from this block and will trust it.

## Record the metrics

Before writing the block, run and paste the last line of:

```sh
.venv/bin/python scripts/ctx.py --log
```

Put the numbers in the `Context:` line of the block — percent used, active
minutes, turns, verdict. The tally in `state/sessions.jsonl` is how the next
session sees whether this pattern is working.

The clock is retired — see `legacy/timer/`. `ctx.py` is the only measurement
that survives: put its numbers in the `Context:` line.
