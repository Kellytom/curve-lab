"""Serve the repo, and forgive the missing /workbench prefix.

    .venv/bin/python scripts/serve.py            # port 8003, repo root
    .venv/bin/python scripts/serve.py --port 8004

The workbench pages live under `workbench/`, so `/catenary.html` is a 404 while
`/workbench/catenary.html` works.  Everyone types the short form, so this serves
the repo root and quietly redirects any bare page name that exists in
`workbench/` to its real path.  Everything else behaves like `http.server`.
"""

from __future__ import annotations

import argparse
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Workbench(SimpleHTTPRequestHandler):
    def do_GET(self):                       # noqa: N802
        path = self.path.split("?", 1)[0]
        if path.count("/") == 1 and path.endswith(".html"):
            name = path.lstrip("/")
            if (ROOT / "workbench" / name).is_file():
                self.send_response(302)
                self.send_header("Location", f"/workbench/{name}")
                self.end_headers()
                return
        super().do_GET()

    def log_message(self, fmt, *args):
        if " 302 " in (fmt % args):
            print("  redirect", self.path, "->", f"/workbench{self.path}")
        else:
            super().log_message(fmt, *args)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8003)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    handler = partial(Workbench, directory=str(ROOT))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"serving {ROOT} on http://{args.host}:{args.port}")
    print("  /catenary.html redirects to /workbench/catenary.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
