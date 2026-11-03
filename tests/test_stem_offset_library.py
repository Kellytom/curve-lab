import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import stem_offset_library as O  # noqa: E402


class StemOffsetTest(unittest.TestCase):
    def test_cards_and_labels(self):
        O.build()
        self.assertGreaterEqual(len(O.CARDS), 12)
        labels = [c["label"] for c in O.CARDS]
        self.assertEqual(labels, [f"OffS{i}" for i in range(1, len(labels) + 1)])
        for card in O.CARDS:
            self.assertGreater(card["d"], 0.0)
            self.assertGreater(len(card["base"]), 8)
            self.assertGreater(len(card["plus"]), 8)
            self.assertGreater(len(card["minus"]), 8)

    def test_rails_are_two_offsets_apart(self):
        O.build()
        for card in O.CARDS:
            if card["label"] in ("OffS10", "OffS11", "OffS12"):
                continue                       # chain rails / two stems
            n = min(len(card["plus"]), len(card["minus"]))
            for i in range(0, n, max(1, n // 9)):
                gap = math.dist(card["plus"][i], card["minus"][i])
                self.assertAlmostEqual(gap, 2 * card["d"], places=9)

    def test_levien_and_chain_options(self):
        O.build()
        by = {c["label"]: c for c in O.CARDS}
        self.assertIn("fit_error", by["OffS1"])
        self.assertLess(by["OffS1"]["fit_error"], 0.01)
        self.assertIn("chain_error", by["OffS10"])
        self.assertLess(by["OffS10"]["chain_error"], 0.05)
        self.assertEqual(by["OffS10"]["folds"], 0)

    def test_conics_and_multiple(self):
        O.build()
        titles = [c["title"] for c in O.CARDS]
        self.assertIn("parallel parabola", titles)
        self.assertIn("parallel ellipse", titles)
        self.assertIn("parallel hyperbola", titles)
        self.assertIn("two stalks · envelopes separated", titles)

    def test_page(self):
        O.build()
        page = (ROOT / "workbench" / "stem-library-offset.html").read_text(
            encoding="utf-8")
        self.assertEqual(page.count("<svg"), len(O.CARDS))
        self.assertIn("2d apart", page)
        self.assertIn("Levien", page)
        self.assertIn("parallel parabola", page)
        self.assertIn("OffS12", page)


if __name__ == "__main__":
    unittest.main()
