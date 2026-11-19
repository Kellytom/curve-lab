"""The DeepSeek1 ↔ DeepSeek2 mailbox is a protocol, not a habit.

The faults this guards:
- an entry with no shape, so the other session cannot tell a job from a note;
- a "done" with no command that proves it — the fault class the register
  already names;
- a log that grows until a session spends its context on history.
"""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "mailbox.py"


class Mailbox(unittest.TestCase):
    def run_mailbox(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True, text=True, cwd=ROOT,
        )

    def test_both_mailboxes_parse_and_every_done_has_its_proof(self):
        result = self.run_mailbox("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_read_is_short(self):
        """A session reads the newest entry, not the transcript."""
        result = self.run_mailbox("--read", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(len(result.stdout.splitlines()), 120, "the read is not short")

    def test_the_mailbox_is_still_bounded(self):
        from scripts.mailbox import MAX_LINES
        for name in ("deep-to-side.md", "side-to-deep.md"):
            lines = (ROOT / "archive" / "notes" / name).read_text(encoding="utf-8").splitlines()
            self.assertLessEqual(len(lines), MAX_LINES, f"{name} needs rotating")


if __name__ == "__main__":
    unittest.main()
