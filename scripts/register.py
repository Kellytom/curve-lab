"""Run the whole regression register: the fast checks and the browser gate.

    .venv/bin/python scripts/register.py
    .venv/bin/python scripts/register.py --no-browser

Exit codes: 0 all ran and passed, 1 something failed, 2 something could not run
(a skip is not a pass — it is reported, and it changes the exit code so a silent
gap cannot be mistaken for health).

What it runs:

* `tests/test_regressions.py` — one check per fault that cost real work. Fast.
* `scripts/check-nth-page.mjs` — the browser facts (the flat-spot strip, the
  suggestion rows, typing in a box, the gallery loading a curve). It needs the
  local server and a headless browser; both are arranged here rather than assumed.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv" / "bin" / "python"
SERVER_LOG = Path(os.environ.get("TMPDIR", "/tmp")) / "curve-lab-register-serve.log"
URL = "http://127.0.0.1:8003/"


def port_open(host="127.0.0.1", port=8003, timeout=1.0) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def server_answers(timeout=2.0) -> bool:
    try:
        with urllib.request.urlopen(URL, timeout=timeout) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def ensure_server(wait_seconds=15) -> tuple[bool, str]:
    """Start the local server if it is down, and wait for it to answer."""
    if server_answers():
        return True, "already serving"
    if not port_open():
        if not (ROOT / "scripts" / "serve.py").exists():
            return False, "scripts/serve.py is missing"
        with SERVER_LOG.open("ab") as log:
            subprocess.Popen([str(VENV), "scripts/serve.py"], cwd=ROOT,
                             stdout=log, stderr=log, start_new_session=True)
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        if server_answers():
            return True, "started"
        time.sleep(0.3)
    return False, f"no answer on :8003 after {wait_seconds}s (see {SERVER_LOG})"


def run(command, timeout) -> tuple[str, str]:
    """Run a command, return (PASSED/FAILED/SKIPPED, detail)."""
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as error:
        return "SKIPPED", f"not available: {error.filename}"
    except subprocess.TimeoutExpired:
        return "FAILED", f"timed out after {timeout}s"
    output = (result.stdout + result.stderr).strip().splitlines()
    tail = output[-1] if output else ""
    if "Cannot find module 'playwright-core'" in (result.stderr or ""):
        return "SKIPPED", "playwright-core is not installed for node"
    return ("PASSED" if result.returncode == 0 else "FAILED"), tail[:120]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-browser", action="store_true",
                        help="run only the fast checks and say the browser gate was skipped")
    args = parser.parse_args()

    rows = []

    python = str(VENV) if VENV.exists() else sys.executable
    status, detail = run([python, "-m", "unittest", "tests.test_regressions"], timeout=120)
    rows.append(("the fast register (fixed faults)", status, detail))

    if args.no_browser:
        rows.append(("the browser gate", "SKIPPED", "not asked for (--no-browser)"))
    else:
        ready, why = ensure_server()
        if not ready:
            rows.append(("the browser gate", "SKIPPED", f"no server: {why}"))
        else:
            status, detail = run(["node", "scripts/check-nth-page.mjs"], timeout=600)
            rows.append((f"the browser gate ({why})", status, detail))

    width = max(len(name) for name, _, _ in rows)
    print()
    for name, status, detail in rows:
        print(f"  {name.ljust(width)}  {status:8s} {detail}")
    print()

    failed = [row for row in rows if row[1] == "FAILED"]
    skipped = [row for row in rows if row[1] == "SKIPPED"]
    if failed:
        print(f"{len(failed)} failed. Fix before writing a handoff block.")
        return 1
    if skipped:
        print(f"{len(skipped)} could not run. That is not a pass: say so in the block.")
        return 2
    print("all clear.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
