import unittest
from fractions import Fraction
from pathlib import Path

from curve_lab import pyth_cubic, pyth_g2

ROOT = Path(__file__).resolve().parents[1]


class PythG2Test(unittest.TestCase):
    def test_345_chain_is_integer_and_g2(self):
        data = pyth_g2.chain(pyth_cubic.case(3, 4, 5))
        self.assertEqual(data["scale"], 5)
        self.assertEqual(len(data["pieces"]), 3)
        for piece in data["pieces"]:
            self.assertEqual(len(piece), 4)
            self.assertTrue(all(isinstance(v, int) for p in piece for v in p))
        joins = pyth_g2.join_report(data)
        self.assertEqual([j["point"] for j in joins], [(0, 0), (50, 0)])
        self.assertTrue(all(j["g2"] for j in joins))
        self.assertTrue(all(j["tangent_match"] for j in joins))
        self.assertTrue(all(j["curvature_match"] for j in joins))
        self.assertEqual(joins[0]["tangent"], (15, -20))
        self.assertEqual(joins[0]["curvature_left"], Fraction(16, 375))
        self.assertEqual(joins[1]["curvature_left"], Fraction(-16, 375))

    def test_all_triples_pass(self):
        reports = pyth_g2.probe_all()
        self.assertEqual(len(reports), 10)
        for report in reports:
            self.assertTrue(report["g2"], report["label"])
            self.assertEqual(report["scale"],
                             int(report["label"].split("-")[2]))
            for join in report["joins"]:
                self.assertTrue(join["tangent_match"])
                self.assertTrue(join["curvature_match"])
                self.assertIsNotNone(join["curvature_left"])

    def test_page(self):
        page = (ROOT / "workbench" / "integer-g2.html").read_text(
            encoding="utf-8")
        self.assertIn("Integer G2 mirror chain", page)
        self.assertIn("Fig. G1", page)
        self.assertIn("G2 (0, 0)", page)
        self.assertIn("G2 (50, 0)", page)
        self.assertIn("10/10", page)
        self.assertIn("pass both joins", page)
        self.assertIn("Probe all ten triples", page)


if __name__ == "__main__":
    unittest.main()
