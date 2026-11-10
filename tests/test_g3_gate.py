"""The gate-tiers page: the strict count, the source row, and near-G3."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "g3-gate.html"
SHOW = ROOT / "workbench" / "g3-showcase.html"


class TestGateTiers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.show = SHOW.read_text(encoding="utf-8")

    def test_the_page_states_the_counts(self):
        self.assertIn("strict G3 count is unchanged: <strong>154</strong>",
                      self.page)
        self.assertIn("Near-G3, not G3 · 9", self.page)
        self.assertIn("Fail even near-G3 · 21", self.page)
        self.assertIn("S44", self.page)
        self.assertIn("S40", self.page)

    def test_the_tiers_are_shown(self):
        for phrase in ("exact", "source-precision", "near-G3",
                       "1e-09", "1e-05", "5e-04"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.page)

    def test_the_showcase_links_to_the_tiers(self):
        self.assertIn('href="g3-gate.html"', self.show)


if __name__ == "__main__":
    unittest.main()
