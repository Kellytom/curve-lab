"""Session metrics: context in use, active minutes, turns — measured, logged, watched.

    .venv/bin/python scripts/ctx.py                  # current session, one line
    .venv/bin/python scripts/ctx.py --log            # ...and append to the tally
    .venv/bin/python scripts/ctx.py --tally          # every session's last record
    .venv/bin/python scripts/ctx.py --watch 60       # poll, beep at 70% and 85%
    .venv/bin/python scripts/ctx.py --json

Context is `input + cache.read` on the newest assistant turn, against the 1M
window. Duration and turns are reported, not judged: the session store shows no
error-rate rise with long sessions, so no time threshold is claimed here.

The tally is `state/sessions.jsonl`, one record per call.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = os.path.expanduser("~/.local/share/opencode/opencode.db")
DEFAULT_WINDOW = 156_000          # this engine (was 1_000_000, which under-reported 6.4x)
TALLY = os.path.join(ROOT, "state", "sessions.jsonl")
CAP_MS = 5 * 60 * 1000              # a gap longer than this is idle, not work
LEVELS = {"ok": 0, "warn": 1, "STOP": 2}


def beep(level: str) -> None:
    sound = "/System/Library/Sounds/Glass.aiff" if level == "warn" else "/System/Library/Sounds/Sosumi.aiff"
    try:
        if os.path.exists(sound):
            subprocess.run(["afplay", sound], check=False)
        else:
            print("\a", end="", flush=True)
    except Exception:                # noqa: BLE001
        print("\a", end="", flush=True)


def measure(db: str, sid: str | None, window: int) -> dict | None:
    if not os.path.exists(db):
        return None
    con = sqlite3.connect(db)
    if not sid:
        row = con.execute("select id from session_v2 order by time_updated desc limit 1").fetchone()
        if not row:
            return None
        sid = row[0]

    stamps = [r[0] for r in con.execute(
        "select time_created from session_message where session_id=? and type in ('user','assistant') "
        "order by time_created", (sid,)).fetchall()]
    active_ms = sum(min(abs(b - a), CAP_MS) for a, b in zip(stamps, stamps[1:]))
    turns = con.execute("select count(*) from session_message where session_id=? and type='assistant'",
                        (sid,)).fetchone()[0]

    for (data,) in con.execute(
            "select data from session_message where session_id=? and type='assistant' "
            "order by seq desc limit 50", (sid,)).fetchall():
        tokens = json.loads(data).get("tokens")
        if not tokens:
            continue
        used = int(tokens.get("input", 0)) + int(tokens.get("cache", {}).get("read", 0))
        pct = 100.0 * used / window
        verdict = "STOP" if pct >= 85 else ("warn" if pct >= 70 else "ok")
        return {"session": sid, "used": used, "window": window, "percent": round(pct, 2),
                "active_min": round(active_ms / 60000.0, 1), "turns": turns, "verdict": verdict}
    return None


def log_record(rec: dict) -> None:
    os.makedirs(os.path.dirname(TALLY), exist_ok=True)
    rec = dict(rec, at=datetime.now().isoformat(timespec="seconds"))
    with open(TALLY, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def show(rec: dict) -> None:
    print(f"session {rec['session']}")
    print(f"context {rec['used']:,} / {rec['window']:,} = {rec['percent']:.1f}%")
    print(f"active  {rec['active_min']:.0f} min · turns {rec['turns']}")
    if rec["verdict"] == "ok":
        print("verdict ok — plenty left")
    elif rec["verdict"] == "warn":
        print("verdict WARN — finish this step, start nothing new")
    else:
        print("verdict STOP — /fhandoff, then a new session")
    if rec["active_min"] >= 180:
        print("note: long session by choice — check the task is still the task")


def tally(limit: int = 20) -> int:
    if not os.path.exists(TALLY):
        print("no tally yet — run with --log")
        return 1
    last: dict[str, dict] = {}
    for line in open(TALLY, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except Exception:            # noqa: BLE001
            continue
        last[rec["session"]] = rec
    rows = sorted(last.values(), key=lambda r: r["at"], reverse=True)[:limit]
    print(f"{'at':>19} {'session':>30} {'ctx %':>7} {'min':>5} {'turns':>6}  verdict")
    for r in rows:
        print(f"{r['at']:>19} {r['session']:>30} {r['percent']:>6.1f}% {r['active_min']:>5.0f} {r['turns']:>6}  {r['verdict']}")
    print(f"\n{len(last)} sessions recorded · {TALLY}")
    return 0


def watch(db: str, sid: str | None, window: int, every: int, cycles: int | None) -> int:
    level = -1
    n = 0
    while cycles is None or n < cycles:
        rec = measure(db, sid, window)
        if rec is None:
            print("no session data")
            return 1
        lvl = LEVELS[rec["verdict"]]
        if lvl > level and lvl > 0:
            beep(rec["verdict"])
            print(f"\n*** {rec['verdict']} — {rec['percent']:.1f}% used ***", flush=True)
        level = max(level, lvl)
        print(f"\r{rec['percent']:.1f}% · {rec['active_min']:.0f} min · {rec['turns']} turns · {rec['verdict']}   ",
              end="", flush=True)
        n += 1
        if cycles is not None and n >= cycles:
            break
        time.sleep(every)
    print()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--session", default=None)
    ap.add_argument("--window", type=int, default=DEFAULT_WINDOW)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--tally", action="store_true")
    ap.add_argument("--watch", type=int, default=0, metavar="SECONDS")
    ap.add_argument("--cycles", type=int, default=None, metavar="N")
    args = ap.parse_args()

    if args.tally:
        return tally()

    if args.watch:
        return watch(args.db, args.session, args.window, args.watch, args.cycles)

    rec = measure(args.db, args.session, args.window)
    if rec is None:
        print("no token usage recorded for this session", file=sys.stderr)
        return 1
    if args.log:
        log_record(rec)
    if args.json:
        print(json.dumps(rec))
    else:
        show(rec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
