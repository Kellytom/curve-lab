"""Guards the fleur proof: the page must state the study's own numbers."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fleur_proof as F  # noqa: E402


class FleurProofTest(unittest.TestCase):
    def setUp(self):
        self.page = (ROOT / "workbench" / "fleur-proof.html").read_text(
            encoding="utf-8")
        self.data = F.proof_data()

    def test_counts_come_from_the_grammar(self):
        self.assertEqual(self.data["spans"], 26)
        self.assertEqual(self.data["half_spans"], 11)
        self.assertEqual(self.data["band_spans"], 4)
        self.assertEqual(self.data["offset"], 12.5)
        self.assertEqual(self.data["radius"], 25.0)
        self.assertGreater(self.data["integer_nodes"], 0)
        self.assertGreater(self.data["petal_length"], 100.0)
        self.assertIn(
            f"{self.data['half_spans']} half + {self.data['half_spans']} "
            f"mirrored + {self.data['band_spans']} band = {self.data['spans']}",
            self.page)

    def test_the_ending_rule_is_stated(self):
        self.assertIn("R = 2 × offset", self.page)
        self.assertIn("cone terminal", self.page)
        self.assertIn("seagrass", self.page)
        self.assertIn("branch", self.page)
        self.assertIn("No bare tip".lower(), self.page.lower())
        self.assertIn("Infinity:", self.page)
        self.assertIn("Grounded:", self.page)

    def test_every_integer_node_is_on_the_page(self):
        data = F.proof_data()
        self.assertEqual(self.page.count("<svg"), 2)
        # the marks are drawn as diamonds; one per integer node
        self.assertEqual(self.page.count('fill="#c9a441"'), data["integer_nodes"] + 2)


if __name__ == "__main__":
    unittest.main()
