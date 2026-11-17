"""The cone-terminal page is the engine's own numbers, and it regenerates.

The page is the proof half of session S1: the geometry comes from
`curve_lab.terminals.cone_terminal`, so a page that disagrees with the engine is
a bug in the generator, not a second source of truth.
"""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "cone-terminal.html"
GENERATOR = ROOT / "scripts" / "cone_terminal.py"


class TestConeTerminalPage(unittest.TestCase):
    def test_the_page_states_the_construction(self):
        page = PAGE.read_text()
        for marker in ("Fig. C1a", "Fig. C1b", "R = 2 ×", "√3", "arc centre",
                       "symmetric=True", "axis twist", "centreline"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)

    def test_the_page_shows_both_modes(self):
        """The default cap is the leaned one, the symmetric cap is on the centreline."""
        page = PAGE.read_text()
        self.assertIn("default cap — the tip sits off the stroke", page)
        self.assertIn("symmetric cap — the tip on the centreline", page)

    def test_the_generator_reproduces_the_page(self):
        before = PAGE.read_text()
        subprocess.run([sys.executable, str(GENERATOR)], check=True, capture_output=True)
        self.assertEqual(before, PAGE.read_text(),
                         "the page is not what scripts/cone_terminal.py emits")

    def test_the_page_is_a_figure_with_labels(self):
        """A figure needs its axis story in the text: y is up, and the flip is stated."""
        page = PAGE.read_text()
        self.assertIn("y is up in the model and flipped here at output", page)


if __name__ == "__main__":
    unittest.main()
