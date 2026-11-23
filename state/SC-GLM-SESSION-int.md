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
| 4 | one line: `run the scan and write the report` | GLM session | no paste: the task and the output path are already in `~/.config/opencode/agents/glm-scan.md`. Choose that agent (`--agent glm-scan` on a command, or the agent picker) so the short line is enough. |
| 5 | let GLM write the md, approve it once, then `/new` | GLM session | GLM writes `deep2/notes/ai-news-scan-glm-5.3.md` itself; the permission prompt is the review. No copying. |
| 6 | model picker → back to `deepseek-v4.1-flash`, then `/sfocus` | DeepSeek | `/new` keeps the last model, so switch back first. Then: move to the repo, run the register, read `state/SC-HANDOFF-int.md`, `state/SCToDo-int.md`, `state/SCmemory-int.md` and `next-shandoff-int.md`, restate one action. |
| 7 | `/shandoff` | DeepSeek | writes the handoff again, now with whatever the GLM answer changed. |

## What to type at step 4

    run the scan and write the report

That is all. The task text and the output path both live in
`~/.config/opencode/agents/glm-scan.md`, so nothing is pasted and no repo file is
read: a GLM turn that opens one project file pays for that file on every later
turn.

If you write a different task by hand, keep the same shape — three lines:

1. what to do, with a budget ("at most 15 searches, 30 minutes") and the exact
   path to write;
2. what the project is, in one paragraph;
3. the output format, and "write nothing except that file".

## Where the answers land

| file | what it is |
|---|---|
| `deep2/notes/glm-ai-news-task.md` | the task text to paste |
| `deep2/notes/ai-news-scan-deepseek-review.md` | the finished scan on `deepseek-v4.1-flash`, 13:22 today — the baseline to compare GLM against |
| `deep2/notes/ai-news-scan-glm-5.3.md` | where the GLM answer goes (paste it, or redirect the headless run) |

## The headless fallback (only if you are not at the keyboard)

The agent `~/.config/opencode/agents/glm-scan.md` already carries the task, has
`shell: deny`, and runs from a neutral directory so no `AGENTS.md` is loaded. A
headless run cannot answer a permission prompt, so it needs `--auto` to be
allowed its one write:

```sh
cd "$TMPDIR" && opencode run --auto --agent glm-scan --model opencode-go/glm-5.3 \
  "Run the scan and write the report."
```

**Read the model line it prints** — `> <agent> · <model>`. A run that says
`deepseek-v4.1-flash` did not use GLM; that happened today, which is why
`--model` is on the command and why the first scan is labelled as the DeepSeek
review.

## Rules this file exists to keep

- **A GLM session never runs `/sfocus`.** That reads five files and the register.
- **One run, one question.** A follow-up in the same session re-reads the whole
  prefix; `/new` plus a short prompt is cheaper, even though it looks wasteful.
- **GLM writes exactly one file — its report.** Not a diff, not a second note:
  one `write` call to the path you named. Anything else is a change nobody
  senior has reviewed, and it costs tokens to re-read.
- **Nothing survives the session.** The old session is not deleted — it is on
  disk and `opencode session list` / `opencode session export` still reach it —
  but the next session never reads it, and it is not a project file. The answer
  has to be in a file the next session opens (`deep2/notes/…`), or it is lost to
  the work even though it still exists on disk.
- **The run is interactive, on purpose.** You are at the keyboard, so the one
  `write` prompt is the approval step; `--auto` is unnecessary and was the wrong
  turn on 2026-11-23. A headless run *cannot* answer that prompt, so it must be
  given `--auto` — which is why the headless route is the fallback, not the
  default.
- **The written file is untracked until you commit it.** Left alone, the next
  `/sfocus` sees a dirty tree and two agents see a file only one of them wrote.
