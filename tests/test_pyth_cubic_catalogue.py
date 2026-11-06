"""Guards the integer-cubic catalogue: counts, controls, signs, rotations."""

import unittest
from pathlib import Path

from curve_lab.pyth_cubic import catalogue, case, checks
from curve_lab.pyth_triples import base_triples


class IntegerCubicCatalogueTest(unittest.TestCase):
    def setUp(self):
        self.rows = catalogue(1000)
        self.prims = [t for t in base_triples(1000) if t["k"] == 1]

    def test_counts_follow_the_triples(self):
        self.assertEqual(len(self.prims), 158)
        self.assertEqual(len(self.rows), 2 * len(self.prims))
        self.assertEqual(len(self.rows), 316)

    def test_every_row_is_integer_and_checked(self):
        for row in self.rows:
            self.assertTrue(checks(row), row["label"])
            self.assertEqual(row["chord"], 2 * row["c"])
            self.assertEqual(row["arm"], row["c"])
            for p in (row["p0"], row["p1"], row["p2"], row["p3"],
                      row["mirror_p1"], row["mirror_p2"], row["mirror_p3"],
                      *row["rotation_points"]):
                self.assertIsInstance(p[0], int, row["label"])
                self.assertIsInstance(p[1], int, row["label"])

    def test_the_3_4_5_rows(self):
        ab = next(r for r in self.rows
                  if r["label"] == "3-4-5" and r["order"] == "ab")
        self.assertEqual(ab["p1"], (3, -4))
        self.assertEqual(ab["p2"], (7, 4))
        self.assertEqual(ab["mirror_p1"], (3, 4))
        self.assertEqual(ab["rotation_points"][1], (25, 0))
        ba = next(r for r in self.rows
                  if r["label"] == "4-3-5" and r["order"] == "ba")
        self.assertEqual(ba["p1"], (4, -3))

    def test_the_page_states_the_counts(self):
        page = (Path(__file__).resolve().parents[1] / "workbench" /
                "integer-cubic-catalogue.html").read_text(encoding="utf-8")
        self.assertIn("158", page)
        self.assertIn("316", page)
        self.assertIn("632", page)
        self.assertIn("3-4-5", page)
        self.assertIn("Infinity:", page)
        self.assertEqual(page.count('<figure class="card">'), 12)


if __name__ == "__main__":
    unittest.main()
