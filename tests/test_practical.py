"""The practical curve: fewer cubics, a stated error, and the corner fix.

The regression here matters beyond this profile: a segment boundary must not
hand the cubic fit the next segment's tangent, or every corner quietly inflates
the SVG.
"""

import math
import unittest

from clothoid_lab import bezier, engine, practical, spine_study
from clothoid_lab.grammar import STUDY_01, fleur_right
from clothoid_lab.model import Design, Segment
from clothoid_lab.piece import build_piece, render_piece


class TestBoundaryTangent(unittest.TestCase):
    def test_a_corner_does_not_bow_the_previous_segment(self):
        design = Design(
            segments=[
                Segment(kd=0.0, length=100.0, kappa0=0.0),
                Segment(kd=0.0, length=100.0, kappa0=0.0,
                        corner=math.pi / 2),
            ],
            anchor={"x": 0.0, "y": 0.0, "angle": 0.0},
        )
        chain = engine.build(design)
        spans, info = bezier.fit_chain(chain, tol=0.02)
        self.assertEqual(info["spans_per_segment"], [1, 1])
        self.assertLess(info["error_max"], 1e-6)
        self.assertEqual(len(spans), 2)


class TestPracticalProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.piece, cls.report = practical.practical_study_01()

    def test_the_study_is_reduced_to_its_runs(self):
        # 11 structural runs in the half, 4 in the band; a few need a second
        # or third clothoid to stay inside 0.5 mm.
        self.assertEqual(len(self.report["half"]), 11)
        self.assertEqual(len(self.report["band"]), 4)
        self.assertEqual(self.report["segments"], 18)
        self.assertTrue(0.0 < self.report["deviation"] <= 0.5)

    def test_the_svg_is_small(self):
        groups, info = build_piece(self.piece, tol=0.1)
        self.assertTrue(info["fit_ok"])
        cubics = sum(len(group.spans) for group in groups
                     if group.role == "spine")
        self.assertLessEqual(cubics, 40)
        self.assertGreaterEqual(cubics, 18)

    def test_it_renders_on_the_sheet(self):
        text, info = render_piece(self.piece, tol=0.1, frame=(200.0, 250.0),
                                  margin=12)
        self.assertTrue(info["fit_ok"])
        self.assertIn('width="200mm"', text)
        self.assertIn('height="250mm"', text)

    def test_a_pin_becomes_an_exact_vertex(self):
        right = fleur_right(STUDY_01)
        points, ends, _ = spine_study.composite(
            right["spans"], 0.5, start=right["start"], heading=right["angle"])
        knot = (ends[1] + ends[2]) // 2
        pin = (float(points[knot][0]), float(points[knot][1]))
        _, report = practical.practical_study_01(0.5, pins=[pin])
        self.assertEqual(len(report["pins"]), 1)
        self.assertLess(report["pins"][0]["error"], 1e-6)
        self.assertEqual(report["segments"], 19)

    def test_the_tolerance_is_honoured(self):
        for tolerance in (0.25, 1.0):
            _, report = practical.practical_study_01(tolerance)
            self.assertLessEqual(report["deviation"], tolerance)


if __name__ == "__main__":
    unittest.main()
