"""The experimental page: fractional exponents, and the gallery under it."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "ph-nth-sandbox-exp.html"
MATH = ROOT / "scripts" / "ph_math.js"
PANELS = ROOT / "scripts" / "ph_nth_panels.js"


class TestFractionalSandbox(unittest.TestCase):
    def test_the_four_buttons_are_wired_to_the_dropdown(self):
        """2026-11-15: every pattern button went dead for every dropdown choice.

        Rewriting the widen control replaced a span of the file that also held the
        listener block, so the buttons were in the page with nothing behind them.
        These three markers are the wiring: the selector, the row table and the call.
        """
        panels = PANELS.read_text()
        for marker in ('document.querySelectorAll(".tweak-step").forEach',
                       "const patternRows = { x1:",
                       "applyPattern(key, row(), Number(button.dataset.step));"):
            with self.subTest(marker=marker):
                self.assertIn(marker, panels)

    def test_the_focus_switch_has_two_copies_that_cannot_disagree(self):
        """One switch in the view panel, one under the figure: both must stay in step.

        They read and write view.focusKnot, and the same paint function sets the word
        and aria-pressed on both, so a reset or a press cannot leave one stale.
        """
        page = PAGE.read_text()
        self.assertIn('id="n-focus-knot-hud"', page)
        self.assertIn('id="n-focus-knot"', page)
        panels = PANELS.read_text()
        self.assertIn('const focusButtons = ["n-focus-knot", "n-focus-knot-hud"]', panels)
        self.assertIn("paintFocus();", panels)
        self.assertIn('["n-focus-knot-hud", () => view.focusKnot]', panels)

    def test_a_saved_curve_keeps_its_flat_spots_and_its_loop(self):
        """Downloaded JSON must describe the curve well enough to restore the ruler."""
        panels = PANELS.read_text()
        self.assertIn('const field = document.getElementById("n-roots");\n        return field ? field.value.trim() : "";', panels)
        self.assertIn("loop: (() => { const [from, to] = loopWindow();", panels)
        self.assertIn("tRange: { from: range.from, to: range.to },", panels)

    def test_the_page_and_the_scripts_sample_t_the_same_way(self):
        """One sampling rule, so a count means the same thing in both places.

        2026-11-15: the page said 8 where the script said 9, because the page ran a
        separate crossing routine over a decimated copy. Both now use 1024 intervals
        and the parameter routine that skips the neighbouring segments.
        """
        panels = PANELS.read_text()
        self.assertIn("function spineSamples(speed, n = 1024) {", panels)
        self.assertIn("const selfCrossings = crossingParams(spinePoints, crossTolerance);", panels)
        self.assertNotIn("decimate(spinePoints), decimate(spinePoints)", panels)

    def test_the_loop_button_reads_its_window_from_the_crossings(self):
        """The window is not one constant: three outer fractions push the knot outward.

        A fixed 0.02 cut suits 1/15 and clips the outermost meeting on 1/9, so the
        button measures the crossing parameters and pads them by 2 per cent. The
        window also travels in the record as `loop`, so a saved curve keeps it.
        """
        panels = PANELS.read_text()
        self.assertIn("function loopWindow()", panels)
        self.assertIn("const params = crossingParams(points, 1e-4);", panels)
        self.assertIn("loop: (() => { const [from, to] = loopWindow();", panels)
        self.assertIn("const [lo, hi] = fixed || loopWindow();", panels)
        page = PAGE.read_text()
        self.assertIn('id="n-loop-only"', page)
        self.assertIn('id="n-whole-curve"', page)

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
        self.assertIn('<option value="13">', page)

    def test_the_point_count_is_labelled_as_a_drawing_detail(self):
        """The visible-part count is a rendering number, not a curve measurement.

        The operator's call, 2026-11-16: small print beside it, and a section on the
        notes page, so it is never mistaken for something the cubic spans are read from.
        """
        page = PAGE.read_text()
        self.assertIn('id="n-zoom-detail-fineprint"', page)
        self.assertIn("not part of formula", page)
        self.assertIn('href="ph-nth-exp-notes.html"', page)
        notes = (ROOT / "workbench" / "ph-nth-exp-notes.html").read_text()
        self.assertIn("The point count is not part of the formula", notes)
        for word in ("visible part", "recalculate at this zoom", "G3 gate"):
            with self.subTest(word=word):
                self.assertIn(word, notes)

    def test_the_census_covers_its_stated_box(self):
        """Exhaustive within a box that is written down, not "all curves" full stop.

        1-3 outer pairs, denominators 2-20, 1-5 copies at 1/2. Measured 2026-11-16:
        7,695 root sets, 7,068 distinct curves, best 19 crossings.
        """
        census = json.loads((ROOT / "workbench" / "family-census.json").read_text())
        self.assertEqual(census["tested"], 7695)
        self.assertEqual(len(census["curves"]), 7068)
        self.assertIn("denominators 2-20", census["box"])
        best = max(curve["crossings"] for curve in census["curves"])
        self.assertEqual(best, 19)
        for curve in census["curves"][:50]:
            for key in ("spots", "outer", "copies", "crossings", "grid", "arc"):
                self.assertIn(key, curve)

    def test_the_related_families_sit_below_the_seven_and_above_the_gallery(self):
        """Two outer spots and their mirrors, three at 1/2: seven spots, a t^7 row.

        Each button carries the crossing count this page's own counter gives, so the
        label and the readout must agree; measured 11, 10, 10, 8, 8, 6, 5.
        """
        page = PAGE.read_text()
        self.assertIn('id="n-related"', page)
        self.assertIn("Related families: two outer flat spots", page)
        self.assertLess(page.index('id="n-families"'), page.index('id="n-related"'))
        self.assertLess(page.index('id="n-related"'), page.index("<h2>Found curves</h2>"))
        for label, spots in (("1/15 + 1/12 &middot; 9 crossings",
                              "1/15, 1/12, 1/2, 1/2, 1/2, 11/12, 14/15"),
                             ("1/17 + 1/4 &middot; 7 crossings",
                              "1/17, 1/4, 1/2, 1/2, 1/2, 3/4, 16/17")):
            with self.subTest(label=label):
                self.assertIn(label, page)
                self.assertIn(f'data-spots="{spots}"', page)

    def test_a_loaded_curve_brings_its_flat_spots_back(self):
        """The ruler must describe the curve that is loaded, not the one before it.

        Gallery entries carry `roots`; the load puts them in the field and on the
        strip, and a curve with no recorded spots clears the strip rather than
        leaving the last curve's dots underneath.
        """
        page = PAGE.read_text()
        self.assertIn('"roots":"1/3, 1/3, 1/2, 1/2, 1/2, 2/3, 2/3"', page)
        panels = PANELS.read_text()
        self.assertIn('rootsFieldNow.value = (item && item.roots) || "";', panels)
        self.assertIn("crosses itself ${selfCrossings.length}", panels)

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
        self.assertIn("document.querySelectorAll('.family')", page)

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

    def test_a_whole_power_row_is_measured_even_on_a_half_step(self):
        """It said "grid n/a: fractional powers" with no fractional power in use.

        The step was 1/2 and every number sat on a whole power, so the row was a
        plain polynomial and the grid existed. A folded row must also be padded to
        a common length: a constant x row folds to one number, and the grid is read
        off the squared rows, so a short row cut the powers off the end of that
        product and reported grid 1/1.
        """
        maths = MATH.read_text()
        self.assertIn("function foldToWholePowers(row, step)", maths)
        self.assertIn("if (!foldedX || !foldedY) return numericMetrics(speedX, speedY);", maths)
        self.assertIn("const pad = row => row.concat(new Array(longest - row.length).fill(0));", maths)
        # the words stay for a number that really is on a fractional power
        self.assertIn("grid n/a: fractional powers", PANELS.read_text())

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
