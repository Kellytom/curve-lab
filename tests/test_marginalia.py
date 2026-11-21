"""Marginalia: every curve as an ornament, at a quarter of the text width.

The theme is a recorded customisation of Starlight: a manifest of one ornament per curve,
the generated SVGs, a Head override that picks four per page, and a CSS layer that places
them. These tests keep the manifest complete and the template wired.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "app" / "src" / "theme" / "marginalia" / "ornaments.json"
CSS = ROOT / "app" / "src" / "theme" / "marginalia" / "marginalia.css"
CONFIG = ROOT / "app" / "astro.config.mjs"
GALLERY = ROOT / "app" / "src" / "pages" / "ornaments.astro"
DOCS = ROOT / "app" / "src" / "content" / "docs" / "docs" / "marginalia.md"
SVGS = ROOT / "app" / "public" / "ornaments"
REGISTRY = ROOT / "workbench" / "curve-registry.json"


class MarginaliaTest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_the_manifest_names_every_curve(self):
        self.assertEqual(self.manifest["format"], "curve-lab.marginalia/1")
        self.assertEqual(self.manifest["count"], len(self.manifest["curves"]))
        self.assertEqual({curve["uid"] for curve in self.manifest["curves"]},
                         {curve["uid"] for curve in self.registry["curves"]})

    def test_the_scale_is_a_quarter(self):
        self.assertEqual(self.manifest["scale"], 0.25)
        self.assertIn("--marginalia-scale: 0.25", CSS.read_text(encoding="utf-8"))

    def test_the_ornaments_are_single_stroke(self):
        files = sorted(SVGS.glob("*.svg"))
        if not files:
            self.skipTest("run node scripts/marginalia.mjs first (predev does)")
        for curve in self.manifest["curves"][:25]:
            svg = (SVGS / f"{curve['uid']}.svg")
            self.assertTrue(svg.exists(), curve["uid"])
            text = svg.read_text(encoding="utf-8")
            self.assertIn('stroke="currentColor"', text, curve["uid"])
            self.assertIn('fill="none"', text, curve["uid"])

    def test_the_template_is_wired(self):
        config = CONFIG.read_text(encoding="utf-8")
        self.assertIn("marginalia.css", config)
        self.assertIn("Head:", config)
        self.assertTrue(GALLERY.exists(), "the /ornaments gallery page")
        docs = DOCS.read_text(encoding="utf-8")
        self.assertIn("/ornaments/", docs)
        self.assertTrue((ROOT / "scripts" / "marginalia.mjs").exists())
        self.assertTrue((ROOT / "app" / "src" / "theme" / "marginalia" / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
