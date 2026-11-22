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
import shutil
import subprocess
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
        hazard is gone by construction rather than by an offered list. The widened
        ink is refitted to whole numbers at the same degree, so it cannot move the
        grid either.
        """
        source = EXP.read_text()
        self.assertNotIn('id="n-tweak-size"', source)
        self.assertNotIn("n-tweak-divisor", source)
        for step in ('data-step="-5"', 'data-step="-1"', 'data-step="1"', 'data-step="5"'):
            with self.subTest(step=step):
                self.assertIn(step, source)
        for spread in ('<option value="3"', '<option value="8"', '<option value="13"'):
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

    def test_the_figure_index_names_every_registry_curve(self):
        """2026-11-19: "the gallery is empty" — `curve_pngs.mjs --only` wrote the
        index from the two curves it had just drawn, so 270 entries vanished.

        The script now merges; this reads the two files so a partial run cannot
        quietly shrink the gallery again.
        """
        registry = json.loads((ROOT / "workbench" / "curve-registry.json").read_text())
        index = json.loads((ROOT / "app" / "public" / "figures" / "index.json").read_text())
        wanted = {record["uid"] for record in registry["curves"]}
        indexed = {meta["uid"] for meta in index["curves"]}
        self.assertEqual(sorted(wanted - indexed), [], "registry curves with no figure")

    def test_the_plates_are_not_parallel_curves(self):
        """2026-11-20, the operator: "I CANT BELIEVE WE ARE DEALING WITH PARALLEL
        CURVE". They were right twice: the plate read a decision file that no longer
        existed, and its row builder carried a duplicate `character:` key whose second
        copy set plus and minus to 0 — a plain parallel offset — whatever the desk said.

        The law now lives in `scripts/lib/plate-row.mjs`, and its own test measures the
        two rails: the guarded side must widen along the curve, the other must not move
        much, and zero character must be the only parallel case.
        """
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "plate-row.test.mjs")],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)



class SpanWidthTraceTest(unittest.TestCase):
    """The desk records name their traces with the layer baked in ("ink/a") and
    carry a width; the constructor refused that combination ("a cubic span trace
    is a hairline"), so every saved desk piece was un-buildable through the
    normal model, and the rails-from-spans capability was unreachable. The
    refusal is removed; build_piece's pre-built path builds the rails and
    reports the fit error; the layer is not doubled when the name already
    carries it."""

    def test_a_span_trace_may_carry_a_width_and_build_its_rails(self):
        import json
        import subprocess
        from pathlib import Path as PathLib
        sys_path = str(PathLib(__file__).resolve().parents[1])
        program = """
import json, sys
sys.path.insert(0, '.')
from curve_lab.model import Design, Segment
from curve_lab.piece import Piece, Trace, build_piece
def ribbon(x, y, length=60.0, angle=0.0, kd=0.0, kappa0=0.005):
    return Design(name="ribbon", segments=[Segment(kd=kd, length=length, kappa0=kappa0)],
                  anchor={"x": x, "y": y, "angle": angle})
groups0, _ = build_piece(Piece(name="src", stroke=0.6, traces=[
    Trace("a", ribbon(0, 0, kd=0.01, kappa0=0.005), width=3.0)]), tol=0.02)
spine_spans = [dict(s) for s in groups0[0].spans]
piece = Piece(name="desk", stroke=0.6, traces=[
    Trace("ink/a", spans=[dict(s) for s in spine_spans], width=3.0,
          terminals=("round", "point"))])
groups, info = build_piece(piece, tol=0.02)
roles = [g.role for g in groups]
assert roles.count("rail") == 2, roles
assert roles.count("cap") == 2, roles
assert roles.count("spine") == 1, roles
assert info["fit_ok"], info["traces"]
assert groups[0].name == "ink/a start round", groups[0].name
assert next(g for g in groups if g.role == "rail").instance == "ink/a"
print("ok")
"""
        run = subprocess.run([sys.executable, "-c", program], capture_output=True,
                             text=True, cwd=sys_path)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)


class DevServerHostTest(unittest.TestCase):
    def test_the_dev_server_answers_on_ipv4_loopback(self):
        """Every browser check failed with `net::ERR_CONNECTION_REFUSED at
        http://127.0.0.1:4321/` while `curl localhost:4321` answered: a fresh
        `npm --prefix app run dev` bound Astro's `localhost` (IPv6 ::1) only, so
        every documented 127.0.0.1 link and every check that uses it was refused.
        The dev script must name the IPv4 loopback."""
        package = json.loads((ROOT / "app" / "package.json").read_text())
        self.assertIn("--host 127.0.0.1", package["scripts"]["dev"])


class SideCurveOffsetTest(unittest.TestCase):
    def test_the_offset_curves_are_equal_on_both_sides(self):
        """The operator, 2026-11-21: "it looks like you just took the original curve and scaled
        it... the offset curves should look the same on both sides of the curve, not thin on the
        right and wide on the left... if the difference at the end is 10x 10y, then move the
        starting position by 5 x and 5 y to balance." The two sides take one strength (the
        average of plus and minus); the profile is zero at both ends, so the start and end gaps
        are equal. The next session moves the curve's starting point where they are not."""
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "plate-offset.test.mjs")],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
