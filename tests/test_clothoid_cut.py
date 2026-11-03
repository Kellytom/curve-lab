import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import clothoid_cut as C  # noqa: E402
import hearts as H  # noqa: E402


class ClothoidCutTest(unittest.TestCase):
    def test_table_contact_is_close(self):
        pts = H.clothoid(s_max=C.S, n=C.N)
        full = [(x, y) for _, x, y in pts] + [(-x, -y) for _, x, y in pts]
        _, _, _, y1, y2 = C.table_contact(full)
        gap = y2 - y1
        self.assertGreater(gap, 0.0)
        self.assertLess(gap, 0.001)
        deg = math.degrees(C.TABLE_PHI) % 360
        self.assertAlmostEqual(min(deg, 360 - deg), 38.456, places=2)

    def test_page_has_full_table_figure(self):
        page = (ROOT / "workbench" / "clothoid-cut.html").read_text(
            encoding="utf-8")
        self.assertIn("Fig. 5 · the full pair on a table", page)
        self.assertIn("38.5° CW", page)
        self.assertIn("table contact", page)
        self.assertNotIn("one half only", page)


if __name__ == "__main__":
    unittest.main()
