"""Guards the integer PH rail page: exact rail, lattice grid, no cubic drawn.

The page is `workbench/integer-ph-rail.html`; the generator is
`scripts/integer_ph_rail.py`; the exact core is `curve_lab/ph_offset.py`.
"""

import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import integer_ph_rail as I  # noqa: E402
from curve_lab import ph_offset as ph  # noqa: E402


class IntegerPhRailTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = I.proof_data()
        cls.mirror = I.mirror_data()

    def setUp(self):
        self.page = (ROOT / "workbench" / "integer-ph-rail.html").read_text(
            encoding="utf-8")

    # -- the exact rail ----------------------------------------------------

    def test_the_offset_is_perpendicular_and_exactly_d_away(self):
        """The normal equations, in Fraction: no sampling, no tolerance."""
        data = self.data
        u, v, d = data["u"], data["v"], data["distance"]
        x_prime, y_prime = ph.hodograph_pair(u, v)
        sigma = ph.speed_squared(u, v)
        for t in (Fraction(1, 3), Fraction(1, 2), Fraction(2, 5)):
            spine = ph.point_at(u, v, 0, t)
            rail = ph.point_at(u, v, d, t)
            dx, dy = rail[0] - spine[0], rail[1] - spine[1]
            hx, hy = ph.evaluate(x_prime, t), ph.evaluate(y_prime, t)
            speed = ph.evaluate(sigma, t)
            # perpendicular to the tangent ...
            self.assertEqual(dx * hx + dy * hy, 0)
            # ... and exactly d along the unit normal
            self.assertEqual(dx * (-hy) + dy * hx, d * speed)

    def test_the_exact_polynomials_are_pinned(self):
        """The rail is a ratio of these polynomials; changing one is a fault."""
        self.assertEqual(self.data["x"], [
            Fraction(0), Fraction(-12), Fraction(70), Fraction(-511, 3),
            Fraction(189), Fraction(-444, 5), Fraction(40, 3),
            Fraction(-4, 7)])
        self.assertEqual(self.data["y"], [
            Fraction(0), Fraction(16), Fraction(-60), Fraction(328, 3),
            Fraction(-112), Fraction(52), Fraction(-4)])
        self.assertEqual(self.data["sigma"], [
            Fraction(20), Fraction(-180), Fraction(609), Fraction(-876),
            Fraction(516), Fraction(-80), Fraction(4)])

    def test_no_cubic_is_drawn(self):
        self.assertFalse(self.data["fit"]["drawn"])
        self.assertIn("It is not drawn", self.page)

    def test_the_fit_reports_its_miss_as_a_share_of_the_size(self):
        fit = self.data["fit"]
        self.assertGreater(fit["error"], 0.0)
        self.assertLess(fit["error"], 1e-5)
        self.assertGreaterEqual(fit["spans"], 2)
        self.assertIn(f"{fit['share']:.2e}", self.page)
        self.assertIn(f"{fit['error']:.2e}", self.page)

    def test_the_rails_are_labelled_and_swapping_them_is_caught(self):
        exact = {"kind": "exact", "coefficients": self.data["sigma"]}
        fitted = {"kind": "fitted", "spans": [1, 2], "error": 1e-6}
        ph.assert_rails_are_labelled(exact, fitted)
        with self.assertRaises(ValueError):
            ph.assert_rails_are_labelled(fitted, exact)

    # -- the lattice -------------------------------------------------------

    def test_the_pitch_gives_only_the_two_ends(self):
        self.assertEqual(self.data["pitch"], 105)
        self.assertEqual(len(self.data["at_pitch"]), 2)
        self.assertEqual(self.data["at_pitch"][0]["point"], (0, 0))

    def test_the_first_interior_hit_is_the_midpoint_at_3360(self):
        first = self.data["first"]
        self.assertEqual(first["scale"], 3360)
        self.assertEqual(first["t"], (1, 2))
        self.assertEqual(first["point"],
                         (Fraction(-1849, 3360), Fraction(59, 48)))
        self.assertEqual(self.data["scale"], 32 * self.data["pitch"])
        self.assertEqual(len(self.data["at_scale"]), 3)

    def test_the_station_is_three_lattice_points_on_the_y_axis(self):
        rows = {row["label"]: row["lattice"] for row in self.data["station"]}
        self.assertEqual(rows["spine"], (0, 4130))
        self.assertEqual(rows["rail +d"], (120, 4103))
        self.assertEqual(rows["rail -d"], (-120, 4157))

    def test_a_rail_hits_only_when_the_distance_is_chosen_for_it(self):
        self.assertEqual(self.data["rail_first"]["scale"], 3360)
        self.assertEqual(self.data["rail_first"]["t"], (1, 2))
        self.assertGreater(self.data["plain_first"]["scale"], 100_000)
        self.assertEqual(self.data["plain_first"]["scale"], 688800)

    def test_the_vertical_axis_is_not_a_mirror_of_this_curve(self):
        data = self.data
        self.assertEqual(len(data["crossings"]), 4)
        self.assertGreater(data["off_vertical_deg"], 12.0)
        self.assertGreater(data["symmetry"]["central"], 0.2)
        self.assertGreater(data["symmetry"]["vertical"], 0.2)
        self.assertAlmostEqual(data["inflection"], 0.5051, places=3)

    def test_the_page_names_the_grid_and_the_station(self):
        self.assertIn("3360", self.page)
        self.assertIn("exact", self.page.lower())
        self.assertIn("(0, 4130)", self.page)
        self.assertIn("mirror", self.page.lower())

    # -- the mirror candidate ---------------------------------------------

    def test_the_mirror_candidate_is_exactly_symmetric(self):
        mirror = self.mirror
        self.assertEqual(mirror["symmetry"]["central"], 0.0)
        self.assertAlmostEqual(mirror["tangent_deg"], 0.0, places=9)
        self.assertEqual(mirror["midpoint"], (Fraction(2, 5), Fraction(1, 3)))

    def test_the_mirror_station_sits_on_the_axis_at_grid_15(self):
        mirror = self.mirror
        self.assertEqual([row["lattice"] for row in mirror["station"]],
                         [(0, 5), (0, 6), (0, 4)])
        self.assertEqual(len(mirror["at_scale"]), 3)
        self.assertEqual(mirror["rail_first"]["scale"], 5)
        self.assertEqual(len(mirror["crossings"]), 1)

    def test_the_page_calls_the_mirror_curve_a_candidate(self):
        self.assertIn("candidate", self.page.lower())
        self.assertIn("not adopted", self.page)


if __name__ == "__main__":
    unittest.main()
