"""The browser-side scale must equal the Python exact scale.

`workbench/ph-families-app.js` recomputes the milestone scale in BigInt so the
slider can answer live.  This test runs that code under node with the DOM
stubbed out and compares it, rung by rung, with `generators.PHCurve.scale(m)`.
If the two ever disagree, the page is claiming a number it cannot back.
"""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "workbench" / "ph-families-app.js"

CASES = [
    ((1,), (1, 1), (1, -1)),
    ((1,), (2, -2), (1, -2)),
    ((1, 2), (1, -1), (1, -2)),
    ((2, 1), (1, 2), (2, -1)),
    ((1,), (1, 2, 1), (1, -1, 1)),
    ((1, 1, 1), (2, 1), (1, -1)),
    ((1, 2), (-1, 1, 0), (2, -1, 0)),
    ((1,), (1, 2, 1, 1), (1, -1, 1, 0)),
    ((1, 2), (1, 2, 1, 0), (1, -1, 1, 1)),
]


@unittest.skipUnless(shutil.which("node"), "node is needed for the app check")
class TestPHFamiliesApp(unittest.TestCase):
    def test_scale_matches_python(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import generators as G

        harness = """
const fs = require('fs');
global.window = { PH_PRESETS: [], PH_NO_INIT: true };
new Function(fs.readFileSync(process.argv[2], 'utf8'))();
const cases = JSON.parse(process.argv[3]);
const out = cases.map(([h, u, v, m]) => {
  const r = window.PH_APP.scaleAndHits(h, u, v, m);
  return { scale: r.scale.toString(), hits: r.hits, n: r.n };
});
console.log(JSON.stringify(out));
"""
        payload = [[list(h), list(u), list(v), 4] for h, u, v in CASES]
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(harness)
            script = fh.name
        try:
            r = subprocess.run(["node", script, str(APP), json.dumps(payload)],
                               capture_output=True, text=True, cwd=ROOT)
        finally:
            Path(script).unlink(missing_ok=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout)
        for (h, u, v), row in zip(CASES, got):
            n = len(h) - 1 + 2 * (max(len(u), len(v)) - 1) + 1
            pc = G.PHCurve(n, u=u, v=v, h=h)
            with self.subTest(h=h, u=u, v=v):
                self.assertEqual(row["n"], n)
                self.assertEqual(row["scale"], str(pc.scale(4)))
                self.assertEqual(row["hits"], 5)


if __name__ == "__main__":
    unittest.main()
