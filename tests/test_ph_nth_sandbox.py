"""The eleventh-power page: generated from the checked-in JavaScript."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from tests.stamps import without_build_stamp  # noqa: E402
PAGE = ROOT / "workbench" / "ph-nth-sandbox.html"
JS = ROOT / "scripts" / "ph_nth_panels.js"


class TestNthSandbox(unittest.TestCase):
    def test_the_ruler_runs_to_the_middle_and_mirrors_back_from_one(self):
        """0 to 1/2 across the page, then 1 to 1/2 under it, so 1/19 and 1/20 split.

        The strip used to read 0 to 1 across the box, which put 1/19 and 1/20
        about 2.6 px apart on a 1030 px page and left the odd denominators
        unreadable. Doubling the scale puts them 6.4 px apart, and the mirror
        strip shows 18/19 directly under 1/19.
        """
        page = PAGE.read_text()
        for marker in ('class="ruler-strip ruler-lower"',
                       'class="ruler-strip ruler-upper"',
                       "RULER_SPAN = 200",
                       "16, 17, 18, 19, 20]",
                       "drawTick(upperStrip, at, false);"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)

    def test_the_readout_names_the_last_number_not_the_last_box(self):
        """Five spots give a t^5 row in fifteen boxes; saying t^14 is a lie.

        The panel reported the last box of the rung as the top power, so a curve
        whose numbers stop at t^5 appeared to run to t^14 and looked truncated.
        """
        page = PAGE.read_text()
        self.assertIn("boxes in use", page)
        self.assertIn("const filled = Math.max(topUsed(state.y), topUsed(state.x)) + 1;", page)

    def test_the_page_holds_the_degree_11_sandbox(self):
        page = PAGE.read_text()
        for marker in ("n-controls", "n-plot", "n-close", "n-open",
                       "n-open-value", "n-json", "n-saved", "n-paste",
                       "n-rotate", "n-rails", "n-character", "n-char-l", "n-char-r", "n-prof", "n-shear", "n-hook", "n-hook-y", "euler-hook", "n-terminal-start", "n-terminal-end", "n-d", "n-rename", "amper",
                       "ph-nth-serif-notes.html", "n-gallery", "phNthGallery", "integer-105", "integer-70",
                       "Build from flat spots", "n-roots", "n-bow", "n-roots-fill", "n-roots-preset",
                       "n-roots-ruler", "n-roots-mirror", "n-roots-undo", "n-roots-clear",
                       "The eleventh power", "degree 11"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)

    def test_the_page_inlines_the_checked_in_javascript(self):
        page = PAGE.read_text()
        self.assertIn(JS.read_text().strip()[:200], page)
        self.assertIn("window.recipeMetrics", page)   # the shared maths came along

    def test_the_javascript_parses(self):
        result = subprocess.run(["node", "--check", str(JS)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_the_generator_reproduces_the_page(self):
        before = PAGE.read_text()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "ph_nth_sandbox.py")],
                       check=True, capture_output=True)
        self.assertEqual(without_build_stamp(PAGE.read_text()),
                         without_build_stamp(before),
                         "the page is not what scripts/ph_nth_sandbox.py emits")

    def test_the_serif_notes_page_is_generated_too(self):
        notes = ROOT / "workbench" / "ph-nth-serif-notes.html"
        self.assertTrue(notes.exists())
        text = notes.read_text()
        for marker in ("appendixOf", "residual", "ph-nth-sandbox.html", "window.polynomialValue",
                       "chord-bars"):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_the_law_and_the_formula_are_named_as_different_things(self):
        """The operator's split: a specification says what, a representation says how."""
        text = (ROOT / "workbench" / "ph-nth-serif-notes.html").read_text()
        paragraphs = text.split("<p")[1:]
        together = [part for part in paragraphs
                    if "specification" in part and "representation" in part]
        self.assertTrue(together,
                        "no paragraph holds both 'specification' and 'representation'")

    def test_the_two_tables_and_every_figure_are_numbered(self):
        text = (ROOT / "workbench" / "ph-nth-serif-notes.html").read_text()
        for marker in ("id=\"lac-membership\"", "id=\"ph-carry\"",
                       "Table 1", "Table 2", "Fig. 1", "Fig. 2"):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_the_carry_table_is_computed_not_typed(self):
        """Table 2 must be what scripts/ph_carry.py produces, to five places."""
        sys.path.insert(0, str(ROOT / "scripts"))
        import ph_carry
        text = (ROOT / "workbench" / "ph-nth-serif-notes.html").read_text()
        for name, fn in (("involute", ph_carry.involute),
                         ("log spiral", ph_carry.log_spiral)):
            points = ph_carry.target_points(fn, samples=240)
            for degree in (3, 9):
                real, imag = ph_carry.fit_speed(points, degree)
                carried = ph_carry.ph_points(real, imag, samples=240)
                cell = f"{ph_carry.deviation(carried, points[1:]):.5f}"
                with self.subTest(target=name, degree=degree):
                    self.assertIn(cell, text)

    def test_the_degree_ladder_is_written_once(self):
        text = JS.read_text()
        self.assertIn("let speedDegree = Number.isFinite(asked) && asked >= 1 ? Math.round(asked) : 5;", text)
        self.assertIn("const positionDegree = () => 2 * speedDegree + 1;", text)
        self.assertIn("window.phNthSetDegree = k => {", text)

    def test_the_page_carries_the_complementary_curve(self):
        page = PAGE.read_text()
        for marker in ("n-complement-controls", "Complementary curve", "n-crossings",
                       "crossingsOf", "complementSpine", "#666666"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)

    def test_the_page_carries_the_five_rungs(self):
        page = PAGE.read_text()
        for degree, numbers in ((11, 12), (13, 14), (15, 16), (17, 18), (19, 20)):
            with self.subTest(degree=degree):
                self.assertIn(f'data-speed-degree="{(degree - 1) // 2}">degree {degree} '
                              f'&middot; {numbers} numbers', page)


if __name__ == "__main__":
    unittest.main()
