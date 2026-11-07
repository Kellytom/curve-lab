"""Pell: the integer hyperbola, and the convergents of √2.

The page claims three things, and each is checked here in integers:
doubling stays on x² − 2y² = 1, the addition law is multiplication of units,
and the convergent error is 1/(2√2 y²) — not "about 1/y²".
"""

import math
import sys
import unittest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pell as P  # noqa: E402


class TestPell(unittest.TestCase):
    def test_the_unit_and_the_first_point(self):
        self.assertEqual(1 * 1 - 2 * 0 * 0, 1)
        self.assertEqual(3 * 3 - 2 * 2 * 2, 1)

    def test_doubling_stays_on_the_curve(self):
        p = (3, 2)
        for _ in range(8):
            p = P.double(p)
            with self.subTest(point=p):
                self.assertEqual(p[0] ** 2 - 2 * p[1] ** 2, 1)

    def test_addition_is_multiplication_of_units(self):
        self.assertEqual(P.multiply((3, 2), (3, 2)), (17, 12))
        self.assertEqual(P.multiply((3, 2), (17, 12)), (99, 70))
        self.assertEqual(P.multiply((1, 0), (3, 2)), (3, 2))

    def test_doubling_and_adding_agree(self):
        a, b = (3, 2), (17, 12)
        self.assertEqual(P.double(a), P.multiply(a, a))
        # (3,2)·(17,12) = 99/70, and 17/12 is already (3,2)²
        self.assertEqual(P.multiply(a, b), (99, 70))

    def test_the_error_is_the_law(self):
        pts = P.chain((3, 2), 6)
        for x, y in pts:
            with self.subTest(point=(x, y)):
                self.assertEqual(x * x - 2 * y * y, 1)
                frac = x / y
                err = 1.0 / (y * y * (frac + math.sqrt(2)))
                self.assertLess(err, 1.0 / (y * y))
                self.assertGreater(err, 1.0 / (3.0 * y * y))

    def test_errors_fall_with_every_doubling(self):
        pts = P.chain((3, 2), 5)
        errs = [1.0 / (y * y * (x / y + math.sqrt(2))) for x, y in pts]
        for a, b in zip(errs, errs[1:]):
            self.assertLess(b, a)
        # y grows fast, so every further point buys many orders of accuracy
        self.assertLess(errs[-1] / errs[-2], 1e-6)
        self.assertGreater(errs[-1] / errs[-2], 1e-35)


if __name__ == "__main__":
    unittest.main()
