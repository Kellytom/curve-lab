"""The memory is as new as the work. A stale handoff is a red gate.

The fault this guards: the handoff sat at 4 November while the tree moved for two
weeks, because `/fhandoff` was a command someone had to remember and nothing
failed when it was skipped.
"""

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "state" / "HANDOFF-int.md"
NEXT = ROOT / "next-fhandoff-int.md"


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


class MemoryFreshnessTest(unittest.TestCase):
    def test_the_handoff_is_not_older_than_the_last_commit_outside_state(self):
        text = HANDOFF.read_text(encoding="utf-8")
        dates = re.findall(r"^## (\d{4}-\d{2}-\d{2})", text, flags=re.M)
        self.assertTrue(dates, "the handoff has no dated section")
        newest = max(dates)
        last = git("log", "-1", "--format=%cs", "--", ".", ":(exclude)state", ":(exclude)workbench")
        if not last:
            self.skipTest("no commits yet")
        self.assertGreaterEqual(newest, last,
                                f"the handoff's newest section is {newest}; the last code commit is {last}. "
                                "Run the handoff step.")

    def test_the_next_action_names_a_commit_that_exists(self):
        text = NEXT.read_text(encoding="utf-8")
        match = re.search(r"commit ([0-9a-f]{7,40})", text)
        if not match:
            self.skipTest("the next action does not name a commit")
        self.assertEqual(0, subprocess.run(["git", "cat-file", "-e", match.group(1) + "^{commit}"],
                                           cwd=ROOT, capture_output=True).returncode,
                         f"the next action names {match.group(1)}, which is not a commit")


if __name__ == "__main__":
    unittest.main()
