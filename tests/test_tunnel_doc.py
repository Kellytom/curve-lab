"""The tunnel run book, and the secrets it must never carry.

Starlight renders the Markdown now, so there is one copy of the page. These
checks guard the run book's headings and the rule that no tunnel secret is
committed.
"""

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "app" / "src" / "content" / "docs" / "docs" / "tunnel.md"


class TunnelDocTest(unittest.TestCase):
    def test_the_run_book_names_both_ends(self):
        text = DOC.read_text(encoding="utf-8")
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
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("scripts/service.sh install", text)
        source = script.read_text(encoding="utf-8")
        self.assertIn("restart [app|tunnel|all]", source)
        self.assertIn("restart app", text)

    def test_no_tunnel_secret_is_committed(self):
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
        paths = tracked.splitlines()
        self.assertNotIn("cert.pem", tracked)
        self.assertNotIn(".cloudflared/", tracked)
        self.assertNotIn("config.yml", paths)  # a root cloudflared config
        self.assertFalse((ROOT / "cert.pem").exists())


if __name__ == "__main__":
    unittest.main()
