"""Guards the second W05 storey: parts, entasis, ground and aspects."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import storey_pillar as S  # noqa: E402


class PillarTest(unittest.TestCase):
    def setUp(self):
        self.page = (ROOT / "workbench" / "storey-pillar.html").read_text(
            encoding="utf-8")
        self.data = S.storey_data()

    def test_the_parts(self):
        d = self.data
        self.assertEqual(d["height"], 100.0)
        self.assertEqual(d["ground"], 0.0)
        self.assertEqual(d["axis_x"], 0.0)
        self.assertEqual(d["plinth_half"], 24.0)
        self.assertEqual(d["abacus_half"], 19.0)
        self.assertEqual(d["shaft_bottom_half"], 15.0)
        self.assertEqual(d["shaft_top_half"], 9.0)
        self.assertEqual(d["flutes"], 4)

    def test_the_profiles_are_integer_mirrors(self):
        for x, y in S.SHAFT_RIGHT:
            self.assertEqual((x, y), (int(x), int(y)))
        self.assertEqual(len(S.mirror(S.SHAFT_RIGHT)), len(S.SHAFT_RIGHT))
        for (lx, ly), (rx, ry) in zip(S.mirror(S.SHAFT_RIGHT), S.SHAFT_RIGHT):
            self.assertEqual(lx, -rx)
            self.assertEqual(ly, ry)

    def test_the_entasis_swells_above_the_base(self):
        self.assertGreater(self.data["waist_half"], self.data["shaft_bottom_half"])
        self.assertGreater(self.data["waist_y"], 20.0)
        self.assertLess(self.data["waist_y"], 50.0)
        self.assertIn("entasis", self.page)

    def test_the_aspects_and_ground(self):
        for word in ("Linearity", "Curve", "Infinity", "Grounded"):
            self.assertIn(word, self.page)
        self.assertIn("baseline at y = 0", self.page)
        self.assertIn("axis at x = 0", self.page)
        self.assertIn("ground", self.page.lower())
        self.assertIn("vertical", self.page.lower())

    def test_one_figure(self):
        self.assertEqual(self.page.count("<svg"), 1)


if __name__ == "__main__":
    unittest.main()
