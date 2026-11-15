"""The experimental page: fractional exponents, and the gallery under it."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "ph-nth-sandbox-exp.html"
MATH = ROOT / "scripts" / "ph_math.js"


class TestFractionalSandbox(unittest.TestCase):
    def test_the_tweak_panel_is_a_dropdown_and_four_buttons(self):
        """One dropdown picks the change; four buttons press it in either direction.

        The operator's call, 2026-11-14: "a drop down of the different options ...
        and then a button to nudge (1) or bump (5) that does the change each time
        it is pressed", plus a minus set for subtracting the same pattern.
        """
        page = PAGE.read_text()
        self.assertIn('id="n-tweak-pattern"', page)
        for pattern in ("x: t1, t2", "x: t2 to t4", "x: t3 to t6",
                        "y: t1 to t3", "y: t2 to t5"):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, page)
        for step in ('data-step="-5"', 'data-step="-1"', 'data-step="1"', 'data-step="5"'):
            with self.subTest(step=step):
                self.assertIn(step, page)
        self.assertIn('id="n-tweak-spread"', page)
        self.assertIn('<option value="39">', page)

    def test_the_seven_families_come_before_the_found_curves(self):
        """Seven families above the line; the found curves stay below it, for later.

        One outer flat spot, its mirror and three copies at 1/2: five spots, so a
        t^5 row. Clicking one writes those spots into the field and presses the
        same "fill from the dots" the operator presses.
        """
        page = PAGE.read_text()
        for family in ("1/15", "1/14", "1/13", "1/12", "1/11", "1/10", "1/9"):
            with self.subTest(family=family):
                self.assertIn(f'data-spots="{family}, 1/2, 1/2, 1/2, ', page)
        self.assertLess(page.index('id="n-families"'),
                        page.index("<h2>Found curves</h2>"),
                        "the families must sit above the found curves")
        self.assertIn("<hr", page)
        self.assertIn("#n-family-buttons .family", page)

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
