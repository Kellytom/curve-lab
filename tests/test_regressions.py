"""Fixed bugs, each with the check that keeps it fixed.

A bug that was fixed once and is discovered again is a process failure, not bad
luck. Every user-visible fault that took real work to fix gets a test here, named
after the fault, and a row in `state/REGRESSIONS-int.md`. The rule: fix and test
land in the same commit, and nothing in here is deleted because a change made it
awkward — an awkward test is the point.

These checks read the generators and the built pages rather than driving a
browser, so they run in the fast suite. Browser-level proof lives in
`scripts/check-nth-page.mjs` and `scripts/phase1_checks` style gates.
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import curve_records as R  # noqa: E402

PANELS = ROOT / "scripts" / "ph_nth_panels.js"
TEMPLATE = ROOT / "scripts" / "ph_nth_sandbox.py"
EXP = ROOT / "scripts" / "ph_nth_sandbox_exp.py"
FOUND = ROOT / "workbench" / "found-curves.json"
PAGE2 = ROOT / "workbench" / "ph-nth-sandbox-2.html"


class TestRegressions(unittest.TestCase):
    def test_the_half_power_boxes_are_never_removed_by_the_starter(self):
        """2026-11-14: the default curve loading at step 1 deleted every 1/2 box."""
        source = EXP.read_text()
        start = source.index("starter = (")
        starter = source[start:source.index("</body></html>", start)]
        self.assertIn("step.value = '0.5'", starter)
        self.assertNotIn("step.value = '1'", starter)

    def test_a_power_lands_in_its_own_box_not_the_next_one(self):
        """2026-11-14: rows were written straight in, so a whole-power curve at
        step 1/2 sat in the half-power boxes and drew the wrong curve."""
        (x, y), refused = R.rows_for_step([R.term(0, 1, -8), R.term(1, 0, 129), R.term(2, 0, -663)], 0.5)
        self.assertEqual(refused, [])
        self.assertEqual(y, [-8, 0, 129, 0, -663])

    def test_stored_curves_keep_terms_and_drop_flat_rows(self):
        """2026-11-14: two sources of truth (row position and power) disagreed."""
        document = R.read(FOUND)
        self.assertEqual(R.validate(document), [])
        for curve in document["curves"]:
            self.assertNotIn("speedX", curve)
            self.assertNotIn("speedY", curve)

    def test_the_build_stamp_sits_at_the_foot_and_is_current(self):
        """2026-11-14: a stale page looked like a broken page."""
        template = TEMPLATE.read_text()
        self.assertIn('<p class="small mono" id="n-build">build __BUILD__</p>', template)
        self.assertIn("def stamped(page)", template)

    def test_every_speed_number_still_has_two_sliders(self):
        """2026-11-14: the decade slider went missing, leaving one slider per number."""
        panels = PANELS.read_text()
        self.assertIn("decade.className = \"decade\"", panels)
        self.assertIn("pair.append(number, fine, decade, flip, scales)", panels)

    def test_the_ladder_still_reaches_thirty_numbers(self):
        """2026-11-14: halving the step halved the top power until the rows doubled."""
        template = TEMPLATE.read_text()
        self.assertIn('data-speed-degree="14"', template)
        self.assertIn("degree 29", template)

    def test_an_open_gallery_cell_draws_one_curve_only(self):
        """2026-11-14: a found curve was drawn twice, thumbnail plus panel."""
        template = TEMPLATE.read_text()
        self.assertIn(".gallery figure.open>svg{display:none}", template)

    def test_the_knotlike_section_still_opens_with_the_operators_curves(self):
        """2026-11-14: position-based ordering re-shuffled the section on its own."""
        page = PAGE2.read_text()
        names = json.loads(re.search(r"window\.phNthKnots = (\[.*?\]);", page, re.S).group(1))
        self.assertEqual(names[:7], ["wave3", "knot", "bud", "knot-2", "hersheys copy",
                                     "wave-1of7-1of5-1-bow9"] + names[6:7])

    def test_the_ordering_rules_name_curves_rather_than_positions(self):
        """2026-11-14: adding one curve shifted every number and re-ordered the page."""
        source = (ROOT / "scripts" / "ph_nth_sandbox2.py").read_text()
        self.assertIn('DEMOTE = ("wave5"', source)
        self.assertIn('AFTER = "wave-1of3-2"', source)

    def test_a_fractional_step_reports_no_grid_and_no_inflection_count(self):
        """2026-11-14: the page claimed a grid that does not exist off whole powers."""
        self.assertIn("grid n/a: fractional powers", PANELS.read_text())
        self.assertIn("inflections n/a: fractional powers", PANELS.read_text())

    def test_the_readout_still_reports_knot_and_leg_shares(self):
        """2026-11-14: 'make the knot bigger' had no number to steer by."""
        self.assertIn("knot ${knotShare}% legs ${legShare}%", PANELS.read_text())

    def test_the_nudge_buttons_offer_only_whole_steps(self):
        """2026-11-14: a size of 1/3 took the grid from 3,465 to 8.7e13, because a
        third cannot be written exactly in machine arithmetic.

        Amended the same day on the operator's call: the free-text size field and
        the share-of-the-pair dial are gone, replaced by one dropdown of patterns
        and four press-buttons. A fraction cannot be typed at all now, so the
        hazard is gone by construction rather than by an offered list.
        """
        source = EXP.read_text()
        self.assertNotIn('id="n-tweak-size"', source)
        self.assertNotIn("n-tweak-divisor", source)
        for step in ('data-step="-5"', 'data-step="-1"', 'data-step="1"', 'data-step="5"'):
            with self.subTest(step=step):
                self.assertIn(step, source)
        for spread in ('<option value="13">', '<option value="39">'):
            with self.subTest(spread=spread):
                self.assertIn(spread, source)

    def test_the_flat_spots_fill_whole_power_boxes(self):
        """2026-11-14: pressing fill at step 1/2 wrote the knot into the half-power
        boxes, so the button drew a different curve from the one it named."""
        panels = PANELS.read_text()
        fill = panels[panels.index("function fillFromFlatSpots()"):]
        fill = fill[:fill.index("writeCells();")]
        self.assertIn("rowsFromTerms(terms)", fill)
        self.assertNotIn("padRow([bow.d, bow.n, -bow.n], count)", fill)

    def test_loading_a_curve_does_not_change_the_exponent_step(self):
        """2026-11-14: loading used to reset the step, silently changing the curve."""
        panels = PANELS.read_text()
        load = panels[panels.index("window.phNthLoad = item =>"):panels.index("window.phNthLoad = item =>") + 400]
        self.assertNotIn("phPowerStep = 1", load)


if __name__ == "__main__":
    unittest.main()
