"""Every stored curve has a grid, a crossing count, a picture, a note and a page.

S4's finish line. The audit is the check; this test makes it part of the suite,
so a curve added without one of the five cannot land quietly.
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CurveAuditTest(unittest.TestCase):
    def test_every_stored_curve_has_all_five_fields(self):
        result = subprocess.run([sys.executable, "scripts/curve_audit.py"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout[-2000:] + result.stderr[-1000:])
        match = re.search(r"(\d+) curves · (\d+) with a gap", result.stdout)
        self.assertIsNotNone(match, result.stdout[-500:])
        self.assertEqual("179", match.group(1))
        self.assertEqual("0", match.group(2))


if __name__ == "__main__":
    unittest.main()
