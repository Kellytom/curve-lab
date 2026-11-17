"""Guards the square/frame lab: the controls, the manifest, the page."""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import square_frame  # noqa: E402

PAGE = ROOT / "workbench" / "square-frame.html"


class SquareFrameTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.generated = square_frame.page_html()

    def test_every_control_is_present(self):
        for control in ("sf-a", "sf-b", "sf-form", "sf-per-w", "sf-per-h",
                        "sf-pattern", "sf-leg", "sf-natural", "sf-size",
                        "sf-fill", "sf-alternate", "sf-frame", "sf-width",
                        "sf-plus", "sf-minus", "sf-profile", "sf-stage",
                        "sf-readout"):
            self.assertIn(f'id="{control}"', self.page, control)

    def test_the_page_computes_in_the_browser(self):
        self.assertIn('src="plate_math.js"', self.page)
        self.assertIn("PlateMath.design(", self.page)
        self.assertIn("PlateMath.group(", self.page)
        self.assertNotIn("square_lab.js", self.page)
        # no form: a page reload must never lose the settings
        self.assertNotIn("<form", self.page.lower())

    def test_the_generator_makes_the_page(self):
        without_bar = re.sub(r"<!-- hub-bar -->.*?<!-- /hub-bar -->", "",
                             self.page, flags=re.S)
        # the hub adds a newline after <body> for its bar; the generator does not
        without_bar = re.sub(r"<body>\n+", "<body>", without_bar)
        self.assertEqual(square_frame.page_html().strip(),
                         without_bar.strip())

    def test_the_curves_are_grouped_by_symmetry(self):
        self.assertIn("optgroup label=", self.page)
        self.assertIn("symmetric: [], asymmetric: []", self.page)
        self.assertIn('["symmetric", "asymmetric"]', self.page)
        self.assertIn("symmetry", self.page)

    def test_curve_b_offers_none_and_same(self):
        self.assertIn('["none", "same"]', self.page)
        self.assertIn('bChoice === "none"', self.page)
        self.assertIn('bChoice === "same"', self.page)

    def test_the_curves_are_inlined(self):
        self.assertIn("window.REAL_CURVES", self.page)
        self.assertNotIn('fetch("real-curves.json")', self.page)

    def test_the_inline_data_matches_the_file(self):
        data = json.loads((ROOT / "workbench" / "real-curves.json").read_text())
        match = re.search(r"window\.REAL_CURVES = (\{.*?\});</script>",
                          self.page, re.S)
        self.assertIsNotNone(match)
        inline = json.loads(match.group(1))
        self.assertEqual(inline, data)
        self.assertEqual(len(inline["curves"]), inline["count"])
        for row in inline["curves"]:
            speeds = list(row.get("speedX") or []) + list(row.get("speedY") or [])
            self.assertTrue(any(float(value) for value in speeds), row["name"])

    def test_the_manifest_names_the_page(self):
        manifest = json.loads((ROOT / "workbench" / "manifest.json").read_text())
        keys = {entry["key"]: entry for entry in manifest["pages"]}
        self.assertIn("square-frame", keys)
        self.assertEqual(keys["square-frame"]["file"], "square-frame.html")

    def test_the_stroke_floor_is_stated(self):
        self.assertIn("strokeFor", self.page)
        self.assertIn("1 point", self.page.lower())


if __name__ == "__main__":
    unittest.main()
