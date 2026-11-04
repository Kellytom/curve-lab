import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IntegerG2EditorTest(unittest.TestCase):
    def test_page(self):
        page = (ROOT / "workbench" / "integer-g2-editor.html").read_text(
            encoding="utf-8")
        self.assertIn("Integer G2 pair · drag probe", page)
        self.assertIn('id="editor"', page)
        self.assertIn('id="reset"', page)
        self.assertIn('id="snap"', page)
        self.assertIn('id="tangents"', page)
        self.assertIn("G2 exact", page)
        self.assertIn("A end κ", page)
        self.assertIn("B start κ", page)
        self.assertIn("pointerdown", page)
        self.assertIn("integer", page)

    def test_manifest_and_link(self):
        manifest = (ROOT / "workbench" / "manifest.json").read_text(
            encoding="utf-8")
        self.assertIn('"integer-g2-editor"', manifest)
        page = (ROOT / "workbench" / "integer-g2.html").read_text(
            encoding="utf-8")
        self.assertIn('href="integer-g2-editor.html"', page)


if __name__ == "__main__":
    unittest.main()
