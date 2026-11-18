"""The LLM index is true: every link exists, and the long form is current.

`llms.txt` is the short map an agent reads first; `llms-full.txt` is the same
documents in one file. A dead link or a stale copy sends a reader to a page that
is not there, which is the fault this test prevents.
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LlmsTest(unittest.TestCase):
    def test_every_relative_link_in_llms_txt_exists(self):
        text = (ROOT / "llms.txt").read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+)\)", text)
        local = [link for link in links if not link.startswith(("http://", "https://", "#"))]
        self.assertTrue(local, "llms.txt has no local links")
        for link in local:
            with self.subTest(link=link):
                self.assertTrue((ROOT / link).exists(), f"{link} is not in the repository")

    def test_llms_full_is_current(self):
        result = subprocess.run(
            [sys.executable, "scripts/llms_full.py", "--check"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
