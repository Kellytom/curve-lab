"""Guards the modulated-width proof: the law, the seam, the no-fold claim."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import modulated_width_proof as M  # noqa: E402


class ModulatedWidthProofTest(unittest.TestCase):
    def setUp(self):
        self.page = (ROOT / "workbench" / "modulated-width-proof.html").read_text(
            encoding="utf-8")
        self.data = M.proof_data()

    def test_the_width_ratio_and_seam(self):
        self.assertAlmostEqual(self.data["ratio"], 1.6, 6)
        self.assertAlmostEqual(self.data["seam"][0], 1.0, 9)
        self.assertAlmostEqual(self.data["seam"][1], 1.0, 9)
        self.assertAlmostEqual(self.data["deviation"], 0.3, 6)
        self.assertIn("1.600", self.page)

    def test_the_rails_match_the_law_and_do_not_fold(self):
        self.assertLess(self.data["sep_error"], 1e-12)
        self.assertEqual(self.data["hits_left"], 0)
        self.assertEqual(self.data["hits_right"], 0)
        self.assertIn("not equidistant", self.page.lower())

    def test_the_rule_is_stated(self):
        self.assertIn("2 × parallel", self.page)
        self.assertIn("not a parallel offset", self.page.lower())
        self.assertIn("w(0) = 1.000000", self.page)


if __name__ == "__main__":
    unittest.main()
