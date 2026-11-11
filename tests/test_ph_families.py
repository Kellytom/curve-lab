"""The PH family gallery: one illustration per rung, plus the not-built list."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "ph-families.html"


class TestPHFamilies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")

    def test_the_degree_ladder(self):
        self.assertIn("n = deg h + 2·max(deg u, deg v) + 1", self.page)
        self.assertIn("h=1, u,v linear → 3", self.page)
        self.assertIn("h linear, u,v linear → 4", self.page)
        self.assertIn("h=1, u,v quadratic → 5", self.page)
        self.assertIn("h quadratic, u,v linear → 5", self.page)
        self.assertIn("h linear, u,v quadratic → 6", self.page)
        self.assertIn("h=1, u,v cubic → 7", self.page)

    def test_every_built_family_is_illustrated(self):
        for title in ("n = 3 · Tschirnhausen PH cubic",
                      "n = 4 · PH quartic",
                      "n = 5 · PH quintic 1",
                      "n = 5 · PH quintic 2",
                      "n = 5 · PH quintic 3",
                      "n = 6 · PH sextic",
                      "n = 7 · PH septic",
                      "n = 2 rational · the circle"):
            with self.subTest(title=title):
                self.assertIn(title, self.page)

    def test_the_non_ph_integer_cubic_is_shown_for_contrast(self):
        self.assertIn("n = 3 · integer cubic 3-4-5", self.page)
        self.assertIn("not PH", self.page)
        self.assertIn("no rational offset", self.page)

    def test_the_not_built_list(self):
        for phrase in ("Not made yet", "general", "PH quintic Hermite",
                       "C² PH spline", "n=8+", "rational PH beyond the circle"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.page)

    def test_the_illustrations_are_present(self):
        self.assertEqual(self.page.count('<div class="ph-card'), 9)
        self.assertEqual(self.page.count("<svg "), 9)


if __name__ == "__main__":
    unittest.main()
