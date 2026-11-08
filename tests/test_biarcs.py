"""Biarcs: endpoints, end tangents, and the G1 join, all measured."""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import biarcs as B  # noqa: E402


class TestBiarcs(unittest.TestCase):
    def test_endpoints_and_radii(self):
        for case in B.CASES:
            with self.subTest(case=case[0]):
                b, ang = B.measure(case)
                _title, p0, _t0, p1, _t1 = case
                self.assertLess(math.dist(b["first"][0], p0), 1e-12)
                self.assertLess(math.dist(b["second"][-1], p1), 1e-12)
                self.assertAlmostEqual(math.dist(b["c0"], b["c1"]), 2 * b["R"], places=9)
                for x, y in b["first"]:
                    self.assertAlmostEqual(math.dist((x, y), b["c0"]), b["R"], places=9)
                for x, y in b["second"]:
                    self.assertAlmostEqual(math.dist((x, y), b["c1"]), b["R"], places=9)

    def test_end_tangents(self):
        for case in B.CASES:
            with self.subTest(case=case[0]):
                b, _ = B.measure(case)
                _title, p0, t0, p1, t1 = case
                start = B.unit(B.left(B.sub(b["first"][0], b["c0"])))
                end = B.unit(B.left(B.sub(b["second"][-1], b["c1"])))
                self.assertGreater(abs(B.dot(start, B.unit(t0))), 1 - 1e-9)
                self.assertGreater(abs(B.dot(end, B.unit(t1))), 1 - 1e-9)

    def test_the_join_is_g1(self):
        for case in B.CASES:
            with self.subTest(case=case[0]):
                _b, ang = B.measure(case)
                self.assertLess(ang, 1e-9)

    def test_the_first_case_radius(self):
        # the equal-radius root for (0,0) east → (1,1) north is √2 − 1
        b, _ = B.measure(B.CASES[0])
        self.assertAlmostEqual(b["R"], math.sqrt(2) - 1, places=12)


if __name__ == "__main__":
    unittest.main()
