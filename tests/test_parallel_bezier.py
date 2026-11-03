import math
import unittest

from curve_lab.parallel_bezier import cusp_ranges, fit_chain


class ParallelBezierTest(unittest.TestCase):
    def test_fit_is_close(self):
        source = [{"p0": (0.0, 0.0), "c1": (0.0, 1.0),
                   "c2": (1.0, 1.0), "p3": (1.0, 0.0)}]
        fitted = fit_chain(source, 0.1, tol=0.005)
        self.assertGreaterEqual(len(fitted["spans"]), 1)
        self.assertLess(fitted["error_max"], 0.005)
        self.assertEqual(fitted["cusps"], [])
        for span in fitted["spans"]:
            for key in ("p0", "c1", "c2", "p3"):
                self.assertIn(key, span)

    def test_cusps_are_found(self):
        # A tight arch: at a large offset the rail folds.
        source = [{"p0": (0.0, 0.0), "c1": (0.0, 0.2),
                   "c2": (0.2, 0.2), "p3": (0.2, 0.0)}]
        cusps = cusp_ranges(source[0], 1.0)
        self.assertTrue(cusps)
        self.assertTrue(all(0.0 <= a <= b <= 1.0 for a, b in cusps))


if __name__ == "__main__":
    unittest.main()
