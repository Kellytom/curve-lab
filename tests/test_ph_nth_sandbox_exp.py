"""The experimental page: fractional exponents, and the gallery under it."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "ph-nth-sandbox-exp.html"
MATH = ROOT / "scripts" / "ph_math.js"


class TestFractionalSandbox(unittest.TestCase):
    def test_the_page_is_built_with_the_step_control(self):
        page = PAGE.read_text()
        for marker in ("Experiment: fractional exponents", "n-step", "exponent step",
                       "n-roots-ruler", "n-roots-fill"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)

    def test_the_page_keeps_the_gallery(self):
        """The operator's call, 2026-11-14: "the page should have a gallery".

        The page was written without one, so a curve under test could not sit
        among the ones we keep. That is reversed: the page opens on a found
        curve and the gallery is how the rest are reached. This test used to
        assert the opposite and was the last red in the suite.
        """
        page = PAGE.read_text()
        self.assertIn('id="n-gallery"', page)
        self.assertIn("window.phNthGallery", page)
        self.assertIn('document.getElementById("n-gallery")', page)

    def test_the_step_applies_from_the_first_draw(self):
        self.assertIn("window.phPowerStep = 0.5", PAGE.read_text())

    def test_the_maths_carries_a_step_and_falls_back_to_horner(self):
        maths = MATH.read_text()
        self.assertIn("phPowerStep", maths)
        self.assertIn("numericMetrics", maths)
        # the whole-power path must stay the Horner loop, or every other page moves
        self.assertIn("total = total * t + coefficients[i]", maths)

    def test_fractional_powers_have_no_grid_or_inflection_count(self):
        page = PAGE.read_text()
        self.assertIn("grid n/a: fractional powers", page)
        self.assertIn("inflections n/a: fractional powers", page)


if __name__ == "__main__":
    unittest.main()
