# SPEC — workhorse, the slow-job session

**Status, 2026-11-23:** the queue and the runner work; the page and the scheduler do not exist.

**The command:** `workhorse` (`~/bin/workhorse` → `scripts/jobq.py run --watch 10`)
**The queue:** `state/jobs/queue.json`; one log per job, `state/jobs/<id>.log`
**The session row:** `data/jobs.json` → `sessions` → `workhorse`

## What it is

The operator: a third session for slow work, "an asynchronous job and can be done lazily".
So workhorse is **not a chat**. It is a queue with one runner:

- **The chat enqueues.** `jobq add "<command>" --name <label>` returns in milliseconds and
  prints the job's id. The session is never blocked by a six-minute command again.
- **The workhorse drains.** `workhorse` sits in a third terminal, checks the queue every ten
  seconds, runs one job at a time, and writes the whole output to the job's log.
- **The log is the report.** `jobq log <id>` prints it; the chat says which job and where.

## Rules

- [x] One runner at a time: a lock file refuses a second `jobq run`. Check: start two, the
      second says "another runner holds the queue".
- [x] A job's status is `queued`, `running`, `done` or `failed (code)`; the seconds are
      recorded. Check: `jobq list`.
- [x] Nothing in the queue decides anything: a job is a command and its output. A decision
      stays a chat message to DeepSeek1.
- [x] The queue and the logs are local state; a job that writes records is still the
      committer's responsibility, not the workhorse's.
- [x] A `/jobs/` page on the Astro server, so the queue is readable without a terminal.
      It reads `state/jobs/queue.json` per request and shows the last lines of each log.

## Enqueue examples

```
jobq add ".venv/bin/python scripts/test.py --full" --name full-suite
jobq add "node scripts/print_plates.mjs --svg-only" --name plates
jobq add "node scripts/curve_pngs.mjs" --name figures
```
