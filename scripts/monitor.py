"""Watch the two connections this work depends on, and say which one breaks.

    .venv/bin/python scripts/monitor.py            # 5 s probes, until stopped
    .venv/bin/python scripts/monitor.py --serve    # also restart the page server

There are two different failures and they look alike from a browser:

  page refuses to connect   the local `http.server` has died; --serve fixes it
  ECONNRESET while talking  the socket to the model API dropped; that is the
                            network or the provider, not the page

This writes one line per probe to `state/monitor.log` so a pattern can be read
afterwards: is the failure local, or is it every host at once?
"""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "state" / "monitor.log"
PAGE = "http://127.0.0.1:8003/workbench/workbench.html"
OUT = ("https://1.1.1.1", "https://www.google.com/generate_204")


def probe(url, timeout=4.0):
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "monitor/1"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read(1)
        return True, (time.perf_counter() - t0) * 1000, ""
    except urllib.error.HTTPError as e:            # a reply is a reply
        return True, (time.perf_counter() - t0) * 1000, f"http {e.code}"
    except Exception as exc:                        # noqa: BLE001
        return False, (time.perf_counter() - t0) * 1000, type(exc).__name__


def dns(timeout=4.0):
    t0 = time.perf_counter()
    try:
        socket.setdefaulttimeout(timeout)
        socket.getaddrinfo("api.anthropic.com", 443)
        return True, (time.perf_counter() - t0) * 1000, ""
    except Exception as exc:                        # noqa: BLE001
        return False, (time.perf_counter() - t0) * 1000, type(exc).__name__


def serve():
    """Make sure the page server is up; it dies with the shell that started it."""
    ok, _, _ = probe(PAGE, timeout=1.5)
    if ok:
        return True
    subprocess.Popen(
        [sys.executable, "-m", "http.server", "8003", "--directory", str(ROOT)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)
    return False


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--every", type=float, default=5.0)
    ap.add_argument("--minutes", type=float, default=0)
    args = ap.parse_args(argv)

    LOG.parent.mkdir(parents=True, exist_ok=True)
    start = time.time()
    fails = {"page": 0, "out": 0, "dns": 0}
    n = 0
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# monitor start {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n")
        while True:
            n += 1
            if args.serve:
                serve()
            pr = probe(PAGE)
            ou = probe(OUT[0])
            dn = dns()
            fails["page"] += not pr[0]
            fails["out"] += not ou[0]
            fails["dns"] += not dn[0]
            stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
            line = (f"{stamp} page={'ok' if pr[0] else 'DOWN'}({pr[1]:.0f}ms)"
                    f" net={'ok' if ou[0] else 'DOWN'}({ou[1]:.0f}ms)"
                    f" dns={'ok' if dn[0] else 'DOWN'}({dn[1]:.0f}ms)")
            if not (pr[0] and ou[0] and dn[0]):
                line += f"  {pr[2] or ''} {ou[2] or ''} {dn[2] or ''}".rstrip()
            fh.write(line + "\n")
            fh.flush()
            print(line)
            if args.minutes and time.time() - start > args.minutes * 60:
                break
            time.sleep(args.every)
    print(json.dumps({"probes": n, "failures": fails}))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
