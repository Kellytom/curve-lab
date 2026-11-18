"""The power-curve numbers are computed, and the two old errors stay fixed.

app/src/content/docs/docs/curvature-power-curves.md was written with a correct formula and a wrong
table: n = 4 read 0.535 (it is 0.511), and the septic superellipse had its
maximum and minimum swapped. The script computes every number; this test runs
its regression check.
"""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CurvaturePowerTest(unittest.TestCase):
    def test_the_numbers_hold(self):
        result = subprocess.run([sys.executable, "scripts/curvature_power.py", "--check"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_the_doc_cites_the_script(self):
        text = (ROOT / "app" / "src" / "content" / "docs" / "docs" / "curvature-power-curves.md").read_text(encoding="utf-8")
        self.assertIn("scripts/curvature_power.py", text)
        self.assertIn("0.511", text)
        self.assertIn("flattest", text)


if __name__ == "__main__":
    unittest.main()
