"""The hybrid desk's data: a formula for every candidate, and a record for every keep.

Spec: state/SPEC-hybrids-int.md. The fault this guards is the one the register already
names (a displayed number no current routine produces): a candidate with no formula, a
figure that is listed but not on disk, or a "keep" that never became a registry record.
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
        kept = [row["name"] for row in decisions if row.get("decision") == "keep"]
        registry = json.loads(REGISTRY.read_text())["curves"]
        aliases = {alias for record in registry for alias in record.get("aliases", [])}
        self.assertEqual([key for key in kept if key not in aliases], [],
                         "kept candidates with no registry record")


if __name__ == "__main__":
    unittest.main()
