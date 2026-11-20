"""The circle the walk cannot see: the four implementations, checked exactly.

Each test names the way it covers, so a failure says which implementation of the idea
broke. All arithmetic is in `Fraction`; a float is never evidence.
"""

import importlib.util
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

_spec = importlib.util.spec_from_file_location("circle_split", ROOT / "scripts" / "circle_split.py")
circle_split = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(circle_split)


class CircleSplit(unittest.TestCase):
    def setUp(self):
        self.stations = circle_split.exact_stations((3, 4, 5), 12)

    def test_the_walk_sits_on_the_unit_circle_exactly(self):
        for X, Y in self.stations:
            self.assertEqual(X * X + Y * Y, 1)

    def test_way_1_the_quadratic_split_is_exact(self):
        """x² + 2xy + y² splits into 1·(x² + y²) and 2xy; the identity holds exactly."""
        row = circle_split.check_quadratic("example", 1, 1, 1, self.stations)
        self.assertEqual(row["circularPart"], "1")
        self.assertEqual(row["identityWorstError"], "0")

    def test_way_1_a_circle_only_form_has_no_remainder(self):
        """x² + y² = 1 is all blind part: the walk reads a constant and nothing else."""
        row = circle_split.check_quadratic("circle", 1, 0, 1, self.stations)
        self.assertEqual(row["circularPart"], "1")
        self.assertEqual(row["remainder"], ["0", "0", "0"])

    def test_way_2_the_general_split_hides_a_squared_circle(self):
        """(x² + y²)² = 1 reduces to the constant 1 with no remainder terms."""
        terms = {(4, 0): 1, (2, 2): 2, (0, 4): 1}
        row = circle_split.check_general("squared circle", terms, self.stations)
        self.assertEqual(row["circularPart"], "1")
        self.assertEqual(row["remainderTerms"], [])
        self.assertEqual(row["identityWorstError"], "0")

    def test_way_3_the_lace_curve_is_a_circle_walk(self):
        """The stored rows are u and v, so the tangent (x'/Q, y'/Q) has norm 1 exactly."""
        registry = circle_split.json.loads(
            (ROOT / "workbench" / "curve-registry.json").read_text())
        row = circle_split.check_lace("c-0028", registry)
        self.assertEqual(row["worstError"], "0")
        # a PH speed radius is a polynomial, not a constant: degree 10 for a sextic row
        self.assertEqual(len(row["speedRadius"]) - 1, 10)

    def test_way_4_circle_parameters_stay_rational_and_bounded(self):
        """t = Y/(1+X) gives rational coordinates, and the usable ones stay on the curve."""
        registry = circle_split.json.loads(
            (ROOT / "workbench" / "curve-registry.json").read_text())
        row = circle_split.check_circle_parameters("c-0028", registry, self.stations)
        self.assertGreater(row["usable"], 0)
        for station in row["rows"]:
            t = Fraction(station["t"])
            self.assertTrue(0 <= t <= 1)
            self.assertLess(abs(Fraction(station["x"])), 10)
            self.assertLess(abs(Fraction(station["y"])), 10)


if __name__ == "__main__":
    unittest.main()
