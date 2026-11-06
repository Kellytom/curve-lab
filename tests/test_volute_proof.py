"""Guards the volute proof: the page must state the spine's own numbers."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import volute_proof as V  # noqa: E402


class VoluteProofTest(unittest.TestCase):
    def setUp(self):
        self.page = (ROOT / "workbench" / "volute-proof.html").read_text(
            encoding="utf-8")
        self.data = V.proof_data()

    def test_counts_come_from_the_spine(self):
        self.assertEqual(self.data["chords"], 33)
        self.assertEqual(self.data["nodes"], 34)
        self.assertEqual(self.data["triangle"], "79-3120-3121")
        self.assertGreater(self.data["peak"], 700.0)
        self.assertEqual(self.data["radius"], 2.0 * self.data["offset"])
        self.assertIn("33 equal chords", self.page)
        self.assertIn(f"{self.data['peak']:.1f}°", self.page)

    def test_the_rules_are_stated(self):
        self.assertIn("R = 2 × offset", self.page)
        self.assertIn("2d = 0.52", self.page)
        self.assertIn("seagrass", self.page)
        self.assertIn("No bare tip", self.page)
        self.assertIn("Infinity:", self.page)
        self.assertIn("fitted", self.page)

    def test_nodes_are_exactly_rational(self):
        _, _, chain = V._chain()
        nodes, scale = chain.integer_form()
        self.assertEqual(len(nodes), self.data["nodes"])
        self.assertTrue(all(isinstance(x, int) and isinstance(y, int)
                            for x, y in nodes))
        self.assertGreater(scale, 1)


if __name__ == "__main__":
    unittest.main()
