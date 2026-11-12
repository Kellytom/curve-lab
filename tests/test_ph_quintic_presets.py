"""The saved presets: exact recipes, their metrics, and the files on disk."""

import json
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_presets as P  # noqa: E402


class TestPresets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = P.build_records()

    def test_one_record_per_case(self):
        self.assertEqual(len(self.records), len(P.CASES))
        self.assertEqual(len(self.records), 12)

    def test_every_record_carries_the_fields(self):
        for item in self.records:
            for key in ("id", "label", "source", "note", "u", "v", "bend", "pitch",
                        "inflection", "closest_approach", "endpoint", "endpoint_at_pitch"):
                with self.subTest(id=item["id"], key=key):
                    self.assertIn(key, item)

    def test_ids_are_unique(self):
        ids = [item["id"] for item in self.records]
        self.assertEqual(len(ids), len(set(ids)))

    def test_the_recipes_are_exact_fractions(self):
        for item in self.records:
            for coefficient in item["u"] + item["v"]:
                with self.subTest(id=item["id"], coefficient=coefficient):
                    F(coefficient)          # raises if the string is not exact

    def test_endpoint_at_pitch_is_whole(self):
        for item in self.records:
            for value in item["endpoint_at_pitch"]:
                with self.subTest(id=item["id"], value=value):
                    self.assertEqual(F(value).denominator, 1)

    def test_the_pick_is_bend_two_pitch_ten(self):
        item = next(x for x in self.records if x["id"] == "bend-2-pick")
        self.assertEqual(item["pitch"], 10)
        self.assertAlmostEqual(item["bend"], 2.00, delta=0.02)
        self.assertEqual(item["endpoint_at_pitch"], ["15", "4"])

    def test_the_target_and_its_x10_share_a_shape(self):
        records = {x["id"]: x for x in self.records}
        self.assertEqual(records["the-target"]["bend"], records["target-x10"]["bend"])
        self.assertEqual(records["the-target"]["pitch"], 1500)
        self.assertEqual(records["target-x10"]["pitch"], 15)

    def test_the_files_on_disk_match_the_generator(self):
        expected = json.loads(json.dumps(P.build_document(self.records)))
        self.assertEqual(json.loads(P.JSON_PATH.read_text()), expected)
        svg = P.SVG_PATH.read_text()
        self.assertIn("<svg", svg)
        for item in self.records:
            self.assertIn(item["label"], svg)


if __name__ == "__main__":
    unittest.main()
