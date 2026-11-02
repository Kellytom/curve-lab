"""Run the tests, fast by default.

    .venv/bin/python scripts/test.py           # the quick set, ~12 s
    .venv/bin/python scripts/test.py --full    # everything, ~40 s
    .venv/bin/python scripts/test.py --slow    # only the slow modules

Three modules carry about two thirds of the runtime and are all numerical
sweeps rather than behaviour checks: they are worth running before a commit and
before a deploy, not on every look at the workbench.  Everything else is fast
enough to run constantly, which is the point of a default.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SLOW = {"test_svg", "test_practical", "test_fit"}


def modules():
    return sorted(p.stem for p in (ROOT / "tests").glob("test_*.py"))


def run(names):
    args = [sys.executable, "-m", "unittest"] + [f"tests.{n}" for n in names]
    t0 = time.perf_counter()
    r = subprocess.run(args, cwd=ROOT)
    return r.returncode, time.perf_counter() - t0


def main(argv):
    everything = modules()
    if "--full" in argv:
        chosen = everything
    elif "--slow" in argv:
        chosen = [n for n in everything if n in SLOW]
    else:
        chosen = [n for n in everything if n not in SLOW]
    code, secs = run(chosen)
    skipped = [n for n in everything if n not in chosen]
    print(f"\n  {len(chosen)} modules in {secs:.1f} s"
          + (f" · skipped {', '.join(skipped)} (--full for those)" if skipped else ""))
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
