"""The cubic-native side list: the curves that qualify, and their links."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "g3-cubic-native.html"
SHOW = ROOT / "workbench" / "g3-showcase.html"
NOTES = ROOT / "workbench" / "g3-notes.html"


class TestCubicNative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.show = SHOW.read_text(encoding="utf-8")
        cls.notes = NOTES.read_text(encoding="utf-8")

    def test_the_counts(self):
        self.assertIn("Exact quintic→cubic elevations · 21", self.page)
        self.assertIn("Cubic by construction · 7", self.page)
        self.assertIn("Cubic source, not G3-qualified · 30", self.page)
        self.assertIn("26", self.page)

    def test_the_integer_rows_and_the_lac_are_listed(self):
        for key in ("integer cubic · 3-4-5", "integer cubic · 13-84-85",
                    "S44 · Fig. 6 · LAC"):
            with self.subTest(curve=key):
                self.assertIn(key, self.page)

    def test_the_four_showcase_cubic_panels_are_listed(self):
        for title in ("the cubic ogee", "the lattice cubic",
                      "the cubic wave", "the Gaussian bell"):
            with self.subTest(panel=title):
                self.assertIn(title, self.page)

    def test_every_note_link_resolves(self):
        for nid in set(re.findall(
                r'href="g3-notes\.html#([^"]+)"', self.page)):
            with self.subTest(note=nid):
                self.assertIn(f'id="{nid}"', self.notes)

    def test_every_figure_link_resolves(self):
        for fig in set(re.findall(
                r'href="g3-showcase\.html#(fig-\d+)"', self.page)):
            with self.subTest(figure=fig):
                self.assertIn(f'id="{fig}"', self.show)


if __name__ == "__main__":
    unittest.main()
