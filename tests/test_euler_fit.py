import math
import unittest

from curve_lab import euler_fit


class EulerFitTest(unittest.TestCase):
    def test_segment_endpoints(self):
        for kind in ("symmetric", "asymmetric"):
            seg = euler_fit.case(kind)
            x, y = seg.point(0.0)
            self.assertAlmostEqual(x, 0.0, places=12)
            self.assertAlmostEqual(y, 0.0, places=12)
            x, y = seg.point(1.0)
            self.assertAlmostEqual(x, 1.0, places=12)
            self.assertAlmostEqual(y, 0.0, places=12)
            self.assertGreater(seg.arclength, 1.0)

    def test_current_parabola_seam(self):
        seg = euler_fit.case("asymmetric")
        one = euler_fit.fit_segment(seg, 1)
        four = euler_fit.fit_segment(seg, 4)
        self.assertGreater(one["error"], four["error"])
        for span in four["spans"]:
            for a, b in zip(span["p0"], seg.point(span["s0"])):
                self.assertAlmostEqual(a, b, places=12)
            for a, b in zip(span["p3"], seg.point(span["s1"])):
                self.assertAlmostEqual(a, b, places=12)

    def test_asymptotic_fifth_order(self):
        for kind, lo, hi in (("symmetric", 4.2, 5.4),
                              ("asymmetric", 4.2, 5.4)):
            data = euler_fit.study(kind)
            slopes = []
            for a, b in zip(data["rows"][2:], data["rows"][3:]):
                slopes.append(math.log(a["error"] / b["error"]) / math.log(2))
            slope = sum(slopes) / len(slopes)
            self.assertGreater(slope, lo)
            self.assertLess(slope, hi)


if __name__ == "__main__":
    unittest.main()
