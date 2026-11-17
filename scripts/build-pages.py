"""Rebuild every page that carries the shared panel JavaScript.

    .venv/bin/python scripts/build-pages.py

The sandbox pages do not load `scripts/ph_nth_panels.js`; each one inlines a
copy of it at build time. So editing the shared file changes nothing until every
page that holds a copy is rebuilt, and a page rebuilt from an older source looks
like broken code in the browser. That is exactly how a working control (rails)
was reported dead while the source was fine (2026-11-16).

This runs the generators in the order their imports require, then the hub, and
prints nothing else. `tests/test_page_assets.py` fails when an inlined copy
does not match the source, so a forgotten rebuild is a red test rather than a
bug hunt.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / "bin" / "python"

# ph_nth_sandbox first: the 2 and exp pages import it for the base template.
GENERATORS = (
    "ph_nth_sandbox.py",
    "ph_nth_sandbox2.py",
    "ph_nth_sandbox_exp.py",
    "ph_11th_sandbox.py",
    "ph_11th_sandbox2.py",
    "ph_nth_serif_notes.py",
    "ph_11th_serif_notes.py",
    "ph_septic_sandbox.py",
    "hub.py",
)


def main() -> int:
    for name in GENERATORS:
        result = subprocess.run([str(PYTHON), str(ROOT / "scripts" / name)], cwd=ROOT,
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{name} failed:\n{result.stderr[-1500:]}")
            return result.returncode
        print(f"{name}: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
