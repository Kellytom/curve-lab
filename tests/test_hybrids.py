"""The hybrid desk's data: a formula for every candidate, and a record for every keep.

Spec: state/SPEC-hybrids-int.md. The fault this guards is the one the register already
names (a displayed number no current routine produces): a candidate with no formula, a
figure that is listed but not on disk, or a "saved" that never became a registry record.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "workbench" / "hybrids.json"
DECISIONS = ROOT / "workbench" / "sandbox-curves.json"
REGISTRY = ROOT / "workbench" / "curve-registry.json"
FIGURES = ROOT / "app" / "public" / "hybrid-figures"


class Hybrids(unittest.TestCase):
    def setUp(self):
        self.candidates = json.loads(CANDIDATES.read_text())["candidates"]

    def test_every_candidate_carries_its_formula(self):
        """2026-11-20: "store a standard version of the formula ... so an outside search
        will find it" — each record names its plain, rational and search form."""
        missing = []
        for row in self.candidates:
            formula = row.get("formula") or {}
            for field in ("plain", "rational", "parameter", "use", "search"):
                if not formula.get(field):
                    missing.append(f'{row["id"]}:{field}')
        self.assertEqual(missing[:10], [], "candidates without a complete formula")

    def test_every_candidate_has_its_figure_on_disk(self):
        missing = [row["id"] for row in self.candidates
                   if not (FIGURES / row["figure"]).exists()]
        self.assertEqual(missing[:10], [], "candidates with no figure file")

    def test_every_kept_candidate_is_a_registry_record(self):
        """A keep is promoted by scripts/promote_hybrids.py; if the decision is visible in
        the JSON and the record is not, the export and the registry have drifted."""
        if not DECISIONS.exists():
            self.skipTest("no decisions exported yet")
        decisions = json.loads(DECISIONS.read_text()).get("curves", [])
        kept = [row["name"] for row in decisions if row.get("decision") == "saved"]
        registry = json.loads(REGISTRY.read_text())["curves"]
        aliases = {alias for record in registry for alias in record.get("aliases", [])}
        self.assertEqual([key for key in kept if key not in aliases], [],
                         "kept candidates with no registry record")


class Rejected(unittest.TestCase):
    def test_every_rejected_candidate_is_on_record(self):
        """2026-11-20: "keep a record of the rejected ones ... so we dont try them again".
        The file is JSON only, and nothing there is ever removed."""
        if not DECISIONS.exists():
            self.skipTest("no decisions exported yet")
        record = ROOT / "workbench" / "hybrid-rejected.json"
        self.assertTrue(record.exists(), "the rejected record is missing")
        rejected = {row["name"] for row in json.loads(DECISIONS.read_text()).get("curves", [])
                    if row.get("decision") == "rejected"}
        on_file = {row["id"] for row in json.loads(record.read_text())["rejected"]}
        self.assertEqual(sorted(rejected - on_file), [],
                         "rejected decisions missing from workbench/hybrid-rejected.json")


class TransformSlot(unittest.TestCase):
    def test_every_record_carries_its_transform(self):
        """2026-11-20: "they will need a matrix in the database" — 90° is a quarter turn and
        exact; 45° is display only, because √2/2 is irrational. The slot is on every record."""
        registry = json.loads(REGISTRY.read_text())["curves"]
        missing = []
        for record in registry:
            slot = record.get("transform") or {}
            if not all(key in slot for key in ("degrees", "matrix", "exact")):
                missing.append(record["uid"])
            matrix = slot.get("matrix")
            if not (isinstance(matrix, list) and len(matrix) == 2 and all(len(row) == 2 for row in matrix)):
                missing.append(f'{record["uid"]}:matrix')
        self.assertEqual(missing[:10], [], "records without a 2×2 transform")


class ConversionSlot(unittest.TestCase):
    def test_every_record_reserves_the_conversion_slot(self):
        """2026-11-20: "they will have to come over to this algorithm eventually, so leave
        space in that record for the new improved formula" — every record carries the slot,
        with `formulaNext` present and null until the improved formula exists."""
        registry = json.loads(REGISTRY.read_text())["curves"]
        missing = []
        for record in registry:
            slot = record.get("conversion") or {}
            for field in ("algorithm", "status", "target"):
                if field not in slot:
                    missing.append(f'{record["uid"]}:{field}')
            if "formulaNext" not in slot:
                missing.append(f'{record["uid"]}:formulaNext')
        self.assertEqual(missing[:10], [], "records without the conversion slot")


if __name__ == "__main__":
    unittest.main()
