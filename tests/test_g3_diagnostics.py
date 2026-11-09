"""The tightest-span diagnostics: red rings on both figures, and a zoom.

The page is generated from the catalogue's own fits. These tests read the
generated JSON and page; they do not re-run the fit.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "workbench" / "g3-diagnostics.json"
PAGE = ROOT / "workbench" / "g3-diagnostics.html"


class TestDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.curves = cls.data["curves"]

    def test_count_matches_the_curve_list(self):
        self.assertEqual(self.data["count"], len(self.curves))
        self.assertGreaterEqual(len(self.curves), 5)

    def test_rows_are_below_the_display_threshold(self):
        for row in self.curves:
            with self.subTest(curve=row["key"]):
                self.assertLess(row["min_speed"], 0.25)
                self.assertGreaterEqual(row["min_speed"], 0.10)
                self.assertIsNotNone(row["problem"])

    def test_every_row_is_drawn(self):
        for row in self.curves:
            with self.subTest(curve=row["key"]):
                self.assertIn(f"Fig. H · {row['key']}", self.page)

    def test_red_rings_are_in_both_figures(self):
        blocks = self.page.split('<section class="panel">')[1:]
        self.assertEqual(len(blocks), len(self.curves))
        for block in blocks:
            svgs = block.split("<svg")[1:]
            self.assertEqual(len(svgs), 2)
            with self.subTest(panel=block.split("<h2>")[1].split(" <span")[0]):
                self.assertGreaterEqual(svgs[0].count("#a23b2a"), 1)
                self.assertGreaterEqual(svgs[1].count("#a23b2a"), 1)

    def test_each_panel_has_a_zoom_button(self):
        self.assertEqual(self.page.count('class="zoom-btn"'), len(self.curves))
        self.assertIn("classList.toggle('zoom')", self.page)

    def test_the_ground_label_is_below_the_line(self):
        block = self.page.split('<section class="panel">')[1]
        svg = block.split("<svg", 1)[1]
        line = re.search(
            r'<line x1="[\d.]+" y1="([\d.]+)" x2="[\d.]+" y2="([\d.]+)" '
            r'stroke="#2e2413" stroke-width="1"/>', svg)
        label = re.search(r'<text x="[\d.]+" y="([\d.]+)"[^>]*>ground</text>', svg)
        self.assertIsNotNone(line)
        self.assertIsNotNone(label)
        self.assertGreater(float(label.group(1)), float(line.group(2)))

    def test_the_page_states_the_floor(self):
        self.assertIn("10% of its chord speed", " ".join(self.page.split()))


if __name__ == "__main__":
    unittest.main()
