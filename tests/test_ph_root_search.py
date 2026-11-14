"""The symmetric root construction: symmetry is exact, not lucky.

The search claims two things and both are checked here in exact arithmetic:
a speed row built from roots that mirror about t = 1/2 satisfies q(1 - t) = ±q(t)
exactly, and an integer row drawn without that structure does not.
"""

import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_root_search as R  # noqa: E402
from ph_crossings import spine  # noqa: E402


def evaluate(row, t):
    return sum(Fraction(value) * t ** power for power, value in enumerate(row))


class TestRootConstruction(unittest.TestCase):
    def test_an_odd_degree_mirrored_set_gives_the_minus_sign(self):
        row = R.row_from_roots([Fraction(1, 6), Fraction(1, 2), Fraction(5, 6)])
        self.assertEqual(len(row), 4)
        for t in (Fraction(1, 7), Fraction(2, 5), Fraction(9, 11)):
            self.assertEqual(evaluate(row, 1 - t), -evaluate(row, t))

    def test_an_even_degree_mirrored_set_gives_the_plus_sign(self):
        row = R.row_from_roots([Fraction(1, 6), Fraction(5, 6)])
        self.assertEqual(len(row), 3)
        for t in (Fraction(1, 7), Fraction(2, 5), Fraction(9, 11)):
            self.assertEqual(evaluate(row, 1 - t), evaluate(row, t))

    def test_wave3_is_exactly_that_row(self):
        """The seed on the page is 72 (t - 1/6)(t - 1/2)(t - 5/6), nothing else."""
        row = R.row_from_roots([Fraction(1, 6), Fraction(1, 2), Fraction(5, 6)])
        self.assertEqual(row, [-5, 46, -108, 72])

    def test_an_integer_row_drawn_without_the_structure_fails(self):
        """Small integers do not land on the symmetry line by accident."""
        for row in ([3, -6, -1, 6], [1, 2, 3, 4], [-6, 41, -80, 48]):
            with self.subTest(row=row):
                holds = True
                for t in (Fraction(1, 7), Fraction(2, 5), Fraction(9, 11)):
                    value = evaluate(row, 1 - t)
                    if value not in (evaluate(row, t), -evaluate(row, t)):
                        holds = False
                        break
                self.assertFalse(holds)

    def test_the_rows_are_integers_of_the_right_length(self):
        for degree in (1, 2, 3, 4, 5):
            for roots, _ in R.symmetric_sets(degree):
                row = R.row_from_roots(roots)
                self.assertEqual(len(row), degree + 1)
                self.assertTrue(all(isinstance(value, int) for value in row))

    def test_a_walked_curve_measures_symmetric_to_rounding(self):
        speed_x = R.scaled([Fraction(1)], 4)
        speed_y = [-5, 46, -108, 72]
        _, x, y = spine(speed_x, speed_y, 400)
        self.assertLess(R.symmetry_of(list(zip(x, y))), 1e-9)

    def test_the_filter_never_passes_an_asymmetric_curve(self):
        """A cheap walk: one root only, so it is one middle root and the x rows."""
        found = R.search(1)
        self.assertTrue(found)
        for curve in found:
            self.assertLessEqual(curve["symmetry"], 1e-6)


if __name__ == "__main__":
    unittest.main()
