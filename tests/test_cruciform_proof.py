"""Guards the cruciform proof: junctions, merges, sections, terminals."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cruciform_proof as C  # noqa: E402


class CruciformProofTest(unittest.TestCase):
    def setUp(self):
        self.page = (ROOT / "workbench" / "cruciform-proof.html").read_text(
            encoding="utf-8")
        self.data = C.proof_data()

    def test_two_declared_junctions(self):
        self.assertEqual(self.data["junctions"], 2)
        self.assertEqual(self.data["merges"], 2)
        self.assertEqual(self.data["join"], "G1")
        self.assertAlmostEqual(self.data["arc"], 0.6 * 3.141592653589793 / 2, 4)
        self.assertAlmostEqual(self.data["curvature_step"], 1.0 / 0.6, 6)
        self.assertIn("G1", self.page)
        self.assertIn("declared", self.page)

    def test_four_terminals_and_seven_sections(self):
        self.assertEqual(self.data["terminals"], 4)
        self.assertEqual(self.data["sections"], 7)
        self.assertIn("R = 2 × offset", self.page)
        self.assertIn("section", self.page.lower())

    def test_the_crossing_is_declared_not_hidden(self):
        left = C._junction(-1)
        built = left.build()
        self.assertTrue(built["contact"].waives_clearance)
        self.assertEqual(built["report"]["join"], "G1")
        self.assertIn("not as an undeclared X", self.page)


if __name__ == "__main__":
    unittest.main()
