"""Where two polylines cross: the count the page and the finder both rely on."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ph_crossings import pair_crossings, spine  # noqa: E402


class TestPairCrossings(unittest.TestCase):
    def test_two_segments_that_cross(self):
        self.assertEqual(len(pair_crossings([(0, 0), (2, 2)], [(0, 3), (3, 0)])), 1)

    def test_two_segments_apart(self):
        self.assertEqual(len(pair_crossings([(0, 0), (1, 1)], [(0, 3), (1, 4)])), 0)

    def test_a_shared_endpoint_is_not_a_crossing(self):
        self.assertEqual(len(pair_crossings([(0, 0), (1, 0)], [(1, 0), (1, 1)])), 0)

    def test_equal_lengths_do_not_pair_segment_with_segment(self):
        # the trap: with both polylines the same length, an index mistake pairs
        # segment i with segment i and reports crossings that are not there
        # the crossing is placed between two samples, so it is a proper crossing
        # rather than a shared vertex
        across = [(i / 100, 0.0) for i in range(101)]
        # offset in y as well, so no vertex sits exactly on the other line
        down = [(0.5005, -0.99 + i / 50) for i in range(101)]
        self.assertEqual(len(pair_crossings(across, down)), 1)

    def test_a_curve_and_its_flip_cross_where_the_page_says(self):
        _, x, y = spine([2, -5, 6, 1, 0, 0], [4, -22, 22, -2, 0, 0], 700)
        points = list(zip(x, y))
        flipped = [(-px, py) for px, py in points]
        self.assertEqual(len(pair_crossings(points, flipped)), 3)


if __name__ == "__main__":
    unittest.main()
