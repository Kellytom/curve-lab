import unittest
from fractions import Fraction

from curve_lab import pyth_chain, pyth_triples


def sweep():
    return pyth_triples.selected_chain(2, 3500, 44.0, 4.0)


class PythChainTest(unittest.TestCase):
    def test_sweep_has_fifty_three_tangents(self):
        self.assertEqual(len(sweep()), 53)

    def test_every_control_point_is_an_integer(self):
        ts = pyth_chain.tangents(sweep())
        for span in pyth_chain.spans(ts):
            for point in span:
                self.assertEqual(len(point), 2)
                self.assertTrue(all(isinstance(v, int) for v in point))

    def test_first_five_triples_form_four_spans(self):
        ts = pyth_chain.tangents(sweep()[:5])
        self.assertEqual(len(pyth_chain.spans(ts)), 4)
        self.assertEqual(pyth_chain.nodes(ts),
                         [(0, 0), (106, -88), (260, -192), (470, -312), (744, -448)])

    def test_join_derivative_is_identical_on_both_sides(self):
        ts = pyth_chain.tangents(sweep())
        self.assertTrue(pyth_chain.check_c1(ts))
        spans = pyth_chain.spans(ts)
        for left, right in zip(spans, spans[1:]):
            incoming = (left[3][0] - left[2][0], left[3][1] - left[2][1])
            outgoing = (right[1][0] - right[0][0], right[1][1] - right[0][1])
            self.assertEqual(incoming, outgoing)

    def test_join_derivative_is_the_shared_arm_vector(self):
        ts = pyth_chain.tangents(sweep())
        spans = pyth_chain.spans(ts)
        for k, (left, right) in enumerate(zip(spans, spans[1:])):
            incoming = (left[3][0] - left[2][0], left[3][1] - left[2][1])
            self.assertEqual(incoming, ts[k + 1])

    def test_span_scale_one_would_be_degenerate(self):
        # At S=1 the inner handles coincide, so the measured curvature is zero.
        ts = pyth_chain.tangents(sweep()[:5])
        spans = pyth_chain.spans(ts, span_scale=1)
        for span in spans:
            self.assertEqual(span[1], span[2])
        self.assertEqual(pyth_chain.curvature_at(spans[0], 0), Fraction(0))

    def test_curvature_jumps_are_bounded_and_not_zero(self):
        ts = pyth_chain.tangents(sweep())
        jumps = pyth_chain.joins(ts)
        self.assertEqual(len(jumps), 51)
        self.assertTrue(all(j >= 0 for j in jumps))
        self.assertEqual(max(jumps), Fraction(6, 23))
        self.assertLess(max(jumps), Fraction(1, 3))
        self.assertGreater(sorted(jumps)[len(jumps) // 2], Fraction(1, 20))

    def test_curvature_formula_at_both_ends(self):
        # A circular-arc cubic has equal curvature at both ends when symmetric;
        # check the exact formula against a hand-computed value.
        cubic = ((0, 0), (1, 0), (2, 0), (3, 0))       # straight line
        self.assertEqual(pyth_chain.curvature_at(cubic, 0), Fraction(0))
        self.assertEqual(pyth_chain.curvature_at(cubic, 1), Fraction(0))
        arc = ((0, 0), (0, 1), (1, 1), (1, 0))
        k0 = pyth_chain.curvature_at(arc, 0)
        k1 = pyth_chain.curvature_at(arc, 1)
        self.assertEqual(k0, k1)
        self.assertGreater(abs(k0), 0)

    def test_report(self):
        r = pyth_chain.report(sweep())
        self.assertEqual(r["tangents"], 53)
        self.assertEqual(r["spans"], 52)
        self.assertTrue(r["integer"])
        self.assertTrue(r["c1"])
        self.assertEqual(r["width"], 245960)
        self.assertEqual(r["height"], 25792)


class PythChainG2Test(unittest.TestCase):
    def test_recurrence_handles(self):
        ts = pyth_chain.tangents(sweep())
        hs = pyth_chain.g2_handles(ts)
        self.assertEqual(len(hs), len(ts))
        self.assertEqual([str(h) for h in hs[:4]], ["1", "1", "29/23", "37/30"])
        self.assertTrue(all(h > 0 for h in hs))

    def test_every_join_is_g2(self):
        ts = pyth_chain.tangents(sweep())
        hs = pyth_chain.g2_handles(ts)
        self.assertEqual(pyth_chain.curvature_gap(ts, hs), 0)

    def test_g2_keeps_c1(self):
        ts = pyth_chain.tangents(sweep())
        hs = pyth_chain.g2_handles(ts)
        sp = pyth_chain.spans_with(ts, hs)
        for left, right in zip(sp, sp[1:]):
            incoming = (left[3][0] - left[2][0], left[3][1] - left[2][1])
            outgoing = (right[1][0] - right[0][0], right[1][1] - right[0][1])
            self.assertEqual(incoming, outgoing)

    def test_g2_is_rational_not_integer(self):
        # Exact G2 exists, but the common denominator is far too large for a grid.
        report = pyth_chain.g2_report(sweep())
        self.assertTrue(report["g2"])
        self.assertFalse(report["integer_grid"])
        self.assertGreater(len(str(report["common_denominator"])), 50)

    def test_parallel_arms_are_rejected(self):
        ts = [(3, -4), (6, -8)]
        with self.assertRaises(ValueError):
            pyth_chain.g2_handles(ts)


if __name__ == "__main__":
    unittest.main()
