#!/usr/bin/env python3
"""One gate runner: the status line, the three tiers, and one heavy run at a time.

The operator's rule is that a wait over five seconds goes to the background, and
that a fix is not finished until the gate is green. This runner keeps the tiers in
one place so the wrong one is not run by habit:

    gate.py --status                 dev and built servers, their address, the database, git
    gate.py --fast                   the 4 s loop: engine, data, register
    gate.py --commit                 the commit gate (about 40 s)
    gate.py --pages                  every page check, all failures in one pass
    gate.py --pages --changed        only the routes whose source changed
    gate.py --pages --read-only      no save and no star write (while the operator works)
    gate.py --pages --url 4322       against the built server on another port
    gate.py --full                   the full Python suite then every page check

The heavy tiers take `state/gate.lock`, so two suites cannot starve each other.
Nothing here replaces `scripts/test.py`; it calls it.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "state" / "gate.lock"
PYTHON = str(ROOT / ".venv" / "bin" / "python")


def run(command: list[str], env: dict[str, str] | None = None) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            env={**os.environ, **(env or {})})
    return result.returncode, f"{result.stdout}{result.stderr}".strip()


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def acquire() -> None:
    if LOCK.exists():
        try:
            holder = int(LOCK.read_text().strip() or 0)
        except ValueError:
            holder = 0
        if holder and holder != os.getpid() and pid_alive(holder):
            sys.exit(f"another gate is running (pid {holder}); wait for it, do not start a second")
        LOCK.unlink()
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(os.getpid()))


def release() -> None:
    LOCK.unlink(missing_ok=True)


def show(label: str, code: int, output: str) -> int:
    print(f"\n$ {label}")
    if output:
        print(output)
    print(f"exit {code}")
    return code


def health(port: int) -> str:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=5) as response:
            body = json.load(response)
        return f"up · node {body.get('node')} · astro {body.get('astro')}"
    except Exception as error:  # noqa: BLE001 — the status line names the failure
        return f"down ({error.__class__.__name__})"


def status() -> int:
    print(f"server :4321  dev    {health(4321)}")
    print(f"server :4322  built  {health(4322)}")
    try:
        _, listeners = run(["lsof", "-nP", "-iTCP:4321", "-sTCP:LISTEN"])
        bound = [line for line in listeners.splitlines() if line.strip()][-1:]
        print(f"bind   127.0.0.1:4321  {' '.join(bound[0].split()[7:9]) if bound else 'not listening'}")
    except Exception:  # noqa: BLE001
        print("bind   127.0.0.1:4321  lsof unavailable")
    _, database = run(["node", "app/scripts/check-db.mjs"])
    print(f"database  {database.splitlines()[-1] if database else 'check failed'}")
    _, branch = run(["git", "branch", "--show-current"])
    _, changed = run(["git", "status", "--porcelain"])
    paths = [line for line in changed.splitlines() if line.strip()]
    print(f"git   {branch.strip() or 'detached'} · {len(paths)} paths changed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="the three gates in one place")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--pages", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--changed", action="store_true", help="pages: only the routes in the diff")
    parser.add_argument("--read-only", action="store_true", help="pages: no save and no star write")
    parser.add_argument("--url", default="4321", help="pages: server port (4321 dev, 4322 built)")
    args = parser.parse_args()

    if args.status or not any((args.fast, args.commit, args.pages, args.full)):
        return status()

    node = shutil.which("node") or "node"
    pages = [node, "app/scripts/check-all.mjs"] + (["--changed"] if args.changed else [])
    page_env = {"CURVE_LAB_URL": f"http://127.0.0.1:{args.url}"}
    if args.read_only:
        page_env["CURVE_LAB_READ_ONLY"] = "1"

    heavy = args.commit or args.pages or args.full
    if heavy:
        acquire()
    try:
        if args.fast:
            code, output = run([PYTHON, "scripts/test.py", "--fast"])
            if show("test.py --fast", code, output):
                return code
        if args.commit:
            code, output = run([PYTHON, "scripts/test.py"])
            if show("test.py (commit gate)", code, output):
                return code
        if args.full:
            code, output = run([PYTHON, "scripts/test.py", "--full"])
            if show("test.py --full", code, output):
                return code
        if args.pages:
            code, output = run(pages, page_env)
            if show(f"page checks (: {args.url}{', changed' if args.changed else ''}{', read-only' if args.read_only else ''})", code, output):
                return code
        return 0
    finally:
        if heavy:
            release()


if __name__ == "__main__":
    sys.exit(main())
