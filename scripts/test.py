"""Run the tests, fast by default, in parallel by module.

    .venv/bin/python scripts/test.py           # the quick set
    .venv/bin/python scripts/test.py --full    # everything
    .venv/bin/python scripts/test.py --slow    # only the slow modules
    .venv/bin/python scripts/test.py --jobs 1  # serial, for a clean traceback

Modules run as separate processes, one per module, up to --jobs at a time
(default: the CPU count). Each module is independent, so a failure in one cannot
hide another, and the wall clock is set by the slowest module rather than by the
sum. `--jobs 1` is the old behaviour.

Three modules carry about two thirds of the runtime and are all numerical
sweeps rather than behaviour checks: they are worth running before a commit and
before a deploy, not on every look at the workbench.  Everything else is fast
enough to run constantly, which is the point of a default.
"""

from __future__ import annotations

import concurrent.futures as futures
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SLOW = {"test_svg", "test_practical", "test_fit", "test_fleur_sets"}

# Only the two modules that write the same page compete for it:
# test_curve_census and test_stem_library both rebuild stem-library.html.
# Everything else builds in memory or writes its own file.
SERIAL = {"test_curve_census", "test_stem_library"}


def modules():
    return sorted(p.stem for p in (ROOT / "tests").glob("test_*.py"))


def one(name):
    t0 = time.perf_counter()
    r = subprocess.run([sys.executable, "-m", "unittest", f"tests.{name}"],
                       cwd=ROOT, capture_output=True, text=True)
    return name, r.returncode, time.perf_counter() - t0, r.stdout + r.stderr


def run(names, jobs=1):
    if jobs <= 1:
        args = [sys.executable, "-m", "unittest"] + [f"tests.{n}" for n in names]
        t0 = time.perf_counter()
        r = subprocess.run(args, cwd=ROOT)
        return r.returncode, time.perf_counter() - t0, []
    t0 = time.perf_counter()
    par = [n for n in names if n not in SERIAL]
    ser = [n for n in names if n in SERIAL]
    done = []
    with futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        for item in pool.map(one, par):
            done.append(item)
    for n in ser:                       # page writers, one at a time
        done.append(one(n))
    code = 0 if all(c == 0 for _, c, _, _ in done) else 1
    for name, c, secs, out in done:
        if c != 0:
            print(f"\n===== {name} FAILED ({secs:.1f}s) =====\n{out}")
    return code, time.perf_counter() - t0, done


def main(argv):
    everything = modules()
    if "--full" in argv:
        chosen = everything
    elif "--slow" in argv:
        chosen = [n for n in everything if n in SLOW]
    else:
        chosen = [n for n in everything if n not in SLOW]
    jobs = max(2, min(8, (os.cpu_count() or 2)))
    if "--jobs" in argv:
        jobs = max(1, int(argv[argv.index("--jobs") + 1]))
    code, secs, done = run(chosen, jobs)
    skipped = [n for n in everything if n not in chosen]
    if done:
        slow = sorted(done, key=lambda d: -d[2])[:5]
        print("\n  slowest: " + " · ".join(f"{n} {s:.1f}s" for n, _, s, _ in slow))
    print(f"  {len(chosen)} modules in {secs:.1f} s · jobs {jobs}"
          + (f" · skipped {', '.join(skipped)} (--full for those)" if skipped else ""))
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
