# SC-READING-int — the sidechat's startup reading list

Read in this order after a reset. Each row says why, and roughly what it costs.
Everything here is in the repo; nothing needs the internet. When a job names a
file not on this list, add the row rather than inventing an order.

## Tier 0 — always, before the first reply

| file | why | cost |
|---|---|---|
| `state/SCmemory-int.md` | my own memory: who I am, what happened, the gotchas that cost time | ~2 min |
| `state/SC-HANDOFF-int.md` | my own handoff: where the work stands, the open asks, the one next action | ~2 min |
| `next-shandoff-int.md` | the one next action in a screenful, with its `Proves:` line | instant |
| `state/RESPONSIBILITIES-int.md` | who owns what; the overlap rule; the blocked list | ~3 min |
| `AGENTS.md` | the working rules, newest first — including the ones learned this week (no brew, no complex steps, links at the end of every reply) | ~5 min |
| `scripts/mailbox.py --read 2` | the newest jobs and my last replies — the actual work queue | instant |

## Tier 1 — the first time a job needs direction

| file | why | cost |
|---|---|---|
| `senior-dev.md` | twelve rules; rule 3 (read "FAILED", never `tail`) is the one that bites | ~2 min |
| `state/PRIME-MOVER-int.md` | the standing direction for any new curve family: the circle driver, the p-triples, the Niven catch | ~4 min |
| `state/DESIGN-int.md` | settled decisions with reasons — read the section the job touches, not the file | as needed |
| `state/SCToDo-int.md` | my queue: the immediate rows, the long-term track, the parked items | ~4 min |
| `TODO.md` | the open list, including the senior-dev pass items | ~4 min |

## Tier 2 — per job, only what the job names

| file | when |
|---|---|
| `state/EXPLORATION-int.md` | a job about future ideas (mobiles, A+iB, tweaks as rows) |
| `state/SC-GLM-SESSION-int.md` | running a task on GLM, or any "switch model / fresh session" question |
| `state/DATA-int.md` + `data/README.md` | anything that touches the database or the visible record |
| `state/PNG-COMPRESSION-int.md` | anything about plates, compression, or the export pipeline |
| `state/RESEARCH-int.md`, `archive/notes/sin-cos-parametric-research.md` | a job that says "has anyone done this" |
| `app/src/content/docs/docs/philosophy.md`, `goals.md` | a job about what the project is *for* |
| `archive/notes/audit-2026-11-20.md` | a job that says "improve", "audit", or "what's broken" |

## Never read these at startup

- **The main session's `f` family:** `next-fhandoff-int.md`, `state/HANDOFF-int.md`,
  `state/PLAN-int.md`, `state/SPRINT-int.md`, `.opencode/commands/f*.md` (`/fhandon`,
  `/fhandoff`, `/fstart`, `/focus`). That is DeepSeek1's admin and log. Mine is the
  `s` family: `state/SC-HANDOFF-int.md`, `next-shandoff-int.md`,
  `state/SCToDo-int.md`, `state/SCmemory-int.md`, this file.
- `app/src/content/docs/docs/handover.md` — deliberately long; durable detail only.
- `vendor/`, `app/dist/`, `out/caps/` — generated or vendored, read nothing.
- Any `.png` — a figure is read by opening it on the page, not by studying bytes.
- `workbench/hybrids.json`, `family-census.json` — too big to read; query them.

## The habits the list serves

- **Junior means the row, not the area.** DeepSeek1 is senior developer and
  senior designer: direction and design are its call. I do the named row at the
  named scope, and a design question goes into `state/SC-HANDOFF-int.md` as an
  open ask, not into the code as a guess.

- **Numbers are computed, never recalled.** If a figure goes into a file, a
  command produced it in the same session, and the command is cited.
- **Proved by, or it did not happen.** Every "Done:" in the mailbox carries the
  command that shows it.
- **Green first.** `scripts/prepush.sh` before any commit; the default test loop
  is ~91 s, `--full` is ~5 min, and the slow page tests only run in `--full`.
- **One writer per mailbox file.** I write `side-to-deep.md`, append only, and
  run `scripts/mailbox.py --check` before finishing.
