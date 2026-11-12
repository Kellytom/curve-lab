# legacy/timer — retired 2026-11-11

The session wall clock, kept for reference. **Do not start it in a session.**

## Why it was retired

It was added to defend against context exhaustion, on the theory that long
sessions were the risk. The actual pressure came from Chrome holding memory,
not from OpenCode's context, so the clock was measuring the wrong thing. It
also imposed a budget the operator could not see, which is the opposite of
what the timer was supposed to fix.

`scripts/ctx.py` remains in place and is the only measurement: it reports
context used against the 1M window.

## What moved here

| file | was |
|---|---|
| `timer.js` | `scripts/timer.js` |
| `notify.js` | `scripts/notify.js` |

Two path references were corrected after the move so the script still runs if
it is ever revived: `ROOT` now resolves two levels up, and the chime calls
`legacy/timer/notify.js`.

## If it is ever wanted again

```sh
node legacy/timer/timer.js --min 20m --no-cap "label"   # floor only
node legacy/timer/timer.js --check
node legacy/timer/timer.js --stop
node legacy/timer/timer.js --tally
```

It writes `.timer.json` at the repo root and appends to `state/timers.jsonl`.
Both still exist and are still gitignored. `state/timers.jsonl` is history —
sessions from 2026-11-05 to 2026-11-11 — not a live log.

Nothing imports these files. `AGENTS.md`, `/fhandon` and `/fhandoff` no longer
mention a clock.
