# The speed-space re-fit: a float search with an exact verdict.
#
# The laws under test:
#   - fitting at the curve's own degree recovers it exactly (L² = 0);
#   - a lower degree has a positive, EXACT L² (the verdict side is rational);
#   - the returned rows are six-decimal Fractions;
#   - the station miss is reported in curve units.
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.measure import curve_polynomials, to_fraction
from reduction import speed_fit


def rows_of(uid):
    record = next(r for r in json.load(open(ROOT / "workbench" / "curve-registry.json"))["curves"]
                  if r["uid"] == uid)
    return ([to_fraction(v) for v in record["speedX"]],
            [to_fraction(v) for v in record["speedY"]])


class RefitTest(unittest.TestCase):
    def test_fitting_at_the_own_degree_recovers_the_curve(self):
        u, v = rows_of("c-0002")  # speed degree 5
        x, y = curve_polynomials(u, v)
        fu, fv, report = speed_fit.reffit(x, y, 5, start=(u, v))
        self.assertEqual(report["l2"], Fraction(0))
        self.assertEqual(report["max_miss"], 0.0)
        # up to the sign gauge: (u, v) and (−u, −v) are the same curve
        self.assertTrue(fu == u or fu == [-c for c in u])

    def test_a_lower_degree_has_an_exact_positive_verdict(self):
        u, v = rows_of("c-0002")
        x, y = curve_polynomials(u, v)
        fu, fv, report = speed_fit.reffit(x, y, 3, start=(u, v))
        self.assertIsInstance(report["l2"], Fraction)
        self.assertGreater(report["l2"], 0)
        self.assertGreater(report["max_miss"], 0)
        # the returned rows are Fractions, printed at the row's own scale
        for c in fu + fv:
            self.assertIsInstance(c, Fraction)
        # and the position degree follows the rows: 2·3 + 1
        fx, fy = speed_fit.position_of_rows(fu, fv)
        self.assertEqual(max(len(fx), len(fy)) - 1, 7)

    def test_the_verdict_measures_the_returned_rows_not_the_search(self):
        # the exact L² is computed on the quantized rows: recomputing it from
        # the returned position polynomials must equal the report
        u, v = rows_of("c-0002")
        x, y = curve_polynomials(u, v)
        fu, fv, report = speed_fit.reffit(x, y, 3, start=(u, v))
        fx, fy = speed_fit.position_of_rows(fu, fv)
        again = speed_fit.exact_l2(x, y, fx, fy)
        self.assertEqual(again, report["l2"])

    def test_a_large_coefficient_curve_recovers_at_its_own_degree(self):
        # c-0253's rows are ~5e7; a recovered-at-own-degree check is the law
        # that catches a verdict-scale fault (register 56: 6-dp quantization
        # in normalized coordinates left a 1e11 L² floor at the own degree)
        u, v = rows_of("c-0253")
        x, y = curve_polynomials(u, v)
        fu, fv, report = speed_fit.reffit(x, y, 7, start=(u, v))
        self.assertEqual(report["l2"], Fraction(0))
        self.assertEqual(report["max_miss"], 0.0)

    def test_a_curve_that_needs_its_degree_is_refused_by_the_miss(self):
        # c-0260: the fit at speed 5 exists but misses by orders of magnitude
        u, v = rows_of("c-0260")
        x, y = curve_polynomials(u, v)
        fu, fv, report = speed_fit.reffit(x, y, 5, start=(u, v))
        self.assertGreater(report["max_miss"], 1000)  # curve units, not a share
        fx, fy = speed_fit.position_of_rows(fu, fv)
        # the returned rows still follow the law: position degree 2·5 + 1
        self.assertEqual(max(len(fx), len(fy)) - 1, 11)


if __name__ == "__main__":
    unittest.main()
