"""One exact core for the numbers, and the page reading it.

The fault this file guards, as the operator saw it: a curve's grid on the page
and the grid in its record disagreed, and nothing in the suite could tell. On
`loop-13-15-17-mid-1` the record says grid 1/36 and the page said 1/5,148 —
thirty-six times eleven times thirteen — because the page squares a row of 10^8
in doubles, and a squared coefficient of 1.06e16 is past the 9.0e15 where a
double stops counting by ones.

Two things now hold: `curve_lab/measure.py` is the only exact implementation,
and the page prints the record's number while the loaded rows are untouched.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import exact_numbers  # noqa: E402
from curve_lab import measure  # noqa: E402

PANELS = ROOT / "scripts" / "ph_nth_panels.js"
MATH = ROOT / "scripts" / "ph_math.js"


class TestExactNumbers(unittest.TestCase):
    def test_every_stored_curve_agrees_with_the_exact_core(self):
        """A record's grid and bend are the exact ones, not a page's double.

        If this fails, run `scripts/exact_numbers.py` to see which record and
        which number, and `--write` to put the exact value back.
        """
        rows, problems = exact_numbers.audit()
        self.assertGreater(len(rows), 70, "the audit found almost no stored curves")
        self.assertEqual([], [(name, what) for name, what, _, _, _, _ in problems])

    def test_the_large_row_keeps_grid_36_not_the_page_5148(self):
        """Measured 2026-11-16: a row of 10^8 made the page's grid 143 times too big."""
        record = json.loads((ROOT / "curves" / "loop-13-15-17-mid-1" / "curve.json").read_text())
        exact = measure.grid(record["speedX"], record["speedY"])
        self.assertEqual(36, exact)
        self.assertEqual(36, record["grid"])

    def test_the_page_squares_the_same_row_wrong_and_is_told_not_to(self):
        """The double limit is real, so the readout takes the record's number.

        The page is not asked to stop having its own arithmetic: a curve being
        edited has no record. It is asked not to print that arithmetic for a
        stored curve, and the marker below is what it prints instead.
        """
        record = json.loads((ROOT / "curves" / "loop-13-15-17-mid-1" / "curve.json").read_text())
        script = """
            const { readFileSync } = require("node:fs");
            const vm = require("node:vm");
            const context = { window: {}, document: { getElementById: () => null,
                                                      createElement: () => ({}) }, console };
            vm.createContext(context);
            vm.runInContext(readFileSync(process.argv[1], "utf8"), context);
            const m = context.window;
            m.phPowerStep = 1;
            console.log(m.recipeMetrics(%s, %s).pitch);
        """ % (json.dumps(record["speedX"]), json.dumps(record["speedY"]))
        result = subprocess.run(
            ["node", "-e", script, str(MATH)], capture_output=True, text=True, check=True
        )
        page_grid = int(result.stdout.strip())
        exact = measure.grid(record["speedX"], record["speedY"])
        self.assertIn(page_grid, (exact, 5148), "the page's own arithmetic changed: read it again")
        if page_grid != exact:
            panels = PANELS.read_text()
            self.assertIn("(exact, from the record)", panels)
            self.assertIn("state.record = (Number.isFinite(recordGrid)", panels)
            self.assertIn("const storedGrid = record && record.grid ? record.grid : null;", panels)


if __name__ == "__main__":
    unittest.main()
