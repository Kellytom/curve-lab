"""Every curve in the export carries a star value: the stored rating, or none.

The operator, 2026-11-21: "add the stars to every curve either stored or none if unstarred
so far." The number is the database note's importance (1-10); `None` is an unstarred curve,
which is different from a rated 0. The pages read the same field (`loadRegistry`).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURVES = ROOT / "data" / "curves.json"
REGISTRY = ROOT / "workbench" / "curve-registry.json"


class CurveStarsTest(unittest.TestCase):
    def test_every_exported_curve_has_stars_or_none(self):
        rows = json.loads(CURVES.read_text(encoding="utf-8"))["rows"]
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))["curves"]
        self.assertEqual(len(rows), len(registry), "the export and the registry disagree")
        for row in rows:
            self.assertIn("stars", row, row["uid"])
            value = row["stars"]
            self.assertTrue(value is None or (isinstance(value, int) and 1 <= value <= 10),
                            f"{row['uid']} has stars {value!r}")
        self.assertTrue(any(row["stars"] is None for row in rows), "unstarred curves must say none")
        self.assertTrue(any(row["stars"] for row in rows), "no curve carries a stored rating")


if __name__ == "__main__":
    unittest.main()
