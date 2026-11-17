"""The reading list's counts, and the counter that was blind to numbered rows.

The fault, as the operator saw it: the list said `HANDOFF-int.md` was 2,226
lines when it was 2,353, and `scripts/reading_counts.py` answered "counts
already right" anyway. Its row pattern expected the file name in the second
column, but every Tier 0 row is numbered, so the name is in the third. The
counter skipped every row it was written to maintain.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIST = ROOT / "state" / "READING-int.md"


class TestReadingCounts(unittest.TestCase):
    def test_a_numbered_row_is_one_the_counter_recognises(self):
        """The Tier 0 table is `| 1 | file | 171 | why |`; the counter must read it."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "reading_counts.py"), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_the_pairing_has_no_stale_count_left(self):
        """A row whose number is not the file's own line count fails here."""
        text = LIST.read_text()
        row = re.compile(r"^\| (?:[0-9]+ \| )?[`]([^`]+)[`] \| ([0-9,]+) \|")
        checked = 0
        for line in text.splitlines():
            match = row.match(line)
            if not match:
                continue
            path = ROOT / match.group(1)
            if not path.exists():
                continue
            actual = len(path.read_text().splitlines())
            self.assertEqual(actual, int(match.group(2).replace(",", "")), match.group(1))
            checked += 1
        self.assertGreater(checked, 5, "the list has almost no counts to check")


if __name__ == "__main__":
    unittest.main()
