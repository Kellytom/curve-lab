#!/usr/bin/env python3
"""A lazy queue for slow work, so the chat never waits.

    jobq add "scripts/test.py --full" --name full-suite
    jobq list
    jobq run            drain the queue, one job at a time (leave this in a third terminal)
    jobq run --watch 10 stay up as the workhorse: check the queue every ten seconds
    jobq run --once     one job, then exit
    jobq log <id>       print a finished job's log

Why: the operator, 2026-11-23 — a slow job "is an asynchronous job and can be done lazily".
A chat message is serialised with the turn, so a six-minute command blocks the conversation.
The queue moves the waiting out of the session: the chat enqueues, the runner in a third
terminal drains, and the log is the report.

State lives in state/jobs/queue.json; each job writes state/jobs/<id>.log. A lock file keeps
two runners from taking the same job. Nothing here decides anything: a job is a command and
its output.
"""

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "state" / "jobs"
QUEUE = DIR / "queue.json"
LOCK = DIR / ".runner.lock"


def load():
    if QUEUE.exists():
        return json.loads(QUEUE.read_text())
    return {"format": "curve-lab.jobs/1", "jobs": []}


def save(data):
    DIR.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(json.dumps(data, indent=1) + "\n")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add(command, name, cwd):
    data = load()
    ident = f"j{int(time.time())}-{len(data['jobs']) + 1:03d}"
    data["jobs"].append({
        "id": ident,
        "name": name or command.split()[0],
        "command": command,
        "cwd": cwd or str(ROOT),
        "status": "queued",
        "created": now(),
        "started": None,
        "finished": None,
        "seconds": None,
        "log": str(Path("state") / "jobs" / f"{ident}.log"),
    })
    save(data)
    print(f"queued {ident}  {name or command}")


def show(data):
    if not data["jobs"]:
        print("the queue is empty")
        return
    for job in data["jobs"]:
        took = f"{job['seconds']:.1f}s" if job["seconds"] is not None else ""
        print(f"{job['id']}  {job['status']:<8} {took:>7}  {job['name']}")


def run(once=False, quiet=False):
    DIR.mkdir(parents=True, exist_ok=True)
    with open(LOCK, "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("another runner holds the queue")
            return 1
        while True:
            data = load()
            job = next((j for j in data["jobs"] if j["status"] == "queued"), None)
            if job is None:
                if not quiet:
                    print("nothing queued")
                return 0
            job["status"] = "running"
            job["started"] = now()
            save(data)
            started = time.time()
            if not quiet:
                print(f"running {job['id']}  {job['name']}")
            log = ROOT / job["log"]
            log.parent.mkdir(parents=True, exist_ok=True)
            with open(log, "w") as out:
                out.write(f"# {job['id']} {job['name']}\n# {job['command']}\n# from {job['cwd']}\n\n")
                out.flush()
                code = subprocess.call(job["command"], shell=True, cwd=job["cwd"],
                                       stdout=out, stderr=subprocess.STDOUT)
            job["seconds"] = time.time() - started
            job["finished"] = now()
            job["status"] = "done" if code == 0 else f"failed ({code})"
            save(data)
            if not quiet:
                print(f"{job['status']}  {job['id']}  {job['seconds']:.1f}s  "
                      f"log {job['log']}")
            # the operator is often away: a job that lands must be heard, not just written
            try:
                subprocess.Popen([str(Path.home() / "bin" / "ding"), f"{job['name']}: {job['status']}"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except OSError:
                pass
            if once:
                return 0 if code == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    addp = sub.add_parser("add")
    addp.add_argument("command")
    addp.add_argument("--name", default=None)
    addp.add_argument("--cwd", default=None)
    sub.add_parser("list")
    runp = sub.add_parser("run")
    runp.add_argument("--once", action="store_true")
    runp.add_argument("--quiet", action="store_true")
    runp.add_argument("--watch", type=int, default=0,
                      help="stay up, checking the queue every N seconds (workhorse)")
    logp = sub.add_parser("log")
    logp.add_argument("id")
    args = ap.parse_args()
    if args.cmd == "add":
        add(args.command, args.name, args.cwd)
    elif args.cmd == "list":
        show(load())
    elif args.cmd == "run":
        if args.watch:
            print(f"workhorse up: checking the queue every {args.watch}s; ctrl-c to stop")
            while True:
                run(quiet=True)
                time.sleep(args.watch)
        return run(args.once, args.quiet)
    elif args.cmd == "log":
        path = ROOT / "state" / "jobs" / f"{args.id}.log"
        if not path.exists():
            print(f"no log for {args.id}")
            return 1
        print(path.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
