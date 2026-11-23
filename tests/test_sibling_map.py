# The sibling map's machinery, pinned to the family's known row.
#
# lace_finder.py records the check: p = 1/8, m = 3 gives v exactly
# [-7, 106, -532, 1208, -1280, 512] for lace-1of8-3. The map must read that
# row back to its roots, keep mirrored pairs whole, refuse a lone root, and
# rebuild a shorter stack whose degree fits the ceiling.
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import lace_finder
from scripts import sibling_map as sm


class RootReadingTest(unittest.TestCase):
    def test_the_known_row_factors_to_its_recipe(self):
        v = lace_finder.v_row(Fraction(1, 8), 3)
        self.assertEqual(v, [-7, 106, -532, 1208, -1280, 512])
        roots = sm.factor_row([Fraction(c) for c in v])
        self.assertIsNotNone(roots)
        half = [r for r in roots if r == Fraction(1, 2)]
        self.assertEqual(len(half), 3)
        self.assertIn(Fraction(1, 8), roots)
        self.assertIn(Fraction(7, 8), roots)

    def test_rebuilding_from_the_roots_gives_the_same_row(self):
        v = lace_finder.v_row(Fraction(1, 8), 3)
        roots = sm.factor_row([Fraction(c) for c in v])
        again = sm.row_from_roots(sorted(roots))
        self.assertEqual(again, v)

    def test_a_lone_root_is_not_this_family(self):
        # a root without its mirror is a different construction
        self.assertIsNone(sm.pairs_of([Fraction(1, 3), Fraction(1, 4)]))

    def test_mirrored_pairs_group_whole_and_halves_count(self):
        pairs, halves = sm.pairs_of([Fraction(1, 5), Fraction(4, 5),
                                     Fraction(1, 2), Fraction(1, 2)])
        self.assertEqual(pairs, [(Fraction(1, 5), Fraction(4, 5))])
        self.assertEqual(halves, 2)

    def test_the_shortening_keeps_the_pairs_and_fits_the_ceiling(self):
        v = lace_finder.v_row(Fraction(1, 8), 4)  # speed degree 6, over
        self.assertEqual(len(v) - 1, 6)
        roots = sm.factor_row([Fraction(c) for c in v])
        candidates = sm.candidates_from(roots)
        self.assertTrue(candidates)
        for _roots, _keep in candidates:
            row = sm.row_from_roots(_roots)
            self.assertLessEqual(len(row) - 1, sm.CEILING_SPEED)
            # the pair survives every candidate: 1/8 and 7/8 are in each
            self.assertIn(Fraction(1, 8), _roots)
            self.assertIn(Fraction(7, 8), _roots)

    def test_the_recipe_name_names_the_roots(self):
        self.assertEqual(
            sm.name_of([Fraction(1, 8), Fraction(7, 8), Fraction(1, 2)]),
            "1of8-mid",
        )


if __name__ == "__main__":
    unittest.main()
