"""The G3 showcase document: Markdown source, generated HTML twin, counts.

`scripts/g3_showcase_doc.py --check` is the gate: it fails when the HTML twin
no longer matches the Markdown or when the counts block is stale against the
catalogue and the showcase page.
"""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "G3-SHOWCASE.md"
HTML = ROOT / "docs" / "G3-SHOWCASE.html"


class TestG3ShowcaseDoc(unittest.TestCase):
    def test_the_markdown_has_the_required_sections(self):
        md = MD.read_text(encoding="utf-8")
        for section in ("What it is for", "The continuity ladder and the gate",
                        "Degree: cubic first", "The LAC correction",
                        "The page: what is where", "The handoff table",
                        "The error tables", "Reproduce it", "Counts"):
            with self.subTest(section=section):
                self.assertIn(section, md)

    def test_the_markdown_states_the_gates_and_the_rule(self):
        md = MD.read_text(encoding="utf-8")
        for phrase in ("1e-9", "1e-5", "10% of its chord", "cubic first",
                       "S44", "Inkscape", "glyph", "quintic"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, md)

    def test_the_html_twin_carries_the_same_content(self):
        html = HTML.read_text(encoding="utf-8")
        for phrase in ("G3 showcase", "1e-9", "cubic first", "S44",
                       "Inkscape", "source-sha:"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, html)

    def test_the_document_is_current(self):
        result = subprocess.run(
            [sys.executable, "scripts/g3_showcase_doc.py", "--check"],
            cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0,
                         result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
