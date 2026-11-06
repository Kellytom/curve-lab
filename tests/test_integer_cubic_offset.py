"""Guards the integer cubic offset page: fitted, labelled, no exact claim."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import integer_cubic_offset as I  # noqa: E402


class IntegerCubicOffsetTest(unittest.TestCase):
    def setUp(self):
        self.page = (ROOT / "workbench" / "integer-cubic-offset.html").read_text(
            encoding="utf-8")
        self.data = I.proof_data()

    def test_the_source_is_the_3_4_5_cubic(self):
        self.assertEqual(self.data["case"]["label"], "3-4-5")
        self.assertEqual(self.data["case"]["chord"], 10)
        self.assertEqual(self.data["case"]["p1"], (3, -4))

    def test_the_rail_is_fitted_with_a_stated_error(self):
        self.assertGreater(self.data["error"], 0.0)
        self.assertLess(self.data["error"], 0.01)
        self.assertGreaterEqual(self.data["spans"], 2)
        self.assertIn(f"{self.data['error']:.2e}", self.page)

    def test_no_exact_claim(self):
        self.assertIn("fitted, not exact", self.page.lower())
        self.assertIn("not a Pythagorean-hodograph", self.page)
        self.assertIn("no — the integer cubic is not PH", self.page)


if __name__ == "__main__":
    unittest.main()
