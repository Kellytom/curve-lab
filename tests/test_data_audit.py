"""The data contract: every dataset declares its format, and the registry agrees.

The fault this guards: a dataset that changes shape or loses its version without
anything noticing, so a reader quietly gets an empty list. The register holds
that fault twice — row 19 (a format change orphaned a reader) and row 23 (a
failed read became a write).
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.datafile import FORMATS, DataFileError, load  # noqa: E402


class DataContractTest(unittest.TestCase):
    def test_every_file_is_stamped_as_registered(self):
        result = subprocess.run(
            [sys.executable, "scripts/data_format.py", "--check"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_every_file_reads_through_the_loader(self):
        result = subprocess.run(
            [sys.executable, "scripts/data_audit.py"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_the_registry_names_every_file_and_nothing_else(self):
        on_disk = sorted(p.name for p in (ROOT / "workbench").glob("*.json"))
        self.assertEqual(sorted(FORMATS), on_disk)
        doc = (ROOT / "state" / "DATA-int.md").read_text(encoding="utf-8")
        for name in on_disk:
            self.assertIn(f"`{name}`", doc, f"{name} is not in state/DATA-int.md")

    def test_the_loader_refuses_an_unversioned_object(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "loose.json"
            path.write_text(json.dumps({"curves": []}), encoding="utf-8")
            with self.assertRaises(DataFileError):
                load(path)
            path.write_text(json.dumps({"format": "x/1"}), encoding="utf-8")
            with self.assertRaises(DataFileError):
                load(path, "y/1")

    def test_a_broken_file_is_named_not_swallowed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "broken.json"
            path.write_text("{ not json", encoding="utf-8")
            with self.assertRaises(DataFileError) as caught:
                load(path)
            self.assertIn("not JSON", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
