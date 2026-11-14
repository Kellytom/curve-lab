"""The exact metrics module: degree 2, degree 7, and the fraction guard."""

import json
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_metrics as M  # noqa: E402


class TestMetrics(unittest.TestCase):
    def test_the_weights_are_the_integrals(self):
        self.assertEqual(M.weight(0), F(1))
        self.assertEqual(M.weight(1), F(0))
        self.assertEqual(M.weight(2), F(1, 12))
        self.assertEqual(M.weight(4), F(1, 80))

    def test_the_centred_frame_moves_t_minus_one_half(self):
        self.assertEqual(M.centred((2, -3, 3)), [F(5, 4), F(0), F(3)])

    def test_the_inflection_count_is_read_off_the_wronskian(self):
        # a bowl has no inflection; an S has one; the w-wave has two
        self.assertEqual(M.inflections([1, 0, 0], [-1, 2, 0]), [])
        self.assertEqual(len(M.inflections([1, 0, 0], [2, -9, 9])), 1)
        self.assertEqual(len(M.inflections([1, 0, 0, 0, 0, 0], [-5, 46, -108, 72, 0, 0])), 2)

    def test_a_straight_line_has_no_inflections(self):
        # the Wronskian is zero everywhere, which is not one root per sample
        straight = M.metrics([2, 0, 0, 0, 0, 0], [4, 0, 0, 0, 0, 0])
        self.assertEqual(straight["inflection_count"], 0)
        self.assertIsNone(straight["inflection"])
        self.assertEqual(round(straight["bend"], 6), 1.0)

    def test_the_inflection_count_never_exceeds_the_degree(self):
        # the Wronskian of two degree-k speeds has degree at most 2k - 1
        for speed_x, speed_y in (([2, -5, 6, 1, 0, 0], [4, -22, 22, -2, 0, 0]),
                                 ([1, 0, 0, 0, 0, 0], [-5, 46, -108, 72, 0, 0])):
            with self.subTest(speed_y=speed_y):
                measured = M.metrics(speed_x, speed_y)
                self.assertLessEqual(measured["inflection_count"], measured["inflection_max"])
                self.assertEqual(measured["inflection_max"],
                                 2 * max(len(speed_x), len(speed_y)) - 3)

    def test_the_fraction_guard_reads_decimals_not_binaries(self):
        self.assertEqual(M.to_fraction(0.1), F(1, 10))
        self.assertEqual(M.to_fraction(1.6500000000000001), F(33, 20))
        self.assertEqual(M.to_fraction(2.725), F(109, 40))
        self.assertEqual(M.to_fraction("1/5"), F(1, 5))

    def test_the_pick_is_bend_two_pitch_ten(self):
        m = M.metrics((2, -3, 3), (2, -12, 12))
        self.assertAlmostEqual(m["bend"], 2.0, delta=0.01)
        self.assertEqual(m["pitch"], 10)
        self.assertAlmostEqual(m["inflection"], 0.5, delta=0.01)

    def test_the_target_is_bend_five_five_pitch_1500(self):
        m = M.metrics((F(1, 5), -2, 2), (F(2, 5), F(-3, 2), F(8, 5)))
        self.assertAlmostEqual(m["bend"], 5.576, delta=0.01)
        self.assertEqual(m["pitch"], 1500)

    def test_a_degree_seven_curve_matches_the_sampled_bend(self):
        u, v = (1, 0, 0, 0), (0, 1, 0, 0)
        m = M.metrics(u, v)
        points = 600
        x = y = 0.0
        trail = [(0.0, 0.0)]
        for i in range(1, points + 1):
            t = (i - 0.5) / points
            a = 1.0
            b = t
            x += (a * a - b * b) / points
            y += 2 * a * b / points
            trail.append((x, y))
        arc = sum(((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2) ** 0.5
                  for p, q in zip(trail, trail[1:]))
        chord = ((trail[-1][0] - trail[0][0]) ** 2
                 + (trail[-1][1] - trail[0][1]) ** 2) ** 0.5
        self.assertAlmostEqual(m["bend"], arc / chord, delta=0.01)

    def test_trailing_zeros_do_not_change_a_recipe(self):
        """A blend of orders is just a longer coefficient list."""
        short = M.metrics((2, -3, 3), (2, -12, 12))
        long = M.metrics((2, -3, 3, 0, 0), (2, -12, 12, 0, 0))
        self.assertAlmostEqual(short["bend"], long["bend"], places=9)
        self.assertEqual(short["pitch"], long["pitch"])
        self.assertAlmostEqual(short["inflection"], long["inflection"], places=6)

    def test_a_mixed_degree_recipe_pads_to_the_longer_list(self):
        """Degree 2 in u, degree 6 in v - the blend case."""
        mixed = M.metrics((2, -3, 3), (1, 0, 0, 0, 0, 0, F(1, 4)))
        padded = M.metrics((2, -3, 3, 0, 0, 0), (1, 0, 0, 0, 0, 0, F(1, 4)))
        self.assertAlmostEqual(mixed["bend"], padded["bend"], places=12)
        self.assertEqual(mixed["pitch"], padded["pitch"])
        self.assertAlmostEqual(mixed["inflection"], padded["inflection"], places=9)

    def test_diagnostics_catch_each_degeneracy(self):
        # a degenerate curve is a straight line or a point, and neither has an
        # inflection: the Wronskian is zero everywhere, so "no-inflection" is
        # reported as well as the shape it degenerated to
        cases = {
            "the pick": ((2, -3, 3), (2, -12, 12), ["degree"]),
            "a point": ((0, 0, 0), (0, 0, 0),
                        ["degree", "point", "axis-line", "cusp", "no-inflection"]),
            "an axis line": ((1, 0, 0), (0, 0, 0),
                             ["degree", "axis-line", "straight", "no-inflection"]),
            "a diagonal line": ((2, 0, 0), (1, 0, 0),
                                ["degree", "straight", "no-inflection"]),
            "a cusp": ((-0.5, 1, 0), (-1, 2, 0),
                       ["degree", "straight", "cusp", "no-inflection"]),
        }
        for label, (u, v, wanted) in cases.items():
            with self.subTest(case=label):
                self.assertEqual([d["code"] for d in M.diagnostics(u, v)], wanted)

    def test_a_healthy_curve_reports_only_the_degree(self):
        report = M.diagnostics((2, -3, 3), (2, -12, 12))
        self.assertEqual([d["level"] for d in report], ["info"])

    def test_every_preset_matches_its_saved_bend(self):
        document = json.loads((ROOT / "workbench" / "ph-quintic-presets.json").read_text())
        for preset in document["presets"]:
            u = [F(coefficient) for coefficient in preset["u"]]
            v = [F(coefficient) for coefficient in preset["v"]]
            m = M.metrics(u, v)
            with self.subTest(id=preset["id"]):
                self.assertAlmostEqual(m["bend"], preset["bend"], delta=0.01)
                self.assertEqual(m["pitch"], preset["pitch"])


if __name__ == "__main__":
    unittest.main()
