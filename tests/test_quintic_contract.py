"""The shared quintic contract, checked from Python.

The Inkscape extension is Python, so the contract must hold from Python and not
only from the TypeScript test that the generator's author runs. Two languages,
one file, the same four facts — that is what "work together on a shared data
structure" has to mean for it to survive.

The operator's requirement, 2026-11-27: "deep2 is working on the inkscape code,
and you can work on the code from our side… but you have to work together on a
shared data structure."
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_quintic_contract.py"
GUIDES = ROOT / "workbench" / "quintic-guides.json"


class QuinticContractTest(unittest.TestCase):
    def test_the_python_reader_accepts_the_shared_files(self) -> None:
        run = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(run.returncode, 0, run.stderr or run.stdout)
        self.assertIn("200 curves", run.stdout)
        self.assertIn("1 closed", run.stdout)

    def test_the_frames_are_forward_tangents(self) -> None:
        data = json.loads(GUIDES.read_text())
        checked = 0
        for curve in data["curves"]:
            for span in curve["spans"]:
                p = span["points"]
                self.assertEqual(span["frame"]["start"]["tangent"], [p[1][0] - p[0][0], p[1][1] - p[0][1]])
                self.assertEqual(span["frame"]["end"]["tangent"], [p[5][0] - p[4][0], p[5][1] - p[4][1]])
                checked += 1
        self.assertEqual(checked, 200)

    def test_six_integer_points_per_span(self) -> None:
        data = json.loads(GUIDES.read_text())
        for curve in data["curves"]:
            for span in curve["spans"]:
                self.assertEqual(len(span["points"]), 6)
                for x, y in span["points"]:
                    self.assertIsInstance(x, int, f"{span['uid']} has a non-integer x")
                    self.assertIsInstance(y, int, f"{span['uid']} has a non-integer y")

    def test_the_closed_curve_carries_a_winding_and_meets_itself(self) -> None:
        data = json.loads((ROOT / "workbench" / "quintic-closed.json").read_text())
        ring = data["curves"][0]
        self.assertTrue(ring["closed"])
        self.assertIn(ring["winding"], ("ccw", "cw"))
        self.assertEqual(ring["spans"][-1]["points"][5], ring["spans"][0]["points"][0])


if __name__ == "__main__":
    unittest.main()
