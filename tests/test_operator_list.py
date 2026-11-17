"""The button list on disk is the list the records give, and it is current.

`workbench/operator-list.json` is the copy the page seeds a fresh browser from.
If it goes stale it is worse than absent: a browser reset would restore old
curves and quietly miss new ones. This test rebuilds the list in memory and
compares it with the file, the same way the curve catalogues are compared with
their tables.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import operator_list  # noqa: E402


class TestOperatorList(unittest.TestCase):
    def test_the_file_is_what_the_records_give(self):
        """A stale list would restore the wrong buttons after a browser reset."""
        document = json.loads(operator_list.OUT.read_text())
        built = operator_list.collect()
        self.assertEqual([entry["name"] for entry in built],
                         [entry["name"] for entry in document["saved"]])

    def test_every_stored_curve_has_a_button(self):
        """Measured 2026-11-16: the B panel showed 33 seeds and none of the curves."""
        document = json.loads(operator_list.OUT.read_text())
        names = {entry["name"] for entry in document["saved"]}
        stored = set()
        if operator_list.FOUND.exists():
            stored |= {c["name"] for c in json.loads(operator_list.FOUND.read_text())["curves"]}
        if operator_list.MOVED.exists():
            stored |= {c["name"] for c in json.loads(operator_list.MOVED.read_text())["curves"]}
        stored |= {json.loads(p.read_text())["name"]
                   for p in operator_list.CURVES.glob("*/curve.json")}
        self.assertEqual(set(), stored - names)

    def test_every_button_can_be_drawn(self):
        """A button with no rows loads nothing: the record must carry both speeds."""
        document = json.loads(operator_list.OUT.read_text())
        for entry in document["saved"]:
            with self.subTest(name=entry["name"]):
                self.assertTrue(entry.get("speedX"))
                self.assertTrue(entry.get("speedY"))


if __name__ == "__main__":
    unittest.main()
