"""Run the tests, fast by default, in parallel by module.

    .venv/bin/python scripts/test.py           # the quick set
    .venv/bin/python scripts/test.py --slim    # the iteration gate, engine only
    .venv/bin/python scripts/test.py --full    # everything
    .venv/bin/python scripts/test.py --slow    # only the slow modules
    .venv/bin/python scripts/test.py --jobs 1  # serial, for a clean traceback
    .venv/bin/python scripts/test.py --browser # also the headless page checks

The browser checks need Chrome and the local server, so they are opt-in: they
are the only way to prove a control exists and draws (rails, the saved-curve
buttons), and they were folklore until 2026-11-17. `--browser` adds them after
the Python modules, in the same gate, so "green" means the page too.

Modules run as separate processes, one per module, up to --jobs at a time
(default: the CPU count). Each module is independent, so a failure in one cannot
hide another, and the wall clock is set by the slowest module rather than by the
sum. `--jobs 1` is the old behaviour.

Three modules carry about two thirds of the runtime and are all numerical
sweeps rather than behaviour checks: they are worth running before a commit and
before a deploy, not on every look at the workbench.  Everything else is fast
enough to run constantly, which is the point of a default.

--slim is for the tight loop: the engine's own behaviour (model, piece,
clearance, fillet, junction, section, grammar) and the exact-triple core, with
no page built. It is a smoke gate, not the commit gate; run the default before
a commit and --full before a push.
"""

from __future__ import annotations

import concurrent.futures as futures
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SLOW = {"test_svg", "test_practical", "test_fit", "test_fleur_sets",
        "test_ph_nth_sandbox2", "test_ph_11th_sandbox2", "test_crossings"}

# The tight-loop gate: the engine's own behaviour, no page built. Everything
# here runs in about a second per module. Deliberately not a substitute for the
# default set; it answers "is the model still sound", not "does every page
# still build".
SLIM = {
    "test_engine",
    "test_piece",
    "test_clearance",
    "test_fillet",
    "test_junction",
    "test_section",
    "test_grammar",
    "test_pyth_triples",
    "test_pyth_cubic",
    "test_todo",
}

# The fast loop: the engine, the data contract, the fixed-fault register and the
# exact core. Minutes of numerical sweeps and page rebuilds are deliberately
# out; run the default before a commit and --full before a push.
FAST = {
    "test_engine", "test_piece", "test_fillet", "test_section",
    "test_pyth_triples", "test_pyth_cubic",
    "test_regressions", "test_data_audit", "test_exact_numbers", "test_operator_list",
    "test_memory_freshness", "test_registry_paths", "test_curve_stars", "test_marginalia",
    "test_hub_stills",
}

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


BROWSER_CHECKS = ("check-saved.mjs", "check-rails.mjs", "check-tune-lab.mjs",
                  "check-side-pillars.mjs", "check-gothic.mjs", "check-roots.mjs")


def node_binary() -> str:
    """Node 24 lives at ~/node24 on this machine; the default `node` may be older and
    fails the app's tests. Prefer the one the app requires."""
    preferred = Path.home() / "node24" / "bin" / "node"
    return str(preferred) if preferred.exists() else "node"


def run_js_tests() -> int:
    """The browser-side modules' own tests, run in Node.

    The exact rational core, the polynomial helpers and the PH offset live in
    `workbench/*.js`; they run in the same runtime as the page, so their tests
    do too. This is the only reason Node is in the gate.
    """
    node = subprocess.run([node_binary(), "--version"], capture_output=True, text=True)
    if node.returncode != 0:
        print("  JS tests skipped: no node")
        return 0
    files = sorted((ROOT / "tests" / "js").glob("*.test.js"))
    files += sorted((ROOT / "app" / "tests").glob("*.test.mjs"))
    if not files:
        return 0
    result = subprocess.run([node_binary(), "--test", *[str(f) for f in files]],
                            cwd=ROOT, capture_output=True, text=True)
    passed = re.search(r"^(?:#|\u2139) pass (\d+)$", result.stdout, re.M)
    failed = re.search(r"^(?:#|\u2139) fail (\d+)$", result.stdout, re.M)
    summary = (f"{passed.group(1) if passed else '?'} pass, "
               f"{failed.group(1) if failed else '?'} fail")
    print(f"  JS tests: {summary}")
    if result.returncode != 0:
        print(result.stdout[-1600:])
        return 1
    return 0


def run_browser_checks() -> int:
    """The page checks that need Chrome: a control exists and draws."""
    node = subprocess.run([node_binary(), "--version"], capture_output=True, text=True)
    if node.returncode != 0:
        print("  browser checks skipped: no node")
        return 0
    code = 0
    for name in BROWSER_CHECKS:
        result = subprocess.run([node_binary(), str(ROOT / "scripts" / name)], cwd=ROOT,
                                capture_output=True, text=True)
        tail = (result.stdout.strip().splitlines() or [""])[-1]
        print(f"  {name}: {tail}")
        if result.returncode != 0:
            print(result.stdout[-1200:])
            code = 1
    return code


def main(argv):
    everything = modules()
    if "--full" in argv:
        chosen = everything
    elif "--slow" in argv:
        chosen = [n for n in everything if n in SLOW]
    elif "--slim" in argv:
        chosen = [n for n in everything if n in SLIM]
    elif "--fast" in argv:
        chosen = [n for n in everything if n in FAST]
    else:
        chosen = [n for n in everything if n not in SLOW]
    jobs = max(2, min(8, (os.cpu_count() or 2)))
    if "--fast" in argv:
        jobs = max(jobs, 8)
    if "--jobs" in argv:
        jobs = max(1, int(argv[argv.index("--jobs") + 1]))
    code, secs, done = run(chosen, jobs)
    skipped = [n for n in everything if n not in chosen]
    if done:
        slow = sorted(done, key=lambda d: -d[2])[:5]
        print("\n  slowest: " + " · ".join(f"{n} {s:.1f}s" for n, _, s, _ in slow))
    if "--slim" in argv or "--fast" in argv:
        tail = f" · skipped {len(skipped)} more (--full for those)"
    elif skipped:
        tail = f" · skipped {', '.join(skipped)} (--full for those)"
    else:
        tail = ""
    print(f"  {len(chosen)} modules in {secs:.1f} s · jobs {jobs}" + tail)
    if code == 0 and "--fast" not in argv:
        code = run_js_tests()
    if "--browser" in argv and code == 0:
        code = run_browser_checks()
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
