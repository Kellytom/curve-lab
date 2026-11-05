"""The tapered log-spiral band: exact ratio, exact partner, and the false friend."""

import math
import unittest

from curve_lab import taper


class TestTaper(unittest.TestCase):
    def test_width_ratio_matches_nearest_distance(self):
        # brute force: nearest point from one spiral to the scaled copy
        a, b, k = 10.0, 0.2, 1.35
        spiral = taper.LogSpiral(a, b)
        outer = spiral.scaled(k)
        p = spiral.point(1.0)
        best = min(math.dist(p, outer.point(t)) for t in [i * 0.001 for i in range(-1000, 5000)])
        r = spiral.radius(1.0)
        self.assertAlmostEqual(taper.width_ratio(k, b) * r, best, places=4)

    def test_width_is_proportional_to_radius(self):
        v = taper.verify(10.0, 0.2, 1.35, 0.0, 8.0, 200)
        self.assertLess(v["ratio_spread"], 1e-9)
        self.assertGreater(v["ratio_min"], 0.0)

    def test_partner_is_a_log_spiral(self):
        v = taper.verify(10.0, 0.2, 1.35, 0.0, 8.0, 200)
        self.assertLess(v["tangent_angle_spread"], 1e-9)

    def test_constant_offset_is_not_a_log_spiral(self):
        # a constant-width parallel drifts in tangent-to-radius angle
        a, b, d = 10.0, 0.2, 4.0
        spiral = taper.LogSpiral(a, b)
        seq = []
        prev = None
        for i in range(600):
            th = 8 * math.pi * i / 599
            p = spiral.point(th)
            n = spiral.normal(th)
            q = (p[0] + d * n[0], p[1] + d * n[1])
            if prev is not None:
                dx = q[0] - prev[0]
                dy = q[1] - prev[1]
                v = (math.atan2(dy, dx) - math.atan2(q[1], q[0])) % math.pi
                if seq:
                    while v - seq[-1] > math.pi / 2:
                        v -= math.pi
                    while v - seq[-1] < -math.pi / 2:
                        v += math.pi
                seq.append(v)
            prev = q
        self.assertGreater(math.degrees(max(seq) - min(seq)), 0.5)

    def test_taper_angle_is_negative_for_a_growing_spiral(self):
        # the partner is rotated backwards, not merely scaled
        self.assertLess(taper.taper_angle(1.35, 0.2), 0.0)


if __name__ == "__main__":
    unittest.main()
