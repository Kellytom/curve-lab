"""The septic sandbox: both panels, generated from the checked-in JavaScript."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
PAGE = ROOT / "workbench" / "ph-septic-sandbox.html"
JS = ROOT / "scripts" / "ph_septic_panels.js"


class TestSepticSandbox(unittest.TestCase):
    def test_the_sample_gallery_is_populated(self):
        import json
        document = json.loads((ROOT / "workbench" / "septic-samples.json").read_text())
        curves = document["curves"]
        self.assertEqual(len(curves), 40)
        for curve in curves:
            for key in ("speedX", "speedY", "bend", "pitch", "inflection", "closest"):
                self.assertIn(key, curve)
            self.assertEqual(len(curve["speedX"]), 4)
            self.assertEqual(len(curve["speedY"]), 4)
        page = PAGE.read_text()
        self.assertIn('class="samples"', page)
        self.assertEqual(page.count("<svg viewBox=\"0 0 480 250\""), 40)

    def test_the_named_curves_match_their_stated_metrics(self):
        import json
        document = json.loads((ROOT / "workbench" / "septic-curves.json").read_text())
        by_name = {curve["name"]: curve for curve in document["curves"]}
        half = by_name["half-heart"]
        self.assertAlmostEqual(half["bend"], 2.377, places=3)
        self.assertEqual(half["pitch"], 84000)
        self.assertAlmostEqual(half["inflection"], 0.368, places=3)
        self.assertAlmostEqual(half["closest"], 2.793, places=3)
        flourish = by_name["flourish-a"]
        self.assertAlmostEqual(flourish["bend"], 1.651, places=3)
        self.assertEqual(flourish["pitch"], 42000)
        self.assertAlmostEqual(flourish["inflection"], 0.466, places=3)
        self.assertAlmostEqual(flourish["closest"], 1.955, places=3)

    def test_the_promoted_curves_keep_their_gallery_numbers(self):
        """A promoted curve is gallery D's curve, renamed; not a new one."""
        import json
        gallery = json.loads((ROOT / "workbench" / "septic-samples.json").read_text())["curves"]
        by_speed = {(tuple(curve["speedX"]), tuple(curve["speedY"])): curve
                    for curve in gallery}
        named = json.loads((ROOT / "workbench" / "septic-curves.json").read_text())["curves"]
        by_name = {curve["name"]: curve for curve in named}
        promoted = {"small-loop", "tight-loop", "shallow-turn", "narrow-arch",
                    "vertical-s", "tight-hook", "straight-start", "long-sweep"}
        self.assertEqual(promoted - set(by_name), set())
        for name in sorted(promoted):
            curve = by_name[name]
            speeds = (tuple(curve["speedX"]), tuple(curve["speedY"]))
            self.assertIn(speeds, by_speed, f"{name} is not a gallery D curve")
            sample = by_speed[speeds]
            for key in ("bend", "pitch", "inflection", "closest"):
                with self.subTest(name=name, key=key):
                    self.assertEqual(curve[key], sample[key])

    def test_the_septic_curve_json_is_current(self):
        import json
        import septic_curves
        expected = json.loads(json.dumps(septic_curves.build()))
        self.assertEqual(json.loads((ROOT / "workbench" / "septic-curves.json").read_text()),
                         expected)

    def test_the_sandbox_default_matches_the_python_metrics(self):
        import ph_quintic_metrics as M
        m = M.metrics((2, -3, 3, 0.3), (2, -12, 12, 0))
        self.assertAlmostEqual(m["bend"], 1.850, places=3)
        self.assertEqual(m["pitch"], 700)
        self.assertAlmostEqual(m["inflection"], 0.494, places=3)
        self.assertAlmostEqual(m["closest"], 1.461, places=3)

    def test_the_page_exists_and_holds_both_panels(self):
        page = PAGE.read_text()
        for marker in ("a-controls", "a-plot", "b-controls", "b-plot",
                       "b-chord-chain", "b-chord-bars",
                       "c-controls", "c-plot", "c-readout",
                       "d-controls", "d-plot", "d-readout",
                       "b-open", "b-open-value", "b-lift", "b-lift-sign",
                       "the general polynomial", "the PH septic"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)

    def test_the_page_inlines_the_checked_in_javascript(self):
        page = PAGE.read_text()
        self.assertIn(JS.read_text().strip()[:200], page)

    def test_the_javascript_parses(self):
        result = subprocess.run(["node", "--check", str(JS)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_the_build_pipeline_keeps_both_panels(self):
        """generator, then the hub bar; the panels survive both."""
        subprocess.run([sys.executable, str(ROOT / "scripts" / "ph_septic_sandbox.py")],
                       check=True, capture_output=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "hub.py")],
                       check=True, capture_output=True)
        page = PAGE.read_text()
        for marker in ("a-controls", "b-controls", "all inputs"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)


if __name__ == "__main__":
    unittest.main()
