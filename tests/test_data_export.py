"""The visible record under `data/` is current, readable and complete.

The database is the source of truth; `data/*.json` is the same record for a
session that cannot open SQLite. This test fails when the files fall behind the
database, when a file cannot be parsed, or when the dictionary is missing.

The check itself is `scripts/export-data.mjs --check`, which recomputes every
table and compares the row count and a hash with `data/manifest.json`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def node() -> str:
    return os.environ.get("NODE24") or shutil.which("node") or str(Path.home() / "node24" / "bin" / "node")


class DataExportTest(unittest.TestCase):
    def test_the_visible_record_is_current(self) -> None:
        result = subprocess.run(
            [node(), "scripts/export-data.mjs", "--check"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_every_file_parses_and_agrees_with_the_manifest(self) -> None:
        manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
        for name, entry in manifest["files"].items():
            body = json.loads((DATA / entry["file"]).read_text(encoding="utf-8"))
            self.assertIn("format", body, name)
            self.assertEqual(entry["count"], body["count"], name)
            rows = body["rows"]
            seen = len(rows) if isinstance(rows, list) else sum(len(item) for item in rows.values())
            self.assertEqual(entry["count"], seen, f"{name}: count does not match the rows")

    def test_the_dictionary_and_the_schema_are_present(self) -> None:
        self.assertTrue((DATA / "README.md").is_file(), "data/README.md is the dictionary")
        schema = json.loads((DATA / "schema.json").read_text(encoding="utf-8"))
        for name in ("curves.json", "metrics.json", "sandbox-curves.json"):
            self.assertIn(name, schema["files"], name)
            self.assertTrue(schema["files"][name]["fields"], f"{name} has no fields in schema.json")

    def test_every_curve_carries_a_formula(self) -> None:
        body = json.loads((DATA / "curves.json").read_text(encoding="utf-8"))
        for row in body["rows"]:
            formula = row.get("formula") or {}
            for key in ("plain", "rational", "parameter", "use", "search"):
                self.assertTrue(formula.get(key), f"{row['uid']} has no formula.{key}")


if __name__ == "__main__":
    unittest.main()
