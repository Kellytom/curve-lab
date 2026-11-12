"""Curves saved from the gallery, cleaned to exact fractions and integers."""

import json
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_yours as Y  # noqa: E402


class TestSavedCurves(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = Y.build_records()

    def test_one_record_per_saved_curve(self):
        self.assertEqual(len(self.records), len(Y.RAW))
        self.assertEqual(len(self.records), 10)

    def test_every_integer_form_is_whole_and_reduced(self):
        for item in self.records:
            values = [int(c) for c in item["u"] + item["v"]]
            divisor = 0
            for value in values:
                divisor = __import__("math").gcd(divisor, abs(value))
            with self.subTest(label=item["label"]):
                self.assertEqual(divisor, 1)

    def test_the_integer_form_is_the_same_curve(self):
        for item in self.records:
            u = tuple(F(c) for c in item["u"])
            v = tuple(F(c) for c in item["v"])
            ud = tuple(F(c) for c in item["u_decimal"])
            vd = tuple(F(c) for c in item["v_decimal"])
            with self.subTest(label=item["label"]):
                self.assertAlmostEqual(Y.P.bend_ratio(u, v), Y.P.bend_ratio(ud, vd), places=6)

    def test_the_pitch_is_read_from_the_integer_form(self):
        for item in self.records:
            with self.subTest(label=item["label"]):
                self.assertLess(item["pitch"], item["pitch_decimal"])
                self.assertGreater(item["pitch"], 0)

    def test_a_browser_save_merges_and_skips_duplicates(self):
        saved = {"presets": [
            {"panel": "q13", "saved": "2026-11-12T19:00:00Z",
             "u": ["1.65", "-5.5", "5.4"], "v": ["1.825", "-11.65", "11.8"]},
            {"panel": "q13", "saved": "2026-11-12T19:00:01Z",
             "u": ["0.5", "-0.5", "0.5"], "v": ["0.7", "-4", "4"]},
        ]}
        merged = Y.merge_saved(saved, [])
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0]["pitch"], 15)
        again = Y.merge_saved(saved, merged)
        self.assertEqual(len(again), 2)

    def test_the_files_match_the_generator(self):
        expected = json.loads(json.dumps(Y.build_document(Y.build_records())))
        self.assertEqual(json.loads(Y.JSON_PATH.read_text()), expected)
        self.assertIn("<svg", Y.SVG_PATH.read_text())


if __name__ == "__main__":
    unittest.main()
