"""The found curves: each name rebuilds its row, and each row is exactly symmetric.

`scripts/ph_root_search.py --found` writes `workbench/found-curves.json`, which the
sandbox gallery reads at load. These checks run on the file itself, so a hand edit
that breaks the construction fails here rather than on the page.
"""

import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_metrics as metrics  # noqa: E402
import ph_root_search as R  # noqa: E402

FOUND = ROOT / "workbench" / "found-curves.json"


def evaluate(row, t):
    return sum(Fraction(value) * t ** power for power, value in enumerate(row))


class TestFoundCurves(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(FOUND.read_text())
        cls.curves = cls.document["curves"]

    def test_the_walk_landed_something(self):
        self.assertTrue(self.curves, "the found file is empty")

    def test_every_name_rebuilds_the_row_it_names(self):
        """A name states the roots, so the roots must give the stored row back."""
        for curve in self.curves:
            roots = [Fraction(text) for text in curve["rootsExact"]]
            rebuilt = R.row_from_roots(roots)
            with self.subTest(name=curve["name"]):
                self.assertEqual(len(rebuilt), len(curve["speedY"]))
                self.assertTrue(R.proportional(rebuilt, curve["speedY"]))

    def test_the_name_carries_every_pair_and_the_middle_count(self):
        for curve in self.curves:
            parts = curve["name"].split("-")
            # a trailing bare number marks a second curve with the same roots but a
            # different x row; that mark is not part of the construction
            if len(parts) > 3 and parts[-1].isdigit() and parts[-2].isdigit():
                parts = parts[:-1]
            kind, middle = parts[0], int(parts[-1])
            named = set(parts[1:-1])
            roots = [Fraction(text) for text in curve["rootsExact"]]
            counts = {}
            for value in roots:
                if value == Fraction(1, 2):
                    continue
                pair = min(value, 1 - value)
                counts[pair] = counts.get(pair, 0) + 1
            pairs = {f"{pair.numerator}of{pair.denominator}" if times // 2 == 1
                     else f"{times // 2}x{pair.numerator}of{pair.denominator}"
                     for pair, times in counts.items()}
            with self.subTest(name=curve["name"]):
                self.assertIn(kind, ("lace", "wave"))
                self.assertEqual(named, pairs or {"middle"})
                self.assertEqual(middle, sum(1 for v in roots if v == Fraction(1, 2)))

    def test_every_row_is_symmetric_about_the_middle_exactly(self):
        """q(1 - t) = +q(t) or -q(t) in integers; a coincidental row would fail."""
        for curve in self.curves:
            for key in ("speedX", "speedY"):
                row = [Fraction(value) for value in curve[key]]
                with self.subTest(name=curve["name"], row=key):
                    for t in (Fraction(1, 7), Fraction(2, 5), Fraction(9, 11)):
                        value = evaluate(row, 1 - t)
                        self.assertIn(value, (evaluate(row, t), -evaluate(row, t)))

    def test_the_stored_numbers_are_the_measured_ones(self):
        for curve in self.curves:
            with self.subTest(name=curve["name"]):
                measured = metrics.metrics(curve["speedX"], curve["speedY"])
                self.assertAlmostEqual(measured["bend"], curve["bend"], places=2)
                self.assertEqual(int(measured["pitch"]), int(curve["pitch"]))
                self.assertEqual(measured["inflection_count"], curve["inflections"])

    def test_the_best_find_is_the_two_pair_lace(self):
        """The walk's headline: pairs at 1/12 and 1/3, one root at the middle,
        and an x row with its own mirrored roots at 2/5."""
        best = max(self.curves, key=lambda curve: curve["meetings180"])
        self.assertEqual(best["name"], "lace-1of12-1of3-1")
        self.assertEqual(best["rootsExact"], ["1/12", "1/3", "1/2", "2/3", "11/12"])
        self.assertEqual(best["self"], 14)
        self.assertEqual(best["meetings180"], 20)
        self.assertEqual(best["speedX"][:3], [7.0, -25.0, 25.0])


if __name__ == "__main__":
    unittest.main()
