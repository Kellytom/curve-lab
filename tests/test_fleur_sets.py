"""Guards W04: twenty sets from one function, same grammar, no retuning."""

import math
import unittest
from pathlib import Path

from curve_lab import grammar
from curve_lab.fleur_sets import SETS

ROOT = Path(__file__).resolve().parents[1]


class FleurSetsTest(unittest.TestCase):
    def test_twenty_sets_p01_to_p20(self):
        self.assertEqual(len(SETS), 20)
        self.assertEqual([s["id"] for s in SETS],
                         [f"P{i:02d}" for i in range(1, 21)])
        self.assertEqual(SETS[0]["opts"], grammar.STUDY_01)
        for item in SETS:
            self.assertEqual(set(item["opts"]), set(grammar.STUDY_01))

    def test_every_set_uses_the_same_grammar(self):
        for item in SETS:
            piece = grammar.study(item["opts"], name=item["name"])
            spans = sum(len(t.design.segments) for t in piece.traces)
            corners = sum(
                1 for t in piece.traces for s in t.design.segments
                if abs(math.degrees(getattr(s, "corner", 0.0))) > 1e-9)
            self.assertEqual(spans, 15, item["id"])
            self.assertEqual(corners, 9, item["id"])
            self.assertEqual(len(piece.contacts), 2, item["id"])

    def test_the_seam_clearance_passes(self):
        from curve_lab.clearance import piece_clearance
        for item in SETS[::7]:
            piece = grammar.study(item["opts"], name=item["name"])
            report = piece_clearance(piece, clearance=1.0)
            self.assertTrue(report["ok"], item["id"])
            self.assertEqual(report["disallowed"], [], item["id"])

    def test_the_page_has_twenty_cards(self):
        page = (ROOT / "workbench" / "fleur-sets.html").read_text(
            encoding="utf-8")
        self.assertEqual(page.count('<section class="card">'), 20)
        self.assertIn("P01", page)
        self.assertIn("P20", page)
        self.assertIn("ornament_set.js", page)
        self.assertIn("rail error", page)


if __name__ == "__main__":
    unittest.main()
