"""The dot-solver gate: exit non-zero if any case regresses.

    python scripts/check-dots.py

Same measurement the page shows, re-derived from the geometry.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import dot_solver  # noqa: E402


def main() -> int:
    rows = dot_solver.measure(dot_solver.case_curves())
    bad = []
    for r in rows:
        state = "PASS" if r["ok"] else "FAIL"
        print(f"  {state}  {r['key']:14} marks {len(r['marks']):3} "
              f"chain-fit {r['worst_px']:6.2f}px")
        if not r["ok"]:
            bad.append(r["key"])
    print(f"\n{len(rows) - len(bad)}/{len(rows)} cases pass")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
