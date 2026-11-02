import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import heart_forms as H  # noqa: E402


class HeartFormsTest(unittest.TestCase):
    def test_forms(self):
        self.assertGreaterEqual(len(H.FORMS), 15)

    def test_each_form_has_points(self):
        for form in H.FORMS:
            with self.subTest(form=form["key"]):
                branches = form["branches"]()
                self.assertGreaterEqual(len(branches), 1)
                pts = [p for branch in branches for p in branch]
                self.assertGreater(len(pts), 500)

    def test_page_has_all_figures(self):
        page = (ROOT / "workbench" / "heart-forms.html").read_text(
            encoding="utf-8")
        self.assertEqual(page.count("<svg"), len(H.FORMS))
        for form in H.FORMS:
            self.assertIn(form["key"], page)


if __name__ == "__main__":
    unittest.main()
