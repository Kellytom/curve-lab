"""The tunnel run book: the Markdown is the source, the HTML twin is generated.

The fault this guards: a hostname or a command fixed in one twin and not the
other, so the operator follows a step that no longer exists.
"""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TunnelDocTest(unittest.TestCase):
    def test_the_twin_is_current(self):
        result = subprocess.run(
            [sys.executable, "scripts/tunnel_doc.py", "--check"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_the_run_book_names_both_ends(self):
        text = (ROOT / "docs" / "TUNNEL.md").read_text(encoding="utf-8")
        for heading in ("## One-time setup", "## Get in", "## Get out",
                        "## Turning it off for good", "## When it breaks"):
            self.assertIn(heading, text)
        self.assertIn("scripts/tunnel.sh start", text)
        self.assertIn("scripts/tunnel.sh stop", text)

    def test_the_service_script_is_runnable(self):
        script = ROOT / "scripts" / "service.sh"
        self.assertTrue(script.exists(), "scripts/service.sh is missing")
        self.assertTrue(script.stat().st_mode & 0o111, "service.sh is not executable")
        result = subprocess.run(["sh", "-n", str(script)], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        text = (ROOT / "docs" / "TUNNEL.md").read_text(encoding="utf-8")
        self.assertIn("scripts/service.sh install", text)

    def test_no_tunnel_secret_is_committed(self):
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
        for name in ("cert.pem", "config.yml"):
            self.assertNotIn(name, tracked)
        self.assertFalse((ROOT / "cert.pem").exists())


if __name__ == "__main__":
    unittest.main()
