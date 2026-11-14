"""The stored curve format: one shape, validated, and impossible to misread.

The point of the format is that a number cannot land in the wrong box, so these
tests are about the file rather than about a page.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import curve_records as R  # noqa: E402

FOUND = ROOT / "workbench" / "found-curves.json"


class TestFormat(unittest.TestCase):
    def test_the_file_is_canonical_and_valid(self):
        document = R.read(FOUND)
        self.assertEqual(document["format"], R.FORMAT)
        self.assertEqual(R.validate(document), [])
        self.assertGreater(len(document["curves"]), 100)

    def test_no_record_keeps_a_flat_row(self):
        """One source of truth: the terms, not a parallel pair of arrays."""
        document = R.read(FOUND)
        for curve in document["curves"]:
            with self.subTest(name=curve["name"]):
                self.assertIn("terms", curve)
                self.assertNotIn("speedX", curve)
                self.assertNotIn("speedY", curve)

    def test_every_term_carries_its_power_beside_its_values(self):
        for curve in R.read(FOUND)["curves"]:
            for item in curve["terms"]:
                with self.subTest(name=curve["name"], power=item.get("power")):
                    self.assertEqual(sorted(item), ["power", "x", "y"])
                    self.assertGreaterEqual(item["power"], 0)
                    self.assertTrue(item["x"] or item["y"], "a zero term was stored")

    def test_a_term_lands_in_the_box_its_power_names(self):
        terms = [R.term(0, 1, -8), R.term(1, 0, 129), R.term(2, 0, -663)]
        (x, y), refused = R.rows_for_step(terms, 0.5)
        self.assertEqual(refused, [])
        self.assertEqual(x, [1, 0, 0, 0, 0])          # t^0, t^1/2, t, t^3/2, t^2
        self.assertEqual(y, [-8, 0, 129, 0, -663])

    def test_a_power_off_the_step_is_refused_not_rounded(self):
        (x, y), refused = R.rows_for_step([R.term(1, 1, 1)], 0.75)
        self.assertEqual(x, [])
        self.assertEqual(len(refused), 1)
        self.assertIn("off the step", refused[0])

    def test_the_measurements_re_derive(self):
        """A stored bend or grid that a fresh measurement disagrees with is a bug."""
        document = R.read(FOUND)
        fresh = {row["name"]: row for row in R.derived(document)}
        for curve in document["curves"]:
            measured = curve.get("measured", {})
            again = fresh[curve["name"]]
            with self.subTest(name=curve["name"]):
                self.assertAlmostEqual(measured["bend"], again["bend"], places=2)
                self.assertEqual(measured["grid"], again["grid"])

    def test_the_old_flat_rows_are_still_read(self):
        """A curve pasted in the old shape is upgraded, not rejected."""
        upgraded = R.upgrade({"name": "old", "speedX": [1, 0, 0], "speedY": [-8, 129, -663],
                              "bend": 1.772, "pitch": 22})
        self.assertEqual([item["power"] for item in upgraded["terms"]], [0, 1, 2])
        self.assertEqual(upgraded["measured"]["grid"], 22)

    def test_a_bad_document_is_refused_before_it_is_written(self):
        bad = {"format": R.FORMAT, "curves": [
            {"name": "twice", "terms": [R.term(0, 1, 1)]},
            {"name": "twice", "terms": [R.term(0, 1, 1)]},
        ]}
        problems = R.validate(R.normalise(bad))
        self.assertTrue(any("used twice" in line for line in problems))

    def test_writing_refuses_a_document_with_problems(self):
        with self.assertRaises(ValueError):
            R.write(Path("/tmp/should-not-be-written.json"),
                    {"format": R.FORMAT, "curves": [{"name": "", "terms": []}]})


if __name__ == "__main__":
    unittest.main()
