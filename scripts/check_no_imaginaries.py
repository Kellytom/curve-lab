#!/usr/bin/env python3
"""The imaginary ban, as a check that can fail.

    .venv/bin/python scripts/check_no_imaginaries.py
    .venv/bin/python scripts/check_no_imaginaries.py --all   # include the debt list

The rule is in `state/EXACT-NUMBERS-int.md`: a complex step imports a square root
(`2 + i` has length `√5`), so the engine is written in whole numbers and ratios.
This scans the pages and their scripts for the ways a complex number gets back in.

The live tree is the pages and their scripts (`app/src/`). The files listed as debt
are scanned only with `--all`, so the debt is visible and not silently forgotten.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LIVE = [
    ROOT / "app" / "src" / "pages",
    ROOT / "app" / "src" / "scripts",
    ROOT / "app" / "src" / "lib",
]

DEBT = [
    "curve_lab/ph_hermite.py",
    "curve_lab/measure.py",
    "scripts/ph_carry.py",
    "scripts/g3_cut.py",
    "scripts/ph_families.py",
    "scripts/pm4_search.py",
    "scripts/pm_deep_search.py",
    "tests/test_ph_hermite.py",
]

SUFFIXES = {".astro", ".js", ".mjs", ".ts", ".py"}

# Each pattern is something that puts a complex quantity or its square root back in.
PATTERNS = [
    (re.compile(r"\b1j\b"), "a Python complex literal"),
    (re.compile(r"\b\d+(?:\.\d+)?j\b"), "a Python complex literal"),
    (re.compile(r"\bcmath\b"), "the complex maths module"),
    (re.compile(r"\bcomplex\s*\("), "a complex number constructor"),
    (re.compile(r"Math\.sqrt\s*\(\s*5\s*\)"), "the length √5"),
    (re.compile(r"√\s*5"), "the length √5"),
    (re.compile(r"\bimaginary\b", re.IGNORECASE), "the banned word"),
]


def scan(paths):
    findings = []
    for base in paths:
        if not base.exists():
            continue
        files = [base] if base.is_file() else sorted(p for p in base.rglob("*") if p.suffix in SUFFIXES)
        for path in files:
            if not path.is_file() or path.suffix not in SUFFIXES:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for pattern, why in PATTERNS:
                    if pattern.search(line):
                        findings.append((path, number, why, line.strip()[:110]))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="include the debt list")
    args = parser.parse_args(argv)

    paths = list(LIVE)
    if args.all:
        paths += [ROOT / name for name in DEBT]

    findings = scan(paths)
    if findings:
        print(f"{len(findings)} imaginary trace(s):")
        for path, number, why, line in findings:
            print(f"  {path.relative_to(ROOT)}:{number}  {why}\n    {line}")
        return 1

    scope = "pages and scripts" if not args.all else "pages, scripts and the debt list"
    print(f"ok — no imaginary trace in the {scope}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
