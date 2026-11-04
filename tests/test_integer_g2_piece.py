import unittest
from pathlib import Path

from curve_lab import pyth_g2
from curve_lab.clearance import piece_clearance
from curve_lab.contact import Contact
from curve_lab.piece import Piece, Trace, build_piece

ROOT = Path(__file__).resolve().parents[1]


class IntegerG2PieceTest(unittest.TestCase):
    def piece(self):
        pair = pyth_g2.asymmetric_pair()

        def span(points):
            return {"p0": points[0], "c1": points[1],
                    "c2": points[2], "p3": points[3]}

        return Piece(
            "integer G2 pair",
            [
                Trace("A", spans=[span(pair["a_points"])]),
                Trace("B", spans=[span(pair["b_points"])]),
            ],
            contacts=[Contact((50, 0), radius=2.0,
                              a="ink/A", b="ink/B")],
        )

    def test_span_trace_builds_and_measures(self):
        piece = self.piece()
        groups, info = build_piece(piece)
        self.assertTrue(info["fit_ok"])
        self.assertEqual(len(groups), 2)
        self.assertTrue(all(g.role == "spine" for g in groups))
        result = piece_clearance(
            piece, clearance=5.0, tol=0.02, roles=("spine",))
        self.assertTrue(result["ok"])
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(len(result["crossings"]), 1)
        self.assertTrue(result["crossings"][0]["allowed"])
        json_text = piece.to_json()
        self.assertIn('"spans"', json_text)

    def test_page(self):
        page = (ROOT / "workbench" / "integer-g2-piece.html").read_text(
            encoding="utf-8")
        self.assertIn("Fig. G4", page)
        self.assertIn("Piece report", page)
        self.assertIn("clearance ok", page)
        self.assertIn("trace", page)
        self.assertIn("A0 (0,0)", page)


if __name__ == "__main__":
    unittest.main()
