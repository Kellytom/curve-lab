"""Sequence curves: factorial/triangular lengths and the symmetric closure.

The tests check the two claims: every right-angle vertex is an integer, and
the schedule 1..n,-n..-1 returns to the origin exactly.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sequence_curves as S  # noqa: E402

PAGE = ROOT / "workbench" / "sequence-curves.html"


class TestSequenceCurves(unittest.TestCase):
    def test_factorial_and_triangular_lengths(self):
        self.assertEqual(S.FACT, [24, 6, 2, 1])
        self.assertEqual(S.TRI, [10, 6, 3, 1])

    def test_every_vertex_is_integer(self):
        for panel in S.PANELS:
            for x, y in panel["pts"] + (panel["back"] or []):
                with self.subTest(panel=panel["key"], point=(x, y)):
                    self.assertEqual(float(x), int(x))
                    self.assertEqual(float(y), int(y))

    def test_the_symmetric_schedule_returns_to_the_origin(self):
        for n in range(3, 11):
            out, back = S.symmetric(list(range(1, n + 1)))
            with self.subTest(n=n):
                self.assertEqual(back[-1], (0, 0))
                self.assertEqual(out[0], (0, 0))
                self.assertEqual(len(out), n + 1)
                self.assertEqual(len(back), n + 1)

    def test_the_signed_schedule_has_the_expected_signs(self):
        self.assertEqual(S.signed([1, 2, 3]), [1, 2, 3, -3, -2, -1])

    def test_the_factorial_closure(self):
        out, back = S.symmetric(S.FACT)
        self.assertEqual(back[-1], (0, 0))

    def test_the_page_has_five_figures(self):
        page = PAGE.read_text(encoding="utf-8")
        for key in ("S1", "S2", "S3", "S4", "S5"):
            self.assertIn(f"Fig. {key}", page)
        self.assertIn("returns to the origin", page)
        self.assertIn("24, 6, 2, 1", page)
        self.assertIn("T₄", page)


if __name__ == "__main__":
    unittest.main()
