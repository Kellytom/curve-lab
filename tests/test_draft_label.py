"""Every outward-facing page says "draft A".

The operator's rule: a page shown outside the working set is a draft, and says
so, until the work is finished. Generated pages are the risk: a rebuild can
drop the label silently, so this check runs in the suite.
"""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DraftLabelTest(unittest.TestCase):
    def test_every_outward_page_says_draft_a(self):
        result = subprocess.run(
            [sys.executable, "scripts/stamp_draft.py", "--check"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
