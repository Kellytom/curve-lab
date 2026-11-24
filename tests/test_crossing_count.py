"""The one crossing counter agrees with the brute-force loop it replaces.

Seven scripts had their own double loop; a coupler sweep made that cost visible (190M pair
tests). `curve_lab.crossings.crossing_pairs` buckets segments in a grid, so the test compares it
with the plain loop on random polylines — the answer must be identical, not nearly.
"""

import math
import random
import unittest

from curve_lab.crossings import crossing_pairs


def brute(points):
    count = 0
    for i in range(len(points) - 2):
        ax, ay = points[i]
        bx, by = points[i + 1]
        for j in range(i + 2, len(points) - 1):
            cx, cy = points[j]
            dx, dy = points[j + 1]
            denominator = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
            if abs(denominator) < 1e-12:
                continue
            s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / denominator
            u = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / denominator
            if 0 < s < 1 and 0 < u < 1:
                count += 1
    return count


class CrossingCountTest(unittest.TestCase):
    def test_random_polylines_match_the_brute_force_loop(self):
        rng = random.Random(11)
        for _ in range(25):
            points = [(rng.uniform(-5, 5), rng.uniform(-5, 5))
                      for _ in range(rng.randint(8, 80))]
            self.assertEqual(brute(points), crossing_pairs(points),
                             f"differs on {len(points)} points")

    def test_a_figure_eight_has_one_pair_and_a_circle_has_none(self):
        eight = [(math.cos(t * math.pi / 60) * 2, math.sin(t * math.pi / 30))
                 for t in range(-60, 61)]
        self.assertGreaterEqual(crossing_pairs(eight), 1)
        circle = [(math.cos(t * math.pi / 90), math.sin(t * math.pi / 90))
                  for t in range(181)]
        self.assertEqual(crossing_pairs(circle), 0)

    def test_a_vertex_touch_is_not_a_crossing(self):
        # the path goes out and comes back along the same line: the shared vertex is not a pair
        points = [(0, 0), (1, 0), (2, 0), (1, 0), (0, 0)]
        self.assertEqual(crossing_pairs(points), 0)


if __name__ == "__main__":
    unittest.main()
