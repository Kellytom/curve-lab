"""Placement on the integer lattice: the group, the scale, the grid."""

import unittest
from fractions import Fraction

from pythagorean_spiral import place
from pythagorean_spiral.exact import Dir
from pythagorean_spiral.triples import for_angle, thinnest

THIN = thinnest(3125)


class TestGroup(unittest.TestCase):
    def test_a_quarter_turn_is_the_swap(self):
        self.assertEqual(place.rotate((1, 0), Dir.east().quarter(1)), (0, 1))
        self.assertEqual(place.rotate((0, 1), Dir.east().quarter(1)), (-1, 0))

    def test_a_triangle_power_is_the_group_element(self):
        tri = for_angle(3.0)
        d = place.rotation(tri, 7)
        self.assertEqual(d, tri.direction ** 7)

    def test_rotation_keeps_squared_distance(self):
        tri = for_angle(3.0)
        d = place.rotation(tri, 5, quarter=1)
        a = place.rotate((Fraction(3, 7), Fraction(-2, 5)), d)
        b = place.rotate((Fraction(-1, 3), Fraction(4, 9)), d)
        def sq(p, q):
            return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
        self.assertEqual(sq(a, b),
                         sq((Fraction(3, 7), Fraction(-2, 5)),
                            (Fraction(-1, 3), Fraction(4, 9))))


class TestPlacement(unittest.TestCase):
    def test_scale_and_offset_are_exact(self):
        pts = [(Fraction(1, 3), Fraction(2, 3))]
        out = place.place(pts, scale=Fraction(3, 2),
                          offset=(Fraction(1, 7), 0))
        self.assertEqual(out, [(Fraction(1, 2) + Fraction(1, 7), 1)])

    def test_every_placed_point_stays_rational(self):
        pts = [(0, 0), (Fraction(3, 5), Fraction(4, 5))]
        out = place.place(pts, scale=Fraction(7, 3), offset=(2, -1))
        for p in out:
            self.assertIsInstance(p[0], Fraction)
            self.assertIsInstance(p[1], Fraction)

    def test_lattice_puts_everything_over_one_denominator(self):
        pts = [(Fraction(1, 3), Fraction(1, 5)), (Fraction(2, 7), 1)]
        ints, den = place.lattice(pts)
        self.assertEqual(den, 105)
        self.assertEqual(ints, [(35, 21), (30, 105)])
        for (x, y), (ix, iy) in zip(pts, ints):
            self.assertEqual(Fraction(ix, den), x)
            self.assertEqual(Fraction(iy, den), y)


class TestFit(unittest.TestCase):
    def setUp(self):
        self.path = [(Fraction(x), Fraction(y)) for x, y in
                     [(0, 0), (1, 0), (1, 1), (0, 1)]]

    def test_the_fit_insets_by_the_margin_and_stays_in_the_box(self):
        ints, scale = place.fit(self.path, box=(200, 250), margin=2,
                                units_per_unit=1000)
        xs = [x for x, _ in ints]
        ys = [y for _, y in ints]
        self.assertEqual(min(xs), 2000)
        self.assertEqual(min(ys), 2000)
        self.assertLessEqual(max(xs), (200 - 2) * 1000)
        self.assertLessEqual(max(ys), (250 - 2) * 1000)
        self.assertAlmostEqual(scale, 196.0)

    def test_a_square_lattice_stays_square(self):
        ints, _ = place.fit(self.path, box=(200, 250), margin=2)
        xs = [x for x, _ in ints]
        ys = [y for _, y in ints]
        self.assertEqual(max(xs) - min(xs), max(ys) - min(ys))

    def test_the_output_is_integers(self):
        ints, _ = place.fit(self.path, box=(200, 250), margin=2)
        self.assertTrue(all(isinstance(x, int) and isinstance(y, int)
                            for x, y in ints))

    def test_a_rotation_from_the_group_is_exact_before_the_fit(self):
        tri = for_angle(3.0)
        d = place.rotation(tri, 4)
        placed = place.place(self.path, rotation=d)
        for p in placed:
            self.assertIsInstance(p[0], Fraction)


class TestQuantize(unittest.TestCase):
    def test_quantize_reports_grid_integers(self):
        self.assertEqual(place.quantize([(0.5, -0.25)], 1000),
                         [(500, -250)])

    def test_quantize_rejects_a_bad_grid(self):
        with self.assertRaises(ValueError):
            place.quantize([(0.0, 0.0)], 0)


class TestFrame(unittest.TestCase):
    def test_the_anchor_is_the_local_origin(self):
        self.assertEqual(place.place_at_frame([(0, 0)], (12, -3), (1, 0)),
                         [(12.0, -3.0)])

    def test_local_x_goes_along_the_heading(self):
        out = place.place_at_frame([(2, 0), (0, 2)], (0, 0), (0, 1))
        self.assertAlmostEqual(out[0][0], 0.0)
        self.assertAlmostEqual(out[0][1], 2.0)
        self.assertAlmostEqual(out[1][0], -2.0)
        self.assertAlmostEqual(out[1][1], 0.0)

    def test_a_float_heading_is_accepted(self):
        h = 2 ** -0.5
        out = place.place_at_frame([(1, 0)], (5, 5), (h, h))
        self.assertAlmostEqual(out[0][0], 5 + h)
        self.assertAlmostEqual(out[0][1], 5 + h)

    def test_a_non_unit_heading_is_refused(self):
        with self.assertRaises(ValueError):
            place.place_at_frame([(0, 0)], (0, 0), (1, 1))


if __name__ == "__main__":
    unittest.main()
