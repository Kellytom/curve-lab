import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import levien_integer as L  # noqa: E402


class LevienIntegerTest(unittest.TestCase):
    def test_simple_families(self):
        f = L.families()
        self.assertEqual(f["parabola"]["source"], [(0, 0), (1, 1), (2, 4)])
        self.assertEqual(f["half"]["source"], [(0, 0), (2, 2)])
        self.assertEqual(f["quarter"]["source"], [(0, 0), (2, 1)])
        self.assertEqual(f["sixtyfourth"]["source"],
                         [(0, 0), (8, 1), (16, 4), (24, 9)])
        self.assertEqual(f["sixtyfourth"]["span"]["c1"], (8, 0))
        self.assertEqual(f["sixtyfourth"]["span"]["c2"], (16, 3))

    def test_success_cases(self):
        cases = L.success_cases()
        self.assertEqual(len(cases), 5)
        self.assertEqual(cases[0]["fig"], "G1")
        self.assertEqual(cases[0]["d"], 5)
        self.assertEqual(cases[0]["hits_plus"], [(21, 13)])
        self.assertEqual(cases[0]["hits_minus"], [(27, 5)])
        self.assertEqual(cases[-1]["fig"], "G5")
        self.assertEqual(cases[-1]["d"], 20)
        self.assertEqual(len(cases[-1]["points"]), 64)

    def test_page(self):
        page = (ROOT / "workbench" / "levien-integer.html").read_text(
            encoding="utf-8")
        self.assertEqual(page.count("<svg"), 30)
        self.assertIn("Levien integer sandbox", page)
        self.assertIn("half parabola", page)
        self.assertIn("quarter parabola", page)
        self.assertIn("integer lattice", page)
        self.assertIn("gold-dash", page)
        self.assertIn("fundamental concept", page)
        self.assertIn("curve fitting", page)
        self.assertIn("degree 10", page)
        self.assertIn("Raph Levien", page)
        self.assertIn("The mechanism, in formulas", page)
        self.assertIn("higher-degree", page)
        self.assertIn("a₄λ₀⁴", page)
        self.assertIn("1/15,625", page)
        self.assertIn("handles on a parabola", page)
        self.assertIn("B(p/q)", page)
        self.assertIn("tangent intersection", page)
        self.assertIn("Where the bounding-parabola idea lives", page)
        self.assertIn("raphlinus.github.io/issues/79", page)
        self.assertIn("pull/258", page)
        self.assertIn("EstParab", page)
        self.assertIn("y = x²/64", page)
        self.assertIn("integer points are (0,0), (8,1), (16,4), (24,9)", page)
        self.assertIn("Success gallery", page)
        self.assertIn("Fig. C1", page)
        self.assertIn("Fig. G1", page)
        self.assertIn("handles (16,0), (32,12)", page)
        self.assertIn("handles (48,0), (96,108)", page)
        self.assertIn("handles (168,0), (336,1323)", page)
        self.assertIn("exact integer offset hits", page)
        self.assertIn("(21,13)", page)
        self.assertIn("Domain note", page)
        self.assertNotIn("x²/24 · [0,12]", page)
        self.assertIn("not constrained to a", page)


if __name__ == "__main__":
    unittest.main()
