"""The G3 catalogue: every named curve attempted as a quintic G3 chain.

The catalogue is an interpolation showcase. These tests read the generated
JSON and check the two claims that matter: every admitted curve passes the G3
gate, and every rejected curve carries a reason. The page is checked for one
panel per admitted non-circle curve.
"""

import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "workbench" / "g3-catalogue.json"
PAGE = ROOT / "workbench" / "g3-catalogue.html"


class TestCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CACHE.read_text(encoding="utf-8"))
        cls.rows = cls.data["curves"]
        cls.admitted = [r for r in cls.rows if r["admitted"]]
        cls.rejected = [r for r in cls.rows if not r["admitted"]]

    def test_every_named_curve_is_attempted(self):
        self.assertGreaterEqual(len(self.rows), 100)
        self.assertEqual(len({r["key"] for r in self.rows}), len(self.rows))

    def test_an_admitted_curve_passes_g3(self):
        self.assertGreaterEqual(len(self.admitted), 15)
        for row in self.admitted:
            with self.subTest(curve=row["key"]):
                self.assertLess(row["g3"], 1e-9)
                self.assertIsNotNone(row["error"])
                self.assertTrue(math.isfinite(row["error"]))
                for branch in row["branches"]:
                    self.assertTrue(branch["pass"])
                    self.assertLess(branch["g3"], 1e-9)

    def test_every_rejection_has_a_reason(self):
        self.assertGreaterEqual(len(self.rejected), 5)
        for row in self.rejected:
            with self.subTest(curve=row["key"]):
                self.assertFalse(row["admitted"])
                self.assertTrue(row["reason"])

    def test_the_closure_seam_is_allowed(self):
        by_key = {r["key"]: r for r in self.admitted}
        for key in ("bow", "strophoid", "bernoulli", "nodal", "abs(x) gerono"):
            self.assertIn(key, by_key)
            branches = by_key[key]["branches"]
            self.assertTrue(any(not b["seam_pass"] for b in branches), key)
            for b in branches:
                self.assertLess(b["g3"], 1e-9)   # body joins still pass

    def test_the_admitted_relative_errors_stay_under_five_percent(self):
        worst = max(r["relative"] for r in self.admitted)
        self.assertLessEqual(worst, 0.0501)

    def test_the_catalogue_spans_are_quintic(self):
        self.assertEqual(self.data["spans"], 6)
        for row in self.admitted:
            for branch in row["branches"]:
                self.assertIn(branch["count"], (5, 6, 10, 14))

    def test_the_page_draws_each_admitted_curve_except_the_circle(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("G3 catalogue", page)
        self.assertIn("quintic", page.lower())
        self.assertIn("max deviation", page)
        self.assertIn("Closure seam allowed", page)
        self.assertIn("closure seam allowed", page)
        for row in self.admitted:
            if row["key"] == "circle":
                self.assertNotIn("Fig. G3.C · circle", page)
            else:
                self.assertIn(f"Fig. G3.C · {row['key']}", page)
        for row in self.rejected:
            self.assertIn(row["key"], page)

    def test_the_bottom_shows_the_still_failing_examples(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("Still failing · examples from the original showcase", page)
        for key in ("astroid", "squircle", "heart · Beutel upper"):
            self.assertIn(key, page)

    def test_the_circle_is_not_drawn(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertNotIn("Fig. G3.C · circle", page)
        self.assertIn("see notes", page)


if __name__ == "__main__":
    unittest.main()
