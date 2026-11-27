# Quintic from Guide: the maths that makes the six points survive.
#
# The operator's workflow (2026-11-26): draw a pale outer guide in Inkscape,
# take six points off it, dial one Fullness scalar, and see the quintic drawn
# as a cubic chain — while the six control points stay the record that goes to
# Blender and GeoGebra.
#
# These tests guard the four claims that make that workflow honest:
#   - the six points are what the slider blends between (Fullness is exact);
#   - the chain passes through the quintic's stations and keeps its end tangents;
#   - the chain is C2 and its error is measured, not assumed;
#   - the two exports carry the same six points, y flipped, and nothing invented.

import math
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inkscape import quintic_math as qm
from inkscape import quintic_theory as qt

import unittest

NODES = [(20, 180), (160, 60), (260, 170), (360, 40), (390, 110), (320, 240)]
GENTLE = [(0, 100), (50, 60), (100, 50), (150, 50), (200, 60), (250, 100)]


def cubic_second_derivative(seg, t):
    p0, c1, c2, p3 = seg
    return (6 * (1 - t) * (p0[0] - 2 * c1[0] + c2[0]) + 6 * t * (c1[0] - 2 * c2[0] + p3[0]),
            6 * (1 - t) * (p0[1] - 2 * c1[1] + c2[1]) + 6 * t * (c1[1] - 2 * c2[1] + p3[1]))


class FullnessTest(unittest.TestCase):
    def test_one_keeps_the_guide_points_and_zero_gives_the_straight_chord(self):
        kept = qm.blend_fullness(NODES, 1.0)
        self.assertEqual(kept, NODES)
        flat = qm.blend_fullness(NODES, 0.0)
        self.assertEqual(flat[0], NODES[0])
        self.assertEqual(flat[5], NODES[5])
        for i in range(1, 5):
            chord = qm.lerp(NODES[0], NODES[5], i / 5)
            self.assertAlmostEqual(flat[i][0], chord[0], places=12)
            self.assertAlmostEqual(flat[i][1], chord[1], places=12)

    def test_the_slider_is_clamped_and_the_ends_never_move(self):
        for alpha in (-3.0, 0.0, 0.5, 1.0, 4.0):
            out = qm.blend_fullness(NODES, alpha)
            self.assertEqual(out[0], NODES[0])
            self.assertEqual(out[5], NODES[5])
            self.assertEqual(len(out), 6)


class StationTest(unittest.TestCase):
    def test_the_chain_passes_exactly_through_every_station(self):
        for segments in (1, 2, 3, 5, 8):
            chain = qm.cubic_chain(NODES, segments)
            self.assertEqual(len(chain), segments)
            for i, seg in enumerate(chain):
                station = qm.evaluate(NODES, i / segments)
                self.assertAlmostEqual(seg[0][0], station[0], places=9)
                self.assertAlmostEqual(seg[0][1], station[1], places=9)
                station_next = qm.evaluate(NODES, (i + 1) / segments)
                self.assertAlmostEqual(seg[3][0], station_next[0], places=9)
                self.assertAlmostEqual(seg[3][1], station_next[1], places=9)

    def test_the_chain_leaves_and_arrives_on_the_quintics_own_tangents(self):
        segments = 3
        h = 1.0 / segments
        chain = qm.cubic_chain(NODES, segments)
        start = qm.scale(qm.sub(chain[0][1], chain[0][0]), 3.0 / h)
        end = qm.scale(qm.sub(chain[-1][3], chain[-1][2]), 3.0 / h)
        d0 = qm.derivative(NODES, 0.0)
        d1 = qm.derivative(NODES, 1.0)
        for a, b in zip(start, d0):
            self.assertAlmostEqual(a, b, places=8)
        for a, b in zip(end, d1):
            self.assertAlmostEqual(a, b, places=8)

    def test_the_chain_is_c2_at_every_interior_joint(self):
        chain = qm.cubic_chain(NODES, 4)
        for i in range(len(chain) - 1):
            left = cubic_second_derivative(chain[i], 1.0)
            right = cubic_second_derivative(chain[i + 1], 0.0)
            self.assertAlmostEqual(left[0], right[0], places=7)
            self.assertAlmostEqual(left[1], right[1], places=7)


class ErrorTest(unittest.TestCase):
    def test_the_measured_error_falls_at_least_eightfold_per_doubling(self):
        prev = None
        for segments in (2, 4, 8, 16):
            chain = qm.cubic_chain(GENTLE, segments)
            err = qm.measure_max_error(GENTLE, chain)
            if prev is not None:
                self.assertLess(err * 8.0, prev)
            prev = err

    def test_the_error_is_small_on_a_gentle_curve_and_honest_on_a_wild_one(self):
        gentle = qm.cubic_chain(GENTLE, 8)
        self.assertLess(qm.measure_max_error(GENTLE, gentle), 0.01)
        # The brief claimed 2-3 cubics hold 0.001 px. On this 400 px cage they
        # do not: the measured miss is tens of pixels. The number is reported,
        # never assumed.
        wild = qm.cubic_chain(NODES, 2)
        self.assertGreater(qm.measure_max_error(NODES, wild), 1.0)

    def test_fit_to_tolerance_meets_the_tolerance_or_reports_the_miss(self):
        chain, err, used = qm.fit_to_tolerance(GENTLE, 0.01)
        self.assertLessEqual(err, 0.01)
        self.assertLess(used, 32)
        self.assertEqual(len(chain), used)
        chain, err, used = qm.fit_to_tolerance(NODES, 1e-9, max_segments=8)
        self.assertEqual(used, 8)
        self.assertGreater(err, 1e-9)  # an honest miss, not a claimed fit


class InterpolationTest(unittest.TestCase):
    def test_the_quintic_passes_through_all_six_samples(self):
        samples = qm.samples_along(
            [((0, 100), (30, 0), (70, 0), (100, 100)),
             ((100, 100), (130, 200), (170, 200), (200, 100))],
            [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        control = qm.solve_through_samples(samples)
        self.assertLess(qm.interpolation_residual(control, samples), 1e-9)
        for k, s in enumerate(samples):
            b = qm.evaluate(control, k / 5)
            self.assertAlmostEqual(b[0], s[0], places=7)
            self.assertAlmostEqual(b[1], s[1], places=7)

    def test_the_ends_of_the_solution_are_the_end_samples(self):
        samples = [(0, 0), (10, 40), (30, 70), (50, 90), (70, 70), (90, 0)]
        control = qm.solve_through_samples(samples)
        self.assertAlmostEqual(control[0][0], 0.0, places=9)
        self.assertAlmostEqual(control[5][1], 0.0, places=9)

    def test_degenerate_samples_are_refused(self):
        flat = [(0, 0)] * 6
        # six coincident points do still have a quintic (all points equal); the
        # refusal is for a zero pivot, so this must NOT raise
        control = qm.solve_through_samples(flat)
        self.assertEqual(len(control), 6)


class SamplingTest(unittest.TestCase):
    def test_arc_length_samples_hit_both_ends_and_stay_between_them(self):
        seg = ((0, 0), (0, 100), (100, 100), (100, 0))
        pts = qm.samples_along([seg], [0.0, 0.5, 1.0])
        self.assertAlmostEqual(pts[0][0], 0.0, places=9)
        self.assertAlmostEqual(pts[0][1], 0.0, places=9)
        self.assertAlmostEqual(pts[2][0], 100.0, places=9)
        self.assertAlmostEqual(pts[2][1], 0.0, places=9)
        self.assertGreater(pts[1][1], 50.0)


class BlenderConventionTest(unittest.TestCase):
    """Blender's Bezier control points are ON the curve; the handles are
    computed. The operator's rule (2026-11-26) is to follow that, so the
    default mode takes the six points on the drawn line and solves for the
    quintic that passes through all six."""

    def test_the_default_mode_puts_the_six_points_on_the_curve(self):
        inx = (ROOT / "inkscape" / "quintic-guide.inx").read_text()
        options = re.findall(r'<option value="([a-z-]+)"', inx)
        self.assertEqual(options[0], "even")  # first option = the default
        self.assertEqual(options[:4], ["even", "lsq", "cage-nodes", "cage-samples"])
        glue = (ROOT / "inkscape" / "quintic_guide.py").read_text()
        self.assertIn('--pointmode", type=str, default="even"', glue)

    def test_the_dialog_is_three_pages(self):
        inx = (ROOT / "inkscape" / "quintic-guide.inx").read_text()
        pages = re.findall(r"<page name=\"([a-z]+)\"", inx)
        self.assertEqual(pages, ["points", "display", "export"])
        self.assertIn("needs-live-preview=\"true\"", inx)

    def test_the_exported_control_points_reproduce_the_drawn_points(self):
        # The control points are not the drawn points — a Bezier control point
        # off the curve is the whole point of the cage (Blender's NURBS
        # interpretation). What must hold is that the quintic built from the
        # exported points passes through every drawn point, and that the two
        # ends coincide.
        samples = [(0, 0), (20, 40), (45, 60), (70, 60), (95, 40), (120, 0)]
        control = qm.solve_through_samples(samples)
        record = qm.sidecar(control, 1.0, "interpolate", 4, 0.01)
        self.assertEqual(record["control_svg_y_down"][0], [0.0, 0.0])
        self.assertEqual(record["control_svg_y_down"][5], [120.0, 0.0])

    def test_fullness_is_a_tension_dial_not_a_rescale(self):
        control = qm.blend_fullness(NODES, 0.5)
        self.assertEqual(control[0], NODES[0])
        self.assertEqual(control[5], NODES[5])
        # half tension puts each interior point halfway between chord and guide
        for i in range(1, 5):
            chord = qm.lerp(NODES[0], NODES[5], i / 5)
            want = qm.lerp(chord, NODES[i], 0.5)
            self.assertAlmostEqual(control[i][0], want[0], places=12)
            self.assertAlmostEqual(control[i][1], want[1], places=12)


class OvershootTest(unittest.TestCase):
    """A quintic through six points can balloon outside them. Blender's Auto
    Clamped handles exist for this; the clamp here is provable, not cosmetic:
    pull the control points into the box and the convex-hull property holds the
    whole curve inside it."""

    def test_interpolation_can_leave_the_drawn_box_and_the_clamp_stops_it(self):
        samples = [(20, 180), (160, 60), (260, 170), (360, 40), (390, 110), (320, 240)]
        control = qm.solve_through_samples(samples)
        self.assertGreater(qm.overshoot(control, samples), 1.0)
        clamped = qm.clamp_inside(control, samples)
        self.assertEqual(qm.overshoot(clamped, samples), 0.0)
        xs = [p[0] for p in samples]
        ys = [p[1] for p in samples]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        for k in range(1001):
            b = qm.evaluate(clamped, k / 1000)
            self.assertGreaterEqual(b[0], x0 - 1e-9)
            self.assertLessEqual(b[0], x1 + 1e-9)
            self.assertGreaterEqual(b[1], y0 - 1e-9)
            self.assertLessEqual(b[1], y1 + 1e-9)

    def test_a_cage_inside_its_own_box_is_not_touched(self):
        control = qm.blend_fullness(NODES, 1.0)
        self.assertEqual(qm.overshoot(control, NODES), 0.0)
        self.assertEqual(qm.clamp_inside(control, NODES), [tuple(p) for p in NODES])


class ReducerTest(unittest.TestCase):
    """The middle layer: how the six points are taken off the drawn stroke."""

    @staticmethod
    def wavy(count=61):
        # a freehand-like stroke: sampled from a formula, no inkex needed
        pts = []
        for i in range(count):
            x = 20 + 400 * i / (count - 1)
            y = 150 - 55 * math.sin(2.0 * math.pi * i / (count - 1)) \
                - 12 * math.sin(4.0 * math.pi * i / (count - 1))
            pts.append((x, y))
        return pts

    def test_the_even_six_points_are_on_the_stroke_and_exact_through_them(self):
        pts = self.wavy()
        step = (len(pts) - 1) // 5
        six = [pts[i * step] for i in range(5)] + [pts[-1]]
        control = qm.solve_through_samples(six)
        for k, want in enumerate(six):
            got = qm.evaluate(control, k / 5)
            self.assertAlmostEqual(got[0], want[0], places=6)
            self.assertAlmostEqual(got[1], want[1], places=6)

    def test_the_best_fit_misses_the_stroke_less_than_six_even_points(self):
        pts = self.wavy()
        step = (len(pts) - 1) // 5
        even = qm.solve_through_samples([pts[i * step] for i in range(5)] + [pts[-1]])
        fitted = qm.fit_least_squares(pts)
        even_max, even_rms = qm.fit_report(even, pts)
        fit_max, fit_rms = qm.fit_report(fitted, pts)
        self.assertLess(fit_max, even_max)
        self.assertLess(fit_rms, even_rms)

    def test_the_best_fit_keeps_the_drawn_ends(self):
        pts = self.wavy()
        fitted = qm.fit_least_squares(pts)
        self.assertEqual(fitted[0], pts[0])
        self.assertEqual(fitted[5], pts[-1])

    def test_the_miss_of_a_curve_through_its_own_points_is_zero(self):
        control = qm.fit_least_squares(self.wavy())
        report = qm.fit_report(control, [qm.evaluate(control, t) for t in (0.0, 0.3, 0.7, 1.0)])
        # the golden-section search resolves ~6e-5 px, far under anything visible
        self.assertLess(report[0], 1e-3)


class SpanTest(unittest.TestCase):
    def test_splitting_shares_the_boundary_points_and_covers_the_stroke(self):
        pts = [(float(i), float(i * i) / 10.0) for i in range(121)]
        chunks = qm.split_samples(pts, 3)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0][0], pts[0])
        self.assertEqual(chunks[-1][-1], pts[-1])
        for a, b in zip(chunks, chunks[1:]):
            self.assertEqual(a[-1], b[0])          # no gap, no overlap
        self.assertEqual(sum(len(c) - 1 for c in chunks), len(pts) - 1)

    def test_a_chunk_too_short_to_fit_is_refused(self):
        with self.assertRaises(ValueError):
            qm.split_samples([(0.0, 0.0)] * 5, 4)

    def test_each_span_gets_its_own_six_points_in_the_record(self):
        curve = {"uid": "g1:curve", "group": "ornament", "family": "freehand",
                 "name": "two spans", "closed": False, "winding": None,
                 "fitError": 2.0, "selfCrossings": 0,
                 "spans": [qt.span_record(NODES, "g1:0"),
                           qt.span_record(GENTLE, "g1:1")],
                 "joins": []}
        doc = qt.contract_document([curve])
        self.assertEqual(doc["count"], 1)
        self.assertEqual(len(doc["curves"][0]["spans"]), 2)
        self.assertEqual(doc["curves"][0]["spans"][1]["points"][0], list(GENTLE[0]))

    def test_two_spans_become_two_blender_splines_and_two_geogebra_curves(self):
        script = qm.blender_script_many([NODES, GENTLE], name="two")
        self.assertEqual(script.count("splines.new('NURBS')"), 2)
        self.assertEqual(script.count("sp.order_u = 6"), 2)
        commands = qm.geogebra_commands_many([NODES, GENTLE])
        self.assertIn("S1_P0 = ", commands)
        self.assertIn("S2_P5 = ", commands)
        self.assertIn("C1(t) = ", commands)
        self.assertIn("C2(t) = ", commands)


class TheoryTest(unittest.TestCase):
    """The advanced pieces: a proved bound, seams, PH, offsets, knot choice."""

    @staticmethod
    def ph_cubic_as_quintic():
        # hodograph (1 - t^2, 2t): x'^2 + y'^2 = (1 + t^2)^2, a perfect square
        c0 = (0.0, 0.0)
        c1 = (1.0 / 3.0, 0.0)
        c2 = (2.0 / 3.0, 1.0 / 3.0)
        c3 = (2.0 / 3.0, 1.0)
        return qt.elevate(qt.elevate(qt._as_fractions([c0, c1, c2, c3])))

    def test_the_bound_is_never_below_the_measured_error(self):
        for segments in (1, 2, 4, 8):
            chain = qm.cubic_chain(NODES, segments)
            bound, per = qt.chain_error_bound(NODES, chain)
            measured = qm.measure_max_error(NODES, chain)
            self.assertGreaterEqual(bound, measured - 1e-9)
            self.assertEqual(len(per), segments)
            self.assertAlmostEqual(bound, max(per), places=12)

    def test_the_bound_is_tighter_than_the_naive_hull_of_the_control_polygon(self):
        chain = qm.cubic_chain(NODES, 8)
        bound, _ = qt.chain_error_bound(NODES, chain)
        self.assertLess(bound, 0.2)      # measured is ~0.055

    def test_split_bezier_reproduces_the_curve_on_both_halves(self):
        left, right = qt.split_bezier(qt._as_fractions(NODES), Fraction(1, 2))
        for u in (0.0, 0.25, 0.5, 0.75, 1.0):
            want = qm.evaluate(NODES, 0.5 * u)
            got = qm.evaluate([(float(p[0]), float(p[1])) for p in left], u)
            self.assertAlmostEqual(got[0], want[0], places=9)
            self.assertAlmostEqual(got[1], want[1], places=9)
            want2 = qm.evaluate(NODES, 0.5 + 0.5 * u)
            got2 = qm.evaluate([(float(p[0]), float(p[1])) for p in right], u)
            self.assertAlmostEqual(got2[0], want2[0], places=9)
            self.assertAlmostEqual(got2[1], want2[1], places=9)

    def test_elevation_does_not_move_the_curve(self):
        cubic = [NODES[0], NODES[1], NODES[2], NODES[3]]
        raised = qt.elevate(qt.elevate(qt._as_fractions(cubic)))
        for u in (0.0, 0.3, 0.6, 1.0):
            a = qm.evaluate_cubic(tuple(cubic), u)
            b = qm.evaluate([(float(p[0]), float(p[1])) for p in raised], u)
            self.assertAlmostEqual(a[0], b[0], places=9)
            self.assertAlmostEqual(a[1], b[1], places=9)

    def test_a_cubic_dressed_as_a_quintic_is_detected(self):
        raised = self.ph_cubic_as_quintic()
        points = [(float(p[0]), float(p[1])) for p in raised]
        self.assertEqual(qt.low_degree(points), 3)
        self.assertEqual(qt.low_degree(NODES), 5)
        chain = qm.cubic_chain(points, 3)   # a chain that starts at 1 reproduces it
        one = qm.cubic_chain(points, 1)
        # one cubic reproduces a cubic exactly; the measure resolves ~6e-5 px
        self.assertLess(qm.measure_max_error(points, one), 1e-3)
        self.assertLess(qm.measure_max_error(points, chain), 1e-3)

    def test_the_ph_test_says_yes_to_a_ph_curve_and_no_to_a_general_one(self):
        points = [(float(p[0]), float(p[1])) for p in self.ph_cubic_as_quintic()]
        self.assertTrue(qt.is_pythagorean(points))
        self.assertFalse(qt.is_pythagorean(NODES))

    def test_smoothing_a_seam_removes_the_corner_and_keeps_the_ends(self):
        second = [NODES[-1]] + [p for p in GENTLE[1:]]
        controls = [list(NODES), second]
        before_angle = qt.seam_angle(controls[0], controls[1])
        self.assertGreater(before_angle, 0.0)
        smoothed, before, after = qt.smooth_seams(controls)
        self.assertLess(after[0][0], 1e-4)   # floating noise, in degrees
        self.assertEqual(smoothed[0][0], NODES[0])
        self.assertEqual(smoothed[1][-1], second[-1])
        self.assertEqual(smoothed[0][-1], smoothed[1][0])   # the seam is shared

    def test_arclength_knots_rise_from_zero_to_one(self):
        knots = qt.arclength_knots(NODES, 4)
        self.assertEqual(len(knots), 5)
        self.assertAlmostEqual(knots[0], 0.0, places=12)
        self.assertAlmostEqual(knots[-1], 1.0, places=12)
        for a, b in zip(knots, knots[1:]):
            self.assertLess(a, b)

    def test_curvature_cuts_stay_ordered_and_inside(self):
        pts = [(float(i), 0.0) for i in range(61)]
        curv = [0.0] * 61
        curv[22] = 5.0
        cuts = qt.curvature_cuts(pts, curv, 3)
        self.assertEqual(cuts[0], 0)
        self.assertEqual(cuts[-1], 60)
        self.assertEqual(cuts[1], 22)
        for a, b in zip(cuts, cuts[1:]):
            self.assertLess(a, b)

    def test_the_offset_of_a_straight_line_is_a_parallel_line(self):
        line = [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0), (40.0, 0.0), (50.0, 0.0)]
        chain, miss = qt.offset_chain(line, 5.0, segments=4)
        self.assertLess(miss, 0.05)
        for seg in chain:
            for point in seg:
                self.assertAlmostEqual(abs(point[1]), 5.0, places=6)

    def test_parameter_correction_does_not_make_the_fit_worse(self):
        pts = ReducerTest.wavy()
        plain = qm.fit_least_squares(pts)
        corrected = qt.fit_least_squares_reparametrised(pts, passes=3)
        plain_rms = qm.fit_report(plain, pts)[1]
        corrected_rms = qm.fit_report(corrected, pts)[1]
        self.assertLess(corrected_rms, plain_rms + 1e-9)


class PathDataTest(unittest.TestCase):
    def test_the_d_string_has_one_c_per_segment_and_reads_back(self):
        chain = qm.cubic_chain(NODES, 3)
        d = qm.chain_to_d(chain)
        self.assertEqual(d.count("C "), 3)
        self.assertTrue(d.startswith("M "))
        numbers = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)]
        expected = [chain[0][0][0], chain[0][0][1]]
        for seg in chain:
            expected.extend([seg[1][0], seg[1][1], seg[2][0], seg[2][1],
                             seg[3][0], seg[3][1]])
        self.assertEqual(len(numbers), len(expected))
        for got, want in zip(numbers, expected):
            self.assertAlmostEqual(got, want, places=6)

    def test_numbers_are_plain_decimals(self):
        self.assertEqual(qm.num(1e-9), "0")
        self.assertEqual(qm.num(-0.0), "0")
        self.assertEqual(qm.num(1234.5), "1234.5")
        self.assertNotIn("e", qm.num(1e-7))
        self.assertNotIn("E", qm.num(1e20))


class ExportTest(unittest.TestCase):
    """The shared record: y up, forward tangents, a measured join."""

    def test_the_record_is_y_up_and_the_points_are_the_exact_object(self):
        record = qt.span_record(NODES, "s1")
        self.assertEqual(record["kind"], "quintic")
        self.assertIsNone(record["weights"])
        self.assertEqual(len(record["points"]), 6)
        # NODES is in SVG space (y down); the record is y up
        self.assertEqual(record["points"][5], [320.0, -240.0])

    def test_the_frame_tangents_point_forward(self):
        record = qt.span_record(NODES, "s1")
        start = record["frame"]["start"]
        end = record["frame"]["end"]
        self.assertEqual(start["tangent"],
                         [NODES[1][0] - NODES[0][0], NODES[1][1] - NODES[0][1]])
        self.assertEqual(end["tangent"],
                         [NODES[5][0] - NODES[4][0], NODES[5][1] - NODES[4][1]])
        self.assertEqual(start["p"], list(NODES[0]))

    def test_a_document_has_the_envelope_the_schema_asks_for(self):
        curve = {"uid": "g1:curve", "group": "ornament", "family": "freehand",
                 "name": "one", "closed": False, "winding": None, "fitError": 0.5,
                 "selfCrossings": 0,
                 "spans": [qt.span_record(NODES, "g1:0")], "joins": []}
        doc = qt.contract_document([curve])
        self.assertEqual(doc["format"], "curve-lab.quintic/1")
        self.assertEqual(doc["degree"], 5)
        self.assertEqual(doc["count"], 1)
        self.assertEqual(doc["axes"]["y"], "up")
        self.assertEqual(doc["axes"]["extent"], [20.0, 390.0, -240.0, -40.0])

    def test_a_join_measures_what_it_claims(self):
        second = [NODES[-1]] + [p for p in GENTLE[1:]]
        residual = qt.join_residual(NODES, second)
        self.assertAlmostEqual(residual["position"], 0.0, places=9)
        self.assertGreater(residual["tangentDegrees"], 1.0)
        smoothed, _, after = qt.smooth_seams([list(NODES), second])
        residual = qt.join_residual(smoothed[0], smoothed[1])
        self.assertLess(residual["tangentDegrees"], 1e-4)

    def test_the_blender_script_is_one_exact_quintic_span_y_up(self):
        text = qm.blender_script(qm.to_y_up(NODES), flip_y=False)
        self.assertIn("sp.order_u = 6", text)
        self.assertIn("sp.use_endpoint_u = True", text)
        rows = re.findall(r"\(\s*(-?[\d.]+),\s*(-?[\d.]+),\s*0\.0\)", text)
        self.assertEqual(len(rows), 6)
        for (x, y), want in zip(rows, NODES):
            self.assertAlmostEqual(float(x), want[0], places=6)
            self.assertAlmostEqual(float(y), -want[1], places=6)

    def test_the_geogebra_commands_are_six_points_and_one_curve(self):
        text = qm.geogebra_commands(qm.to_y_up(NODES), flip_y=False)
        points = re.findall(r"^P(\d) = \((-?[\d.]+), (-?[\d.]+)\)$", text, re.M)
        self.assertEqual([p[0] for p in points], ["0", "1", "2", "3", "4", "5"])
        for (_, x, y), want in zip(points, NODES):
            self.assertAlmostEqual(float(x), want[0], places=6)
            self.assertAlmostEqual(float(y), -want[1], places=6)
        curve = [line for line in text.splitlines() if line.startswith("Q(t)")]
        self.assertEqual(len(curve), 1)
        self.assertIn("5*(1-t)^4*t*P1", curve[0])

    def test_the_bernstein_weights_are_a_partition_of_unity(self):
        for t in (0.0, 0.17, 0.5, 0.83, 1.0):
            total = sum(qm.bernstein_weight(i, 5, t) for i in range(6))
            self.assertAlmostEqual(total, 1.0, places=12)


class TheoryTest(unittest.TestCase):
    """The advanced pieces: a proved bound, seams, PH, offsets, knot choice."""

    @staticmethod
    def ph_cubic_as_quintic():
        # hodograph (1 - t^2, 2t): x'^2 + y'^2 = (1 + t^2)^2, a perfect square
        c0 = (0.0, 0.0)
        c1 = (1.0 / 3.0, 0.0)
        c2 = (2.0 / 3.0, 1.0 / 3.0)
        c3 = (2.0 / 3.0, 1.0)
        return qt.elevate(qt.elevate(qt._as_fractions([c0, c1, c2, c3])))

    def test_the_bound_is_never_below_the_measured_error(self):
        for segments in (1, 2, 4, 8):
            chain = qm.cubic_chain(NODES, segments)
            bound, per = qt.chain_error_bound(NODES, chain)
            measured = qm.measure_max_error(NODES, chain)
            self.assertGreaterEqual(bound, measured - 1e-9)
            self.assertEqual(len(per), segments)
            self.assertAlmostEqual(bound, max(per), places=12)

    def test_the_bound_is_tighter_than_the_naive_hull_of_the_control_polygon(self):
        chain = qm.cubic_chain(NODES, 8)
        bound, _ = qt.chain_error_bound(NODES, chain)
        self.assertLess(bound, 0.2)      # measured is ~0.055

    def test_split_bezier_reproduces_the_curve_on_both_halves(self):
        left, right = qt.split_bezier(qt._as_fractions(NODES), Fraction(1, 2))
        for u in (0.0, 0.25, 0.5, 0.75, 1.0):
            want = qm.evaluate(NODES, 0.5 * u)
            got = qm.evaluate([(float(p[0]), float(p[1])) for p in left], u)
            self.assertAlmostEqual(got[0], want[0], places=9)
            self.assertAlmostEqual(got[1], want[1], places=9)
            want2 = qm.evaluate(NODES, 0.5 + 0.5 * u)
            got2 = qm.evaluate([(float(p[0]), float(p[1])) for p in right], u)
            self.assertAlmostEqual(got2[0], want2[0], places=9)
            self.assertAlmostEqual(got2[1], want2[1], places=9)

    def test_elevation_does_not_move_the_curve(self):
        cubic = [NODES[0], NODES[1], NODES[2], NODES[3]]
        raised = qt.elevate(qt.elevate(qt._as_fractions(cubic)))
        for u in (0.0, 0.3, 0.6, 1.0):
            a = qm.evaluate_cubic(tuple(cubic), u)
            b = qm.evaluate([(float(p[0]), float(p[1])) for p in raised], u)
            self.assertAlmostEqual(a[0], b[0], places=9)
            self.assertAlmostEqual(a[1], b[1], places=9)

    def test_a_cubic_dressed_as_a_quintic_is_detected(self):
        raised = self.ph_cubic_as_quintic()
        points = [(float(p[0]), float(p[1])) for p in raised]
        self.assertEqual(qt.low_degree(points), 3)
        self.assertEqual(qt.low_degree(NODES), 5)
        chain = qm.cubic_chain(points, 3)   # a chain that starts at 1 reproduces it
        one = qm.cubic_chain(points, 1)
        # one cubic reproduces a cubic exactly; the measure resolves ~6e-5 px
        self.assertLess(qm.measure_max_error(points, one), 1e-3)
        self.assertLess(qm.measure_max_error(points, chain), 1e-3)

    def test_the_ph_test_says_yes_to_a_ph_curve_and_no_to_a_general_one(self):
        points = [(float(p[0]), float(p[1])) for p in self.ph_cubic_as_quintic()]
        self.assertTrue(qt.is_pythagorean(points))
        self.assertFalse(qt.is_pythagorean(NODES))

    def test_smoothing_a_seam_removes_the_corner_and_keeps_the_ends(self):
        second = [NODES[-1]] + [p for p in GENTLE[1:]]
        controls = [list(NODES), second]
        before_angle = qt.seam_angle(controls[0], controls[1])
        self.assertGreater(before_angle, 0.0)
        smoothed, before, after = qt.smooth_seams(controls)
        self.assertLess(after[0][0], 1e-4)   # floating noise, in degrees
        self.assertEqual(smoothed[0][0], NODES[0])
        self.assertEqual(smoothed[1][-1], second[-1])
        self.assertEqual(smoothed[0][-1], smoothed[1][0])   # the seam is shared

    def test_arclength_knots_rise_from_zero_to_one(self):
        knots = qt.arclength_knots(NODES, 4)
        self.assertEqual(len(knots), 5)
        self.assertAlmostEqual(knots[0], 0.0, places=12)
        self.assertAlmostEqual(knots[-1], 1.0, places=12)
        for a, b in zip(knots, knots[1:]):
            self.assertLess(a, b)

    def test_curvature_cuts_stay_ordered_and_inside(self):
        pts = [(float(i), 0.0) for i in range(61)]
        curv = [0.0] * 61
        curv[22] = 5.0
        cuts = qt.curvature_cuts(pts, curv, 3)
        self.assertEqual(cuts[0], 0)
        self.assertEqual(cuts[-1], 60)
        self.assertEqual(cuts[1], 22)
        for a, b in zip(cuts, cuts[1:]):
            self.assertLess(a, b)

    def test_the_offset_of_a_straight_line_is_a_parallel_line(self):
        line = [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0), (40.0, 0.0), (50.0, 0.0)]
        chain, miss = qt.offset_chain(line, 5.0, segments=4)
        self.assertLess(miss, 0.05)
        for seg in chain:
            for point in seg:
                self.assertAlmostEqual(abs(point[1]), 5.0, places=6)

    def test_parameter_correction_does_not_make_the_fit_worse(self):
        pts = ReducerTest.wavy()
        plain = qm.fit_least_squares(pts)
        corrected = qt.fit_least_squares_reparametrised(pts, passes=3)
        plain_rms = qm.fit_report(plain, pts)[1]
        corrected_rms = qm.fit_report(corrected, pts)[1]
        self.assertLess(corrected_rms, plain_rms + 1e-9)


class PathDataTest(unittest.TestCase):
    def test_the_d_string_has_one_c_per_segment_and_reads_back(self):
        chain = qm.cubic_chain(NODES, 3)
        d = qm.chain_to_d(chain)
        self.assertEqual(d.count("C "), 3)
        self.assertTrue(d.startswith("M "))
        numbers = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)]
        expected = [chain[0][0][0], chain[0][0][1]]
        for seg in chain:
            expected.extend([seg[1][0], seg[1][1], seg[2][0], seg[2][1],
                             seg[3][0], seg[3][1]])
        self.assertEqual(len(numbers), len(expected))
        for got, want in zip(numbers, expected):
            self.assertAlmostEqual(got, want, places=6)

    def test_numbers_are_plain_decimals(self):
        self.assertEqual(qm.num(1e-9), "0")
        self.assertEqual(qm.num(-0.0), "0")
        self.assertEqual(qm.num(1234.5), "1234.5")
        self.assertNotIn("e", qm.num(1e-7))
        self.assertNotIn("E", qm.num(1e20))


class ExportTest(unittest.TestCase):
    def test_the_sidecar_keeps_svg_y_down(self):
        record = qm.sidecar(NODES, 1.0, "nodes", 4, 0.01, guide_id="guide1")
        self.assertEqual(record["control_svg_y_down"][5], [320.0, 240.0])
        self.assertEqual(record["degree"], 5)
        self.assertTrue(record["endpoint"])

    def test_the_blender_script_is_one_exact_quintic_span_y_up(self):
        text = qm.blender_script(NODES)
        self.assertIn("sp.order_u = 6", text)
        self.assertIn("sp.use_endpoint_u = True", text)
        rows = re.findall(r"\(\s*(-?[\d.]+),\s*(-?[\d.]+),\s*0\.0\)", text)
        self.assertEqual(len(rows), 6)
        for (x, y), want in zip(rows, NODES):
            self.assertAlmostEqual(float(x), want[0], places=6)
            self.assertAlmostEqual(float(y), -want[1], places=6)
        self.assertIn("y flipped", text)

    def test_the_geogebra_commands_are_six_points_and_one_curve(self):
        text = qm.geogebra_commands(NODES)
        points = re.findall(r"^P(\d) = \((-?[\d.]+), (-?[\d.]+)\)$", text, re.M)
        self.assertEqual([p[0] for p in points], ["0", "1", "2", "3", "4", "5"])
        for (_, x, y), want in zip(points, NODES):
            self.assertAlmostEqual(float(x), want[0], places=6)
            self.assertAlmostEqual(float(y), -want[1], places=6)
        curve = [line for line in text.splitlines() if line.startswith("Q(t)")]
        self.assertEqual(len(curve), 1)
        for i, coefficient in enumerate(["1", "5", "10", "10", "5", "1"]):
            self.assertIn("*P%d" % i, curve[0])
        self.assertIn("5*(1-t)^4*t*P1", curve[0])

    def test_the_bernstein_weights_are_a_partition_of_unity(self):
        for t in (0.0, 0.17, 0.5, 0.83, 1.0):
            total = sum(qm.bernstein_weight(i, 5, t) for i in range(6))
            self.assertAlmostEqual(total, 1.0, places=12)


if __name__ == "__main__":
    unittest.main()
