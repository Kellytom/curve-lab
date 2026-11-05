"""Guards the ending fit pass: ten sections, attached, clear, unfolded."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ending_fit as F  # noqa: E402


class EndingFitTest(unittest.TestCase):
    def setUp(self):
        self.page = (ROOT / "workbench" / "ending-fit.html").read_text(
            encoding="utf-8")
        self.rows = F.fit_data()

    def test_ten_sections_are_fitted(self):
        self.assertEqual(len(self.rows), 10)
        names = {r["name"] for r in self.rows}
        for want in ("Cycloid", "Astroid", "Semicubical / Neile", "Tractrix",
                     "Heart", "Squircle", "Bicorn", "Nodal",
                     "Tschirnhausen", "Piriform 2×"):
            self.assertIn(want, names)
        self.assertEqual(self.page.count('<section class="card">'), 10)

    def test_none_crosses_itself_or_the_rails(self):
        for row in self.rows:
            self.assertEqual(row["intersections"], 0, row["name"])
            self.assertGreaterEqual(row["clearance"], 0.45, row["name"])
            self.assertGreater(row["scale"], 0.0, row["name"])
        self.assertEqual(self.page.count("keeps its grade"), 10)
        self.assertNotIn("· flag", self.page)

    def test_the_rule_is_stated(self):
        self.assertIn("6 × offset", self.page)
        self.assertIn("2 × offset rule", self.page)
        self.assertIn("ending grades", self.page)


if __name__ == "__main__":
    unittest.main()
