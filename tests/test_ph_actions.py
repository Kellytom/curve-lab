# The Inkscape round trip: exact actions, exact metadata, exact back.
#
# The design (2026-11-21): a closed vocabulary of actions — recipe parameter
# edits, rigid motions (rational translate, p-triple rotate, rational-square
# scale, mirror), end-handle edits — each with an exact algebraic effect on
# the speed rows. There is no re-fit: the SVG is a view, the recipe is the
# truth, and reading the file back is arithmetic.

import json
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inkscape import ph_actions, ph_svg

import unittest


def rows_of(uid):
    import json
    from curve_lab.measure import to_fraction
    registry = json.load(open(ROOT / "workbench" / "curve-registry.json"))
    record = next(r for r in registry["curves"] if r["uid"] == uid)
    return ([to_fraction(v) for v in record["speedX"]],
            [to_fraction(v) for v in record["speedY"]])


class RigidMotionTest(unittest.TestCase):
    """Each action's exact algebra, checked on known answers."""

    def test_translate_moves_the_offset_and_not_the_rows(self):
        rx, ry = rows_of("c-0002")
        placement = ph_actions.act_translate(ph_actions.identity_placement(), 3, -2)
        px, py = ph_actions.position_of(rx, ry, placement)
        self.assertEqual(placement["dx"], Fraction(3))
        # a translation differs from the base curve by a CONSTANT: only the
        # constant term moves (the register-55 fault added it to every term)
        base_x, base_y = ph_actions.position_of(rx, ry, ph_actions.identity_placement())
        self.assertEqual(px[0], base_x[0] + 3)
        self.assertEqual(py[0], base_y[0] - 2)
        for k in range(1, len(px)):
            self.assertEqual(px[k], base_x[k], f"x coefficient {k}")
            self.assertEqual(py[k], base_y[k], f"y coefficient {k}")

    def test_p_triple_rotation_keeps_the_rows_exact(self):
        rx, ry = rows_of("c-0002")
        # half angle (3/5, 4/5): the full turn is the (7/25, 24/25) direction
        placement = ph_actions.act_rotate_p_triple(
            ph_actions.identity_placement(), Fraction(3, 5), Fraction(4, 5))
        # the placement stores the HALF angle; the position turns by its double
        self.assertEqual(placement["a"], Fraction(3, 5))
        self.assertEqual(placement["b"], Fraction(4, 5))
        px, py = ph_actions.position_of(rx, ry, placement)
        base_x, base_y = ph_actions.position_of(rx, ry, ph_actions.identity_placement())
        # the position rotates by cos 2φ = −7/25, sin 2φ = 24/25
        self.assertEqual(px[1], Fraction(-7, 25) * base_x[1] - Fraction(24, 25) * base_y[1])
        self.assertEqual(py[1], Fraction(24, 25) * base_x[1] + Fraction(-7, 25) * base_y[1])
        # the speed rows pick up (a + ib) exactly — no trig, no rounding
        ux, uy = ph_actions.place_rows(rx, ry, placement)
        self.assertEqual(ux[0], Fraction(3, 5) * rx[0] - Fraction(4, 5) * ry[0])
        # a non-unit pair is refused
        with self.assertRaises(ValueError):
            ph_actions.act_rotate_p_triple(
                ph_actions.identity_placement(), Fraction(1, 2), Fraction(1, 2))

    def test_scale_by_rational_square(self):
        rx, ry = rows_of("c-0002")
        placement = ph_actions.act_scale_square(ph_actions.identity_placement(), 2)
        ux, uy = ph_actions.place_rows(rx, ry, placement)
        self.assertEqual(ux[0], 2 * rx[0])
        px, py = ph_actions.position_of(rx, ry, placement)
        base_x, base_y = ph_actions.position_of(rx, ry, ph_actions.identity_placement())
        self.assertEqual([4 * a for a in base_x], px)

    def test_mirror_negates_v_and_the_y_offset(self):
        rx, ry = rows_of("c-0002")
        placement = ph_actions.act_mirror_x(ph_actions.identity_placement())
        ux, uy = ph_actions.place_rows(rx, ry, placement)
        self.assertEqual(uy[0], -ry[0])
        self.assertEqual(ux[0], rx[0])


class DegreeGateTest(unittest.TestCase):
    def test_degree_is_read_from_the_rows(self):
        rx, ry = rows_of("c-0002")  # speed degree 5 → position 11
        self.assertEqual(ph_actions.degree_of(rx, ry), 11)

    def test_the_gate_refuses_over_the_ceiling(self):
        rx, ry = rows_of("c-0059")  # speed 5 → position 11
        ok, degree = ph_actions.degree_gate(rx, ry, 11)
        self.assertTrue(ok)
        over_x, over_y = rows_of("c-0260")  # speed 11 → position 23
        ok, degree = ph_actions.degree_gate(over_x, over_y, 11)
        self.assertFalse(ok)
        self.assertEqual(degree, 23)

    def test_end_edit_keeps_the_degree(self):
        rx, ry = rows_of("c-0002")
        ex, ey = ph_actions.act_end_edit(rx, ry, Fraction(1), 0)
        self.assertEqual(ph_actions.degree_of(ex, ey), 11)
        self.assertEqual(ex[-1], rx[-1] + 1)


class RecipeSwapTest(unittest.TestCase):
    def test_swap_takes_the_registry_rows(self):
        registry = json.load(open(ROOT / "workbench" / "curve-registry.json"))
        rx, ry, name = ph_actions.act_recipe_swap(registry, "c-0004")
        self.assertEqual(name, "gosling")
        self.assertEqual(rx[0], Fraction(1))

    def test_swap_refuses_an_unknown_uid(self):
        registry = {"curves": []}
        with self.assertRaises(KeyError):
            ph_actions.act_recipe_swap(registry, "c-9999")


class SnapTest(unittest.TestCase):
    def test_a_near_drag_snaps_and_states_a_zero_miss(self):
        rx, ry = rows_of("c-0002")
        placement = ph_actions.identity_placement()
        spots = ph_actions.legal_handle_positions(rx, ry, placement)
        px, py = ph_actions.position_of(rx, ry, placement)
        base = (px[-1], py[-1])
        action, miss = ph_actions.snap((base[0] + Fraction(1, 1000), base[1]), spots, Fraction(1))
        self.assertEqual(action, "stay")
        self.assertEqual(miss, Fraction(1, 1000))

    def test_a_far_drag_is_refused_with_the_miss_in_units(self):
        rx, ry = rows_of("c-0002")
        spots = ph_actions.legal_handle_positions(rx, ry, placement=ph_actions.identity_placement())
        action, miss = ph_actions.snap((Fraction(10 ** 6), Fraction(0)), spots, Fraction(1))
        self.assertIsNone(action)
        self.assertIsNotNone(miss)


class RoundTripTest(unittest.TestCase):
    """Send to Inkscape, read back: the rows are bit-for-bit the same."""

    def test_round_trip_is_lossless(self):
        rx, ry = rows_of("c-0002")
        placement = ph_actions.act_translate(
            ph_actions.act_scale_square(ph_actions.identity_placement(), Fraction(3, 2)),
            Fraction(10), Fraction(-5))
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "c-0002.svg"
            ph_svg.write_svg(svg, "c-0002", "euler-hook", rx, ry, placement)
            uid, name, (bx, by), back_placement = ph_svg.read_svg(svg)
        self.assertEqual(uid, "c-0002")
        self.assertEqual(name, "euler-hook")
        self.assertEqual(bx, rx)
        self.assertEqual(by, ry)
        self.assertEqual(back_placement, placement)

    def test_the_round_trip_after_an_action_still_agrees(self):
        rx, ry = rows_of("c-0002")
        placement = ph_actions.act_rotate_p_triple(
            ph_actions.identity_placement(), Fraction(3, 5), Fraction(4, 5))
        ax, ay = ph_actions.act_end_edit(rx, ry, Fraction(0), Fraction(1, 2))
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "edited.svg"
            ph_svg.write_svg(svg, "c-0002-edited", "euler-hook end-edited", ax, ay, placement)
            uid, _, (bx, by), back = ph_svg.read_svg(svg)
        self.assertEqual(bx, ax)
        self.assertEqual(by, ay)
        # the drawn position from the file equals the drawn position from the rows
        px1, py1 = ph_actions.position_of(ax, ay, back)
        px2, py2 = ph_actions.position_of(ax, ay, placement)
        self.assertEqual(px1, px2)
        self.assertEqual(py1, py2)

    def test_a_file_without_metadata_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            plain = Path(tmp) / "plain.svg"
            plain.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            with self.assertRaises(ValueError):
                ph_svg.read_svg(plain)


if __name__ == "__main__":
    unittest.main()
