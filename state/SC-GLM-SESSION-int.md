# SC-GLM-SESSION-int — a task on GLM, paid for once

GLM bills every token it has to **write into cache and read back**. A long-lived
session with a project already in context costs the most; a fresh session that
you paste one task into and then throw away costs the least. So a GLM session is
a **one-shot**: no repo tour, no `/sfocus`, one question, one answer, dropped.

The sequence below is the whole shape. Steps 1 and 7 are DeepSeek; 2–5 are GLM.

## The sequence

| # | you type | in which session | why |
|---|---|---|---|
| 1 | `/shandoff` | the current DeepSeek session | commits the work, writes `state/SC-HANDOFF-int.md` and `next-shandoff-int.md`. Nothing is left living only in the context you are about to drop. |
| 2 | `/new` | — | an empty context. Do this **before** changing the model, so GLM's first turn is the task and not a 40,000-token history. |
| 3 | model picker → `opencode-go/glm-5.3` | the new session | `glm-5.3-flash` is the cheaper pass. An agent file's `model:` line is **not** enough: the TUI picker (or `--model` on a command) is what sets it. |
| 4 | paste the task | GLM session | one self-contained message. `deep2/notes/glm-ai-news-task.md` is already written that way. |
| 5 | copy the answer out, then `/new` | GLM session | the answer is the value; the context is now the expensive part. Save it to a file first, then drop the session. |
| 6 | `/sfocus` | DeepSeek | moves the session to the repo, runs the register, reads `state/SC-HANDOFF-int.md`, `state/SCToDo-int.md`, `state/SCmemory-int.md` and `next-shandoff-int.md`, and restates one action. |
| 7 | `/shandoff` | DeepSeek | writes the handoff again, now with whatever the GLM answer changed. |

## What to paste at step 4

The task file, unchanged and whole:

```
deep2/notes/glm-ai-news-task.md
```

Its own opening says it is self-contained and needs no project context, and that
is the point: a GLM turn that reads one repo file pays for that file on every
later turn. Paste it; do not tell GLM to go and open it.

If you write a task by hand, keep the same shape — three lines:

1. what to do, with a budget ("at most 15 searches, 30 minutes");
2. what the project is, in one paragraph;
3. the exact output format, and "do not edit any project file".

## Where the answers land

| file | what it is |
|---|---|
| `deep2/notes/glm-ai-news-task.md` | the task text to paste |
| `deep2/notes/ai-news-scan-deepseek-review.md` | the finished scan on `deepseek-v4.1-flash`, 13:22 today — the baseline to compare GLM against |
| `deep2/notes/ai-news-scan-glm-5.3.md` | where the GLM answer goes (paste it, or redirect the headless run) |

## The same run without typing, in one command

The agent `~/.config/opencode/agents/glm-scan.md` already carries the task, has
`edit: deny` and `shell: deny`, and runs from a neutral directory so no
`AGENTS.md` is loaded:

```sh
cd "$TMPDIR" && opencode run --agent glm-scan --model opencode-go/glm-5.3 \
  "Begin the scan now." > deep2/notes/ai-news-scan-glm-5.3.md 2>"$TMPDIR/glm-scan.err"
```

**Read the model line it prints** — `> <agent> · <model>`. A run that says
`deepseek-v4.1-flash` did not use GLM; that happened today, which is why
`--model` is on the command and why the first scan is labelled as the DeepSeek
review.

## Rules this file exists to keep

- **A GLM session never runs `/sfocus`.** That reads five files and the register.
- **One run, one question.** A follow-up in the same session re-reads the whole
  prefix; `/new` plus a short prompt is cheaper, even though it looks wasteful.
- **GLM returns text, not diffs.** No edits: a write is a diff that you then pay
  to re-read, and it is a change nobody senior has reviewed.
- **Nothing survives the session.** If it is worth keeping, it is in a file
  before `/new`.
