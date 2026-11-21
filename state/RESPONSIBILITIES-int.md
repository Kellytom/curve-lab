# RESPONSIBILITIES — who owns what, and why overlap is allowed

Read this at `/focus` and at sidechat startup. It exists because work stopped on a
**perceived** conflict: two agents avoided `plate_math.js` and `print_plates.mjs` in case
they touched each other, and nothing got built. That was a process fault, not caution.

## 1 · The rule, stated once

**Overlap is normal. Nobody is blocked by another agent working in the same file.**

Two agents may edit the same file in the same hour. Git merges text; the only thing that
cannot be merged is *discarded work*, and that happens when someone runs
`git checkout -- <file>` or `git restore` over another agent's uncommitted edit. Do not do
that. Ever.

You are blocked only by the short list in §4. A shared file is not on that list.

## 2 · The four roles

| role | decides | does | never |
|---|---|---|---|
| **Operator** | scope, what counts as good, whether to spend money or go online | looks at figures, judges, authorises | — |
| **DeepSeek1** | what is work; the review of a diff; the handoff text | reads, checks, writes the handoff and the memory | commits while DeepSeek2 is mid-job |
| **DeepSeek2** | how a thing is built | builds, renders, **owns git**: commits and pushes when `scripts/prepush.sh` is green, reports the hash | pushes without a green gate |
| **Sidechat** | nothing about the main tree | isolated research and jobs, reported through the mailbox | edits the working tree; installs with brew |

One committer at a time is a **git** rule, not a file rule. It orders commits; it does not
reserve files.

## 3 · Who normally touches what

| area | usual owner | others may still edit |
|---|---|---|
| `curve_lab/` (Python core, tests) | DeepSeek1 | yes |
| `workbench/plate_math.js`, `scripts/print_plates.mjs` | either main agent | **yes — this file is shared by design** |
| `app/src/pages/`, `app/src/scripts/` | either main agent | yes |
| `scripts/`, `tests/` | either main agent | yes |
| `state/` memory, specs, registers | DeepSeek1 | yes, add rows; do not rewrite another's argument |
| `data/`, `app/prisma/` schema | DeepSeek2 | tell someone first (migrations are in §4) |
| `archive/notes/` mailbox | writer writes, reader reads | reader never edits the other's file |

## 4 · The short list that genuinely needs coordination

These are the only things where two people at once cause real damage or real waste:

1. **A push.** One at a time. DeepSeek2's job.
2. **A schema migration** (`prisma db push`) or a data-format change that rewrites exports.
3. **Deleting files**, or anything that rewrites history (`rebase`, `reset --hard`, force-push).
4. **A whole-set re-render** (397 plates, ~10 min). Run it freely; just say you ran it, so
   the other does not run it again for nothing. Two runs are waste, not care.
5. **A deploy.** Explicit and separate from a push.

Everything else — editing the same function, the same page, the same test — needs no
permission and no waiting.

## 5 · Working in a file someone else has changed

```sh
git status --short                  # see whose work is in flight
git diff -- <file>                  # read before you overwrite
```

- Edit additively where you can; keep your diff to your own concern.
- Stage **paths**, never `git add -A`, so another agent's half-written file is not swept in.
- If your change and theirs are in the same lines, make yours fit theirs; do not revert it.
- If you must rewrite a block they wrote, say so in your report with the file and the reason.
- A failed test caused by their work is **their** red gate, not a reason to stop yours.
  Report it in one line and carry on.

## 6 · What to say when you finish

One line, in this shape:

    touched: <paths> · ran: <command> · result: <pass/fail/measured number>

That line is how the other agent knows what moved without asking, and it is why overlap
costs nothing.
