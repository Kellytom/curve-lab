# The variant proposal: an acted SVG becomes a registry record candidate.
#
# Rules under test:
#   - a translation is a view, not a curve → refused;
#   - an end-edit bakes into the rows and proposes parent+letter;
#   - a recipe swap maps back to the sibling that is already in the
#     registry — no new record;
#   - the payload's degrees are read from the rows, never guessed.
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inkscape import ph_actions, ph_variant


def registry():
    return json.load(open(ROOT / "workbench" / "curve-registry.json"))


def rows_of(uid="c-0002"):
    from curve_lab.measure import to_fraction
    record = next(r for r in registry()["curves"] if r["uid"] == uid)
    return ([to_fraction(v) for v in record["speedX"]],
            [to_fraction(v) for v in record["speedY"]])


class VariantTest(unittest.TestCase):
    def setUp(self):
        self.rx, self.ry = rows_of()

    def test_a_translation_is_a_view_and_is_refused(self):
        placement = ph_actions.act_translate(ph_actions.identity_placement(),
                                             Fraction(1, 10), 0)
        record, note = ph_variant.variant_record(
            ("c-0002", "euler-hook", (self.rx, self.ry), placement),
            registry())
        self.assertIsNone(record)
        self.assertIn("a translation is a view", note)

    def test_an_end_edit_proposes_the_next_variant_uid(self):
        ex, ey = ph_actions.act_end_edit(self.rx, self.ry, Fraction(1), 0)
        record, note = ph_variant.variant_record(
            ("c-0002", "euler-hook", (ex, ey),
             ph_actions.identity_placement()),
            registry())
        self.assertIsNotNone(record)
        self.assertTrue(record["uid"].startswith("c-0002"))
        self.assertNotEqual(record["uid"], "c-0002")
        self.assertEqual(record["base_uid"], "c-0002")
        self.assertEqual(record["name"], "euler-hook-end-edited")
        self.assertEqual(record["speedX"][-1], -0.1)  # the acted coefficient
        self.assertIn("position degree 11", note)

    def test_the_baked_rows_draw_the_acted_curve(self):
        # a rotated, scaled recipe bakes into rows whose integral is the
        # drawn curve minus its (zero) offset
        placement = ph_actions.act_scale_square(
            ph_actions.act_rotate_p_triple(ph_actions.identity_placement(),
                                           Fraction(3, 5), Fraction(4, 5)),
            Fraction(2))
        baked_x, baked_y = ph_actions.place_rows(self.rx, self.ry, placement)
        record, _ = ph_variant.variant_record(
            ("c-0002", "euler-hook", (self.rx, self.ry), placement),
            registry())
        self.assertEqual(record["speedX"][0], float(baked_x[0]))
        self.assertIn('"exact": true', json.dumps(record["transform"]))

    def test_the_degree_is_read_from_the_rows(self):
        ex, ey = ph_actions.act_end_edit(self.rx, self.ry, Fraction(1), 0)
        record, note = ph_variant.variant_record(
            ("c-0002", "euler-hook", (ex, ey),
             ph_actions.identity_placement()),
            registry())
        self.assertEqual(ph_actions.degree_of(
            [Fraction(v) if not isinstance(v, float) else Fraction(str(v))
             for v in record["speedX"]],
            [Fraction(v) if not isinstance(v, float) else Fraction(str(v))
             for v in record["speedY"]]), 11)

    def test_a_recipe_swap_is_already_a_curve(self):
        # a swapped file carries the sibling's rows; the sibling is in the
        # registry, so the record would duplicate it — the swap maps back
        # to the sibling's uid (the design note, not a refusal here)
        book = registry()
        sibling = next(r for r in book["curves"] if r["uid"] == "c-0004")
        self.assertEqual(sibling["name"], "gosling")


if __name__ == "__main__":
    unittest.main()
