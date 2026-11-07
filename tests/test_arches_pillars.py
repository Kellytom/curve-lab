"""Arches and pillars: placement, mirror, and the verdict of the join."""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import arches_pillars as A  # noqa: E402


class TestArchesPillars(unittest.TestCase):
    def test_place_maps_the_ends(self):
        out = A.place([(0.0, 0.0), (3.0, 4.0)], (2.0, 1.0), (2.0, 5.0))
        self.assertAlmostEqual(out[0][0], 2.0)
        self.assertAlmostEqual(out[0][1], 1.0)
        self.assertAlmostEqual(out[-1][0], 2.0)
        self.assertAlmostEqual(out[-1][1], 5.0)

    def test_mirror_is_an_exact_flip(self):
        pts = [(0.0, 1.0), (2.0, 3.0)]
        self.assertEqual(A.mirror(pts), [(-0.0, 1.0), (-2.0, 3.0)])

    def test_a_vertical_line_has_no_crown_error(self):
        self.assertAlmostEqual(A.crown_off_vertical([(0.0, 0.0), (0.0, 1.0)]), 0.0)

    def test_the_join_classifies_the_sections(self):
        rows = {r["title"]: r for r in A.classify()}
        self.assertEqual(rows["cycloid, half arch"]["use"], "arch")
        self.assertEqual(rows["astroid, quadrant"]["use"], "arch")
        self.assertEqual(rows["integer cubic, half"]["use"], "arch")
        self.assertEqual(rows["log spiral"]["use"], "capital")
        self.assertEqual(rows["Euler, steep recovery"]["use"], "capital")
        self.assertEqual(rows["squircle, 45° arc"]["use"], "capital")
        # and the two that fit neither
        self.assertEqual(rows["Euler, two tangents"]["use"], "—")
        self.assertEqual(rows["circle, quarter"]["use"], "—")

    def test_arch_arrives_near_vertical(self):
        for row in A.classify():
            if row["use"] == "arch":
                with self.subTest(section=row["title"]):
                    self.assertLessEqual(row["crown"], A.ARCH_IF_CROWN)

    def test_capital_branches_outward(self):
        lo, hi = A.CAPITAL_IF_DIVERGE
        for row in A.classify():
            if row["use"] == "capital":
                with self.subTest(section=row["title"]):
                    self.assertGreaterEqual(row["div"], lo)
                    self.assertLessEqual(row["div"], hi)


if __name__ == "__main__":
    unittest.main()
