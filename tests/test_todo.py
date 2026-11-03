import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import todo


class TodoTwinTest(unittest.TestCase):
    def test_twin_matches_source(self):
        source = (ROOT / "TODO.md").read_text(encoding="utf-8")
        blocks = todo.parse(source.splitlines())
        tasks = [b for b in blocks if b[0] == "task"]
        page = (ROOT / "workbench" / "todo.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('type="checkbox"'), len(tasks))
        self.assertEqual(page.count('type="checkbox" checked'), sum(1 for _, (done, _) in tasks if done))
        self.assertIn("Curve grades", page)
        self.assertIn("Levien", page)
        self.assertIn("Grade A", page)

    def test_progress_is_reported(self):
        blocks = todo.parse((ROOT / "TODO.md").read_text(encoding="utf-8").splitlines())
        done, total, pct, _ = todo.render(blocks)
        self.assertGreater(done, 0)
        self.assertGreater(total, done)
        self.assertAlmostEqual(pct, 100.0 * done / total, places=6)


if __name__ == "__main__":
    unittest.main()
