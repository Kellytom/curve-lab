"""Every crossing counter agrees on the pinned curves, or the test fails.

The pins were measured in this session and are stable across samplings:

- `c-0262` (`loop-8-11-mid-1`) = 9 pairs
- `c-0260` (`loop-5-8-12-mid-5`) = 19 pairs
- `c-0253` (`loop-12-13-15-mid-1`) = 6 pairs
- the Chebyshev arc `T3 x T5` on t in [0,1] = 2 pairs (the (p-1)(q-1)/2 formula
  counts the *closed* Lissajous on the circle, which is a different object)

Two counters had said 1 and 4 for the first and last of these; the counters were
reached, not the numbers. The reference is `scripts/ph_crossings.py` (the
router): it is the one exact core the docs quote.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ph_crossings import self_crossings, spine, stable_crossings  # noqa: E402
from scripts.chebyshev_curves import chebyshev, deriv  # noqa: E402

PINS = {"c-0262": 9, "c-0260": 19, "c-0253": 6}


def node() -> str:
    return os.environ.get("NODE24") or shutil.which("node") or str(Path.home() / "node24" / "bin" / "node")


class CrossingCalibrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = {r["uid"]: r for r in json.loads(
            (ROOT / "workbench" / "curve-registry.json").read_text())["curves"]}

    def test_the_router_reports_the_pinned_numbers(self) -> None:
        for uid, want in PINS.items():
            row = self.registry[uid]
            got = len(stable_crossings(row["speedX"], row["speedY"]))
            self.assertEqual(want, got, f"{uid} {row['name']}: router says {got}, pin says {want}")

    def test_the_chebyshev_arc_count(self) -> None:
        x, y = chebyshev(3), chebyshev(5)
        for samples in (600, 1200, 2400):
            got = len(self_crossings(deriv(x), deriv(y), samples=samples))
            self.assertEqual(2, got, f"T3 x T5 arc at {samples} samples says {got}")

    def test_the_stored_analysis_agrees_with_the_router(self) -> None:
        analysis = {row["uid"]: row for row in json.loads(
            (ROOT / "workbench" / "curve-analysis.json").read_text())["curves"]}
        for uid, want in PINS.items():
            self.assertEqual(want, analysis[uid]["crossings"],
                             f"{uid}: the stored analysis says {analysis[uid]['crossings']}")

    def test_the_python_polyline_counters_agree_with_the_router(self) -> None:
        from scripts.parametric_search import crossings as raw, signed_crossings
        from scripts.bezier_knots import crossings as bezier
        from scripts.coupler_curves import crossings as coupler
        for uid, want in PINS.items():
            row = self.registry[uid]
            _, xs, ys = spine(row["speedX"], row["speedY"], samples=1200)
            points = list(zip(xs.tolist(), ys.tolist()))
            self.assertEqual(want, signed_crossings(points), f"{uid} clustered")
            self.assertEqual(want, raw(points), f"{uid} parametric raw")
            self.assertEqual(want, bezier(points), f"{uid} bezier_knots")
            self.assertEqual(want, coupler(points), f"{uid} coupler")

    def test_the_page_counters_agree_with_the_router(self) -> None:
        row = self.registry["c-0262"]
        _, xs, ys = spine(row["speedX"], row["speedY"], samples=600)
        points = list(zip(xs.tolist(), ys.tolist()))
        with tempfile.TemporaryDirectory() as hold:
            fixture = Path(hold) / "spine.json"
            fixture.write_text(json.dumps(points))
            for module in ("lissajous.js", "lab-roots.js", "lattice-mobile.js"):
                result = subprocess.run(
                    [node(), "--input-type=module", "-e",
                     f"const {{crossings}} = await import('./app/src/scripts/{module}');"
                     "const { readFileSync } = await import('node:fs');"
                     f"const points = JSON.parse(readFileSync({str(fixture)!r}, 'utf8'));"
                     "console.log(crossings(points));"],
                    cwd=ROOT, capture_output=True, text=True, check=False,
                    env={**os.environ, "NODE24": node()},
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertEqual("9", result.stdout.strip().splitlines()[-1],
                                 f"{module} says {result.stdout.strip()!r}")


if __name__ == "__main__":
    unittest.main()
