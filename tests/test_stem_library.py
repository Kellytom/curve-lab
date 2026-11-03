import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import stem_library as L  # noqa: E402


class StemLibraryTest(unittest.TestCase):
    def test_cards(self):
        L.build()
        self.assertGreaterEqual(len(L.CARDS), 60)
        groups = {c["group"] for c in L.CARDS}
        self.assertIn("Log-aesthetic", groups)
        self.assertIn("Spiral turns", groups)

    def test_page_has_all_cards(self):
        page = (ROOT / "workbench" / "stem-library.html").read_text(
            encoding="utf-8")
        self.assertEqual(page.count("<svg"), len(L.CARDS))
        self.assertIn("S01", page)
        self.assertIn(f"S{len(L.CARDS):02d}", page)


if __name__ == "__main__":
    unittest.main()
