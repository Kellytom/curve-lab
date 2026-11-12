"""The Tschirnhausen-type PH quintic on a coarse lattice.

Each claim on `workbench/ph-quintic-lattice.html` is checked here, exactly:
the Pythagorean identity, the hit period, the scale-5 controls of a cut
piece, the rational arc lengths, and the degree-5 cost of the midpoint chain.
"""

import sys
import unittest
from fractions import Fraction as F
from math import lcm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_lattice as Q  # noqa: E402


class TestQuinticLattice(unittest.TestCase):
    def test_the_hodograph_is_pythagorean(self):
        for k in (3, 5, 15):
            for i in range(0, 41):
                t = F(i, 7)
                dx, dy, ds = Q.speed(k, t)
                with self.subTest(k=k, t=t):
                    self.assertEqual(dx * dx + dy * dy, ds * ds)

    def test_tq15_hits_every_integer(self):
        for t in range(0, 11):
            x, y = Q.curve(15, t)
            with self.subTest(t=t):
                self.assertEqual(x.denominator, 1)
                self.assertEqual(y.denominator, 1)

    def test_tq3_hits_only_multiples_of_five(self):
        hits = [t for t in range(0, 21)
                if all(c.denominator == 1 for c in Q.curve(3, t))]
        self.assertEqual(hits, [0, 5, 10, 15, 20])

    def test_the_cut_piece_has_integer_controls_at_scale_five(self):
        x = Q.piece_controls(15, 0, 0)
        y = Q.piece_controls(15, 0, 1)
        self.assertEqual([v * 5 for v in x],
                         [0, 224, 448, 597, 596, 595])
        self.assertEqual([v * 5 for v in y],
                         [0, -30, -60, -85, -100, -100])

    def test_every_unit_piece_keeps_the_scale(self):
        for m in range(0, 6):
            with self.subTest(m=m):
                self.assertEqual(Q.piece_scale(15, m), 5)

    def test_the_arc_lengths_are_integers(self):
        self.assertEqual(Q.arc(15, 1), 121)
        self.assertEqual(Q.arc(15, 5), 123005)
        self.assertEqual(Q.arc(3, 5), 4925)

    def test_the_chain_is_the_wrong_tool_at_degree_five(self):
        k, T, N = 3, F(5), 12
        dt = T / N
        g = 1
        for i in range(N):
            dx, dy, ds = (c * dt for c in Q.speed(k, (i + F(1, 2)) * dt))
            for v in (dx, dy, ds):
                g = lcm(g, v.denominator)
        self.assertEqual(g, 442368)
        # and it does not land on the exact stop
        self.assertNotEqual(Q.curve(k, T)[0], F(0) + sum(
            Q.speed(k, (i + F(1, 2)) * dt)[0] * dt for i in range(N)))

    def test_the_page_links_to_ph_families(self):
        page = (ROOT / "workbench" / "ph-quintic-lattice.html").read_text()
        self.assertIn("ph-families.html", page)
        self.assertIn("TQ(15)", page)
        self.assertIn("primitive", page)


if __name__ == "__main__":
    unittest.main()
