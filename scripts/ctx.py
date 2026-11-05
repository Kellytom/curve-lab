"""How much context is actually in use, read from the session store.

    .venv/bin/python scripts/ctx.py                 # newest session
    .venv/bin/python scripts/ctx.py --session ses_…
    .venv/bin/python scripts/ctx.py --window 1000000

The number is `input + cache.read` from the newest assistant message that
carries token usage: that is the prompt the model actually read on that turn.
Thresholds are against the window, not against a feeling.

    < 70%   ok
    70-85%  warn: finish the step, do not start another
    >= 85%  stop: /fhandoff and a new session
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys

DEFAULT_DB = os.path.expanduser("~/.local/share/opencode/opencode.db")
DEFAULT_WINDOW = 1_000_000          # DeepSeek V4.1 Flash


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--session", default=None)
    ap.add_argument("--window", type=int, default=DEFAULT_WINDOW)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print(f"no session store at {args.db}", file=sys.stderr)
        return 1

    con = sqlite3.connect(args.db)
    sid = args.session
    if not sid:
        row = con.execute("select id from session_v2 order by time_updated desc limit 1").fetchone()
        if not row:
            print("no sessions", file=sys.stderr)
            return 1
        sid = row[0]

    # active minutes: sum of gaps between turns, each capped at 5 min, so idle
    # time between messages does not count as work
    stamps = [r[0] for r in con.execute(
        "select time_created from session_message where session_id=? and type in ('user','assistant') "
        "order by time_created", (sid,)).fetchall()]
    active_ms = 0
    for a, b in zip(stamps, stamps[1:]):
        gap = (a - b) if a > b else (b - a)
        active_ms += min(gap, 5 * 60 * 1000)
    active_min = active_ms / 60000.0
    turns = con.execute("select count(*) from session_message where session_id=? and type='assistant'",
                        (sid,)).fetchone()[0]

    rows = con.execute(
        "select data from session_message where session_id=? and type='assistant' "
        "order by seq desc limit 50", (sid,)).fetchall()
    for (data,) in rows:
        tokens = json.loads(data).get("tokens")
        if not tokens:
            continue
        used = int(tokens.get("input", 0)) + int(tokens.get("cache", {}).get("read", 0))
        pct = 100.0 * used / args.window
        # context is measured; duration is reported, not judged: the session
        # store shows no error-rate rise with long sessions (0.47 vs 0.12 per
        # 100 turns), so a time threshold would be a guess, not a finding.
        if pct >= 85:
            verdict = "STOP"
        elif pct >= 70:
            verdict = "warn"
        else:
            verdict = "ok"
        if args.json:
            print(json.dumps({"session": sid, "used": used, "window": args.window,
                              "percent": round(pct, 1), "verdict": verdict}))
        else:
            print(f"session {sid}")
            print(f"context {used:,} / {args.window:,} = {pct:.1f}%")
            print(f"active  {active_min:.0f} min · turns {turns}")
            if verdict == "ok":
                print("verdict ok — plenty left")
            elif verdict == "warn":
                print("verdict warn — finish this step, start nothing new")
            else:
                print("verdict STOP — /fhandoff, then a new session")
            if active_min >= 180:
                print("note: long session by choice — check the task is still the task")
        return 0

    print("no token usage recorded for this session", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
