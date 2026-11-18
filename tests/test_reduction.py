"""The properness test: which parametric curves are covers of a simpler curve.

The register's habit applies: a verdict is exact, and the examples are the ones
that are easy to get wrong.
"""

import unittest
from fractions import Fraction

from curve_lab.reduction import is_proper, reduce_curve


def poly(*coefficients):
    return [Fraction(c) for c in coefficients]


class PropernessTest(unittest.TestCase):
    def test_a_septic_parabola_is_proper(self):
        self.assertTrue(is_proper(poly(0, 1), poly(0, 0, 0, 0, 0, 0, 0, 1)))
        self.assertEqual({"proper": True}, reduce_curve(poly(0, 1), poly(0, 0, 0, 0, 0, 0, 0, 1)))

    def test_a_parabola_traced_twice_collapses_to_itself(self):
        result = reduce_curve(poly(0, 0, 1), poly(0, 0, 0, 0, 1))
        self.assertFalse(result["proper"])
        self.assertEqual(2, result["cover"])
        self.assertEqual((poly(0, 1), poly(0, 0, 1)), result["curve"])

    def test_several_terms_do_not_fool_it(self):
        # y = t^4 - t^2 is the parabola u^2 - u under u = t^2.
        result = reduce_curve(poly(0, 0, 1), poly(0, 0, -1, 0, 1))
        self.assertFalse(result["proper"])
        self.assertEqual((poly(0, 1), poly(0, -1, 1)), result["curve"])

    def test_a_cube_cover_reduces_by_three(self):
        result = reduce_curve(poly(0, 0, 0, 1), poly(0, 0, 0, 0, 0, 0, 1))
        self.assertEqual(3, result["cover"])
        self.assertEqual((poly(0, 1), poly(0, 0, 1)), result["curve"])

    def test_a_non_monomial_cover_is_named_not_guessed(self):
        # Q(u) = (u, u^2) composed with u = t^2 + t.
        x = poly(0, 1, 1)
        y = poly(0, 0, 1, 2, 1)
        self.assertFalse(is_proper(x, y))
        result = reduce_curve(x, y)
        self.assertFalse(result["proper"])
        self.assertIsNone(result["curve"])
        self.assertIn("not monomial", result["note"])

    def test_a_parabola_is_proper(self):
        self.assertTrue(is_proper(poly(0, 1), poly(0, -1, 1)))


if __name__ == "__main__":
    unittest.main()
