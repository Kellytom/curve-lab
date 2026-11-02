"""Gate 4 candidate: study 01 as chains, and its measured separation from P01.

The tests fix the two things that must not drift silently: every node is
rational before placement, and the candidate is not misrepresented as P01
parity. The conformance rule itself is not tested, because it is not decided.
"""

import math
import unittest
from fractions import Fraction

from curve_lab import spine_study
from curve_lab.grammar import STUDY_01, fleur_right
from curve_lab.piece import render_piece


class TestChainStudy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = spine_study.report(1.0)
        cls.piece = spine_study.study_01_from_chains(2.0)

    def test_every_span_end_is_measured(self):
        self.assertEqual(len(self.result["drifts"]), 11)
        self.assertEqual(self.result["spans"], 11)
        self.assertEqual(self.result["chords"], 115)

    def test_the_drift_is_measured_and_stated(self):
        self.assertAlmostEqual(self.result["worst"],
                               max(self.result["drifts"]), places=9)
        self.assertLess(self.result["worst"], 25.0,
                        "the 1 degree candidate moved past its budget")
        # Not parity: the ported P01 matches within 0.03 units, this does not.
        self.assertGreater(self.result["worst"], 0.03)

    def test_the_study_meets_the_1_6_percent_rule(self):
        measured = spine_study.report(0.5)
        self.assertLessEqual(measured["worst_fraction"], 0.016,
                             "the default chain study left the fidelity budget")
        self.assertAlmostEqual(measured["worst_fraction"], 0.0129, delta=0.0005)

    def test_the_chain_is_rational_before_placement(self):
        right = fleur_right(STUDY_01)
        points, ends, heading = spine_study.composite(
            right["spans"], 1.0, start=right["start"], heading=right["angle"])
        self.assertTrue(all(isinstance(x, Fraction) and isinstance(y, Fraction)
                            for x, y in points))
        self.assertEqual(ends[-1], len(points) - 1)
        self.assertGreater(math.degrees(heading.angle), 0.0)

    def test_the_piece_holds_both_strokes(self):
        self.assertTrue(self.piece.mirror)
        self.assertEqual([trace.name for trace in self.piece.traces],
                         ["half", "band"])
        half, band = self.piece.traces
        self.assertGreater(len(half.design.segments), 50)
        self.assertFalse(band.mirror)

    def test_renders_on_the_sheet(self):
        text, info = render_piece(self.piece, frame=(200.0, 250.0), margin=12)
        self.assertTrue(info["fit_ok"])
        self.assertIn('width="200mm"', text)
        self.assertIn('height="250mm"', text)


if __name__ == "__main__":
    unittest.main()
