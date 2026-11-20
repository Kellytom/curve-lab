"""The dictionary in `data/README.md` names every field the record carries.

`data/schema.json` is built from the rows themselves, so it cannot drift from
the data; the prose can. This test fails when a field exists in a file but is
not named in the dictionary, so a new column is a documentation task, not a
surprise for the next reader.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class DataDictionaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((DATA / "schema.json").read_text(encoding="utf-8"))
        cls.readme = (DATA / "README.md").read_text(encoding="utf-8")

    def test_every_field_is_named_in_the_dictionary(self) -> None:
        missing = []
        for file, entry in self.schema["files"].items():
            for field in entry["fields"]:
                if not re.search(rf"\b{re.escape(field)}\b", self.readme):
                    missing.append(f"{file}: {field}")
        self.assertEqual([], missing, "fields not named in data/README.md")

    def test_every_file_is_described(self) -> None:
        for file in self.schema["files"]:
            self.assertIn(f"`{file}`", self.readme, f"{file} has no section in the dictionary")


if __name__ == "__main__":
    unittest.main()
