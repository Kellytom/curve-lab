"""The tracked figure fixes: no red tight rings in the gallery, cusp counts.

`state/G3-FIXES-int.md` is the human-readable list. This test is the machine
check that the listed fixes are present in the generated showcase.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "g3-showcase.html"
LOG = ROOT / "state" / "G3-FIXES-int.md"

KEYS = (
    "S44 · Fig. 6 · LAC: p = 0, turn 270",
    "Stage II · Fig. 11 · Arc, Euler, line, Euler, arc · spine 3",
    "Stage II · Fig. 13 · Log spiral, one turn each way · spine 3",
    "Stage II · Fig. 14 · Involute, one turn each way · spine 3",
    "Stage II · Fig. 16 · Log spiral, two turns each way · spine 2",
    "Stage II · Fig. 19 · Log spiral, both ends · spine 3",
    "Stage II · Fig. 20 · Involute, both ends · spine 3",
    "Stage II · Fig. 5 · The S branch · spine 3",
    "Stage II · Fig. 5 · The S branch · spine 5",
    "Stage II · Fig. 6 · The S root · spine 4",
    "Stage II · Fig. 6 · The S root · spine 6",
    "misc · Maclaurin trisectrix · exact loop",
    "misc · Pell · x² − 2y² = 1 · +",
    "misc · Pell · x² − 2y² = 1 · −",
    "misc · Reuleaux triangle",
    "misc · catenary",
    "heart · Eisemann lower",
    "heart · Hechinger lower",
    "heart · Kuriscak lower",
    "heart · Mangaldan",
    "heart · Valentine",
    "heart · |x|^(2/3) lower",
    "heart · |x|^(2/3) upper",
)


class TestG3Fixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.log = LOG.read_text(encoding="utf-8")
        cls.gallery = cls.page.split('id="every-curve"')[1]

    def test_the_gallery_has_no_red_tight_rings(self):
        self.assertEqual(self.gallery.count("#e01b1b"), 0)

    def test_the_contents_links_to_the_gallery(self):
        self.assertIn('href="#every-curve"', self.page)
        self.assertIn("Every complete curve ·", self.page)

    def test_every_reported_curve_is_present_and_logged(self):
        for key in KEYS:
            with self.subTest(curve=key):
                self.assertIn(key, self.page)
                self.assertIn(key, self.log)

    def test_the_cusp_counts_are_stated(self):
        for count in ("cusp ×2", "cusp ×3", "cusp ×4",
                      "cusp ×5", "cusp ×6"):
            with self.subTest(count=count):
                self.assertIn(count, self.page)
                self.assertIn(count, self.log)

    def test_the_hearts_are_declared(self):
        for key in ("heart · Eisemann lower", "heart · Hechinger lower",
                    "heart · Kuriscak lower", "heart · Mangaldan",
                    "heart · Valentine", "heart · |x|^(2/3) lower",
                    "heart · |x|^(2/3) upper"):
            with self.subTest(curve=key):
                self.assertIn(key, self.page)


if __name__ == "__main__":
    unittest.main()
