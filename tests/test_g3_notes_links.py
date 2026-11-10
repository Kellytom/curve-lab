"""Every figure links to its own notes entry, and the notes link back.

The showcase panels carry a `g3-notes.html#note-...` link on the title and the
curve. The notes page carries the matching `id`, the measurement, the fix note
and the join table, plus a back-link to the figure anchor.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "workbench" / "g3-showcase.html"
NOTES = ROOT / "workbench" / "g3-notes.html"


class TestNotesLinks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.show = SHOW.read_text(encoding="utf-8")
        cls.notes = NOTES.read_text(encoding="utf-8")

    def test_every_figure_links_to_a_notes_entry(self):
        hrefs = set(re.findall(
            r'href="g3-notes\.html#(note-[^"]+)"', self.show))
        self.assertGreaterEqual(len(hrefs), 160)
        for href in hrefs:
            with self.subTest(note=href):
                self.assertIn(f'id="{href}"', self.notes)

    def test_every_notes_entry_links_back_to_its_figure(self):
        anchors = set(re.findall(
            r'g3-showcase\.html#(fig-\d+)', self.notes))
        self.assertGreaterEqual(len(anchors), 150)
        show_ids = set(re.findall(r'id="(fig-\d+)"', self.show))
        for anchor in anchors:
            with self.subTest(figure=anchor):
                self.assertIn(anchor, show_ids)

    def test_the_nephroid_note_names_the_two_true_cusps(self):
        self.assertIn("nephroid", self.notes)
        self.assertIn("(0.00, -4.00), (0.00, 4.00)", self.notes)


if __name__ == "__main__":
    unittest.main()
