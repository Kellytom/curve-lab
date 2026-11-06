"""Guards the W03 fleur-grammar report: spans, corners, seam, clearance."""

import unittest
from pathlib import Path

from curve_lab.grammar import study_01, study_01_report

ROOT = Path(__file__).resolve().parents[1]


class FleurGrammarTest(unittest.TestCase):
    def setUp(self):
        self.report = study_01_report()
        self.page = (ROOT / "workbench" / "fleur-grammar.html").read_text(
            encoding="utf-8")

    def test_the_port_states_its_spans_and_corners(self):
        self.assertEqual(self.report["spans"], 26)
        self.assertEqual(self.report["spans_half"], 11)
        self.assertEqual(self.report["spans_band"], 4)
        self.assertEqual(self.report["corners"], 9)
        self.assertGreater(self.report["max_corner"], 170.0)
        self.assertIn("26 spans", self.page)
        self.assertIn(f"{self.report['max_corner']:.2f}", self.page)

    def test_the_seam_is_declared_and_clearance_passes(self):
        self.assertEqual(self.report["contacts"], 2)
        self.assertEqual(len(study_01().contacts), 2)
        self.assertEqual(self.report["folds"], 0)
        self.assertEqual(self.report["disallowed"], 0)
        self.assertTrue(self.report["clearance_ok"])
        self.assertIn("declared contact", self.page)

    def test_no_false_copy_error_claim(self):
        self.assertIsNone(self.report["copy_error"])
        self.assertIn("not measured", self.page)
        self.assertNotIn("copy error 0", self.page)


if __name__ == "__main__":
    unittest.main()
