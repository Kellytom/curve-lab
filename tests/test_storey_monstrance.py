"""Guards the first W05 storey: parts, rays, ground and aspects."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import storey_monstrance as S  # noqa: E402


class MonstranceTest(unittest.TestCase):
    def setUp(self):
        self.page = (ROOT / "workbench" / "storey-monstrance.html").read_text(
            encoding="utf-8")
        self.data = S.storey_data()

    def test_the_parts_and_rays(self):
        self.assertEqual(self.data["rays"], 24)
        self.assertEqual(self.data["head_radius"], 24.0)
        self.assertEqual(self.data["host_radius"], 12.0)
        self.assertGreater(self.data["stem"], 70.0)
        self.assertIn("24 rays", self.page)
        self.assertIn("p-triple", self.page)

    def test_the_aspects_and_ground(self):
        for word in ("Linearity", "Curve", "Infinity", "Grounded"):
            self.assertIn(word, self.page)
        self.assertIn("baseline at y = 0", self.page)
        self.assertIn("stem on x = 0", self.page)
        self.assertIn("ground", self.page.lower())
        self.assertIn("vertical", self.page.lower())

    def test_one_figure(self):
        self.assertEqual(self.page.count("<svg"), 1)


if __name__ == "__main__":
    unittest.main()
