import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.euler_polygon import convert  # noqa: E402


def cycloid():
    return [(t - math.sin(t), 1 - math.cos(t))
            for t in (0.1 + (math.pi - 0.2) * i / 120 for i in range(121))]


class EulerPolygonTest(unittest.TestCase):
    def test_cycloid_section(self):
        r = convert(cycloid(), n=120, max_angle=0.2, width_factor=0.08)
        self.assertGreater(len(r["target"]), 100)
        self.assertEqual(len(r["polygon"]), len(r["target"]))
        self.assertGreater(r["alpha_deg"], 0.0)
        self.assertLess(r["poly_max"], 0.05 * r["size"])
        self.assertLess(r["cubic_max"], 0.10 * r["size"])
        self.assertGreater(len(r["turns"]), 100)
        self.assertEqual(len(r["left"]), len(r["right"]))
        self.assertEqual(len(r["left"]), len(r["polygon"]))

    def test_page(self):
        page = (ROOT / "workbench" / "euler-sections.html").read_text(
            encoding="utf-8")
        self.assertEqual(page.count("<svg"), 6)
        self.assertIn("p-triple", page)
        self.assertIn("rational", page)
        self.assertIn("Cycloid", page)
        self.assertIn("Squircle", page)
        self.assertIn("cubic seam", page)


if __name__ == "__main__":
    unittest.main()
