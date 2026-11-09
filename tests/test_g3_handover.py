"""The handover gallery: every G3-complete curve as a panel.

The gallery is generated from `g3_catalogue.catalogue()`, so these tests read
the generated JSON and page; they do not re-run the fit. The claims: one panel
per G3-complete curve, a curve and an acceleration graph in each panel, the
groups present, and no declared feature on a smooth row.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "workbench" / "g3-handover.json"
PAGE = ROOT / "workbench" / "g3-handover.html"


class TestHandoverGallery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.curves = cls.data["curves"]
        cls.counts = cls.data["counts"]

    def test_counts_match_the_curve_list(self):
        self.assertEqual(self.counts["complete"], len(self.curves))
        self.assertEqual(self.counts["smooth"] + self.counts["declared"],
                         self.counts["complete"])
        self.assertGreaterEqual(self.counts["smooth"], 100)

    def test_every_complete_curve_is_drawn(self):
        for row in self.curves:
            with self.subTest(curve=row["key"]):
                self.assertIn(f"Fig. H · {row['key']}", self.page)

    def test_each_panel_has_a_curve_and_an_acceleration(self):
        self.assertEqual(self.page.count('<section class="panel">'), len(self.curves))
        self.assertEqual(self.page.count("<svg "), 2 * len(self.curves))
        self.assertIn("G3 acceleration", self.page)
        self.assertIn("dκ/ds", self.page)
        self.assertIn("declared breaks", self.page)

    def test_the_groups_are_present(self):
        for label in ("Named curves", "Heart forms", "Integer cubics",
                      "Presets", "Primals", "LAC spines", "Stage II spines",
                      "Other families", "Cusp-arc curves"):
            with self.subTest(group=label):
                self.assertIn(label, self.page)

    def test_a_smooth_row_has_no_declared_feature(self):
        for row in self.curves:
            if row["smooth"]:
                with self.subTest(curve=row["key"]):
                    self.assertIsNone(row["feature"])

    def test_the_page_states_the_coordinate_convention(self):
        self.assertIn("+y up", self.page)


if __name__ == "__main__":
    unittest.main()
