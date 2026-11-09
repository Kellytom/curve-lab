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
            elif row.get("source") == "cusp":
                self.assertIn(row["key"], page)   # shown in the cusp section
            else:
                self.assertIn(f"Fig. G3.C · {row['key']}", page)
        for row in self.rejected:
            self.assertIn(row["key"], page)

    def test_the_bottom_has_cusp_and_deviation_sections(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("Cusp curves · allowed with a declared cusp", page)
        self.assertIn("Still failing · deviation", page)
        for key in ("astroid", "deltoid", "nephroid"):
            self.assertIn(key, page)
        for key in ("squircle", "heart · Beutel upper"):
            self.assertIn(key, page)

    def test_the_astroid_is_admitted_as_cusp_arcs(self):
        astroid = next(r for r in self.admitted if r["key"] == "astroid")
        self.assertEqual(astroid["source"], "cusp")
        self.assertEqual(len(astroid["branches"]), 4)
        self.assertLess(astroid["g3"], 1e-9)

    def test_every_admitted_row_is_classified(self):
        for row in self.admitted:
            with self.subTest(curve=row["key"]):
                self.assertIn("g3_complete", row)
                self.assertIn("smooth", row)
                self.assertIsNotNone(row.get("native"))
                self.assertIsNotNone(row.get("quintic_content"))

    def test_smooth_rows_are_complete_and_featureless(self):
        smooth = [r for r in self.rows if r.get("smooth")]
        self.assertGreaterEqual(len(smooth), 20)
        for row in smooth:
            with self.subTest(curve=row["key"]):
                self.assertTrue(row["g3_complete"])
                self.assertIsNone(row.get("feature"))
                self.assertLessEqual(row["relative"], 0.0501)

    def test_cubic_native_rows_include_the_integer_cubics(self):
        native = [r for r in self.rows if r.get("native") == "cubic-native"]
        keys = {r["key"] for r in native}
        self.assertTrue(any(k.startswith("integer cubic ·") for k in keys))
        for row in native:
            self.assertLess(row["quintic_content"], 1e-9)

    def test_the_page_has_a_handover_section(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("Handover to Inkscape and the glyph pipeline", page)
        self.assertIn("G3-complete", page)
        self.assertIn("smooth handover", page)
        self.assertIn("cubic-native", page)

    def test_the_circle_is_not_drawn(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertNotIn("Fig. G3.C · circle", page)
        self.assertIn("see notes", page)


if __name__ == "__main__":
    unittest.main()
