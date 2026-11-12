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

    def test_a_mixed_degree_recipe_runs(self):
        """Degree 2 in u, degree 6 in v - the blend case."""
        m = M.metrics((2, -3, 3), (1, 0, 0, 0, 0, 0, F(1, 4)))
        self.assertGreater(m["bend"], 0)
        self.assertGreater(m["pitch"], 0)
        self.assertIsNotNone(m["inflection"])

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
