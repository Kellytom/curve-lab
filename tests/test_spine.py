"""The promotion gate, step 1: a spine chain becomes a Piece/Trace.

A real chain from `pythagorean-spiral/` is fitted into the engine, and the
anchors it was built from are checked explicitly: every span endpoint is a
chain node, every fitted join lands on that node, and the fitted end is the
chain's own final point.
"""

import math
import re
import unittest

from clothoid_lab import engine, spine, svg
from clothoid_lab.clearance import piece_clearance
from clothoid_lab.contact import Contact
from clothoid_lab.piece import Piece, build_piece, render_piece


def span_tangents(span):
    p0, c1, c2, p3 = span["p0"], span["c1"], span["c2"], span["p3"]
    t0 = math.atan2(c1[1] - p0[1], c1[0] - p0[0])
    t1 = math.atan2(p3[1] - c2[1], p3[0] - c2[0])
    return t0, t1


class TestChainImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = spine.load()
        cls.chain = cls.package.design.lobe(
            cls.package.thinnest(3125), steps=7)
        cls.spans = spine.chain_spans(cls.chain)

    def test_anchors_are_the_chain_nodes(self):
        anchors = spine.anchors(self.chain)
        self.assertEqual(len(anchors), len(self.chain.turns) + 1)
        points = {(x, y) for x, y, _ in anchors}
        for index, span in enumerate(self.spans):
            self.assertIn(tuple(float(v) for v in span["p0"]), points,
                          f"span {index} starts off the anchors")
            self.assertIn(tuple(float(v) for v in span["p3"]), points,
                          f"span {index} ends off the anchors")

    def test_one_segment_per_span(self):
        design = spine.design_from_chain(self.chain)
        self.assertEqual(len(design.segments), len(self.spans))
        self.assertTrue(design.g1)

    def test_every_join_lands_on_its_anchor(self):
        design = spine.design_from_chain(self.chain)
        chain = engine.build(design)
        self.assertEqual((design.anchor["x"], design.anchor["y"]),
                         (self.chain.floats()[0]))
        s = 0.0
        for index, segment in enumerate(design.segments):
            x, y = chain.point(s)
            anchor = self.spans[index]["p0"]
            self.assertAlmostEqual(x, anchor[0], delta=1e-9,
                                   msg=f"anchor {index} x")
            self.assertAlmostEqual(y, anchor[1], delta=1e-9,
                                   msg=f"anchor {index} y")
            s += segment.length
        end = chain.point(chain.length)
        final = self.chain.floats()[-1]
        self.assertAlmostEqual(end[0], final[0], delta=1e-9)
        self.assertAlmostEqual(end[1], final[1], delta=1e-9)

    def test_the_apsis_corner_is_carried_not_flattened(self):
        design = spine.design_from_chain(self.chain)
        self.assertGreater(len(design.segments), 1)
        self.assertEqual(design.segments[0].corner, 0.0)
        turn = design.segments[1].corner
        _, previous_t1 = span_tangents(self.spans[0])
        t0, _ = span_tangents(self.spans[1])
        expected = math.atan2(math.sin(t0 - previous_t1),
                              math.cos(t0 - previous_t1))
        self.assertAlmostEqual(turn, expected, delta=1e-9)
        self.assertGreater(abs(turn), math.radians(1.0),
                           "the lobe's apsis keeps a real tangent jump")

    def test_a_cusp_is_refused_not_rounded(self):
        package = self.package
        path = package.Spiral(package.thinnest(3125), length=1.0)
        path.walk(0).cusp(1).walk(0)
        with self.assertRaisesRegex(ValueError, "cusp"):
            spine.chain_spans(path)

    def test_trace_and_piece_carry_the_chain(self):
        piece = spine.piece_from_chain(
            self.chain, name="lobe", width=1.0, terminals=("butt", "round"))
        self.assertEqual(len(piece.traces), 1)
        trace = piece.traces[0]
        self.assertEqual(trace.name, "lobe")
        self.assertEqual(trace.width, 1.0)
        self.assertEqual(trace.terminals, ("butt", "round"))
        groups, info = build_piece(piece)
        self.assertTrue(info["fit_ok"])
        self.assertTrue(any(group.role == "rail" for group in groups))
        again = type(piece).from_dict(piece.to_dict())
        self.assertEqual(again.to_dict(), piece.to_dict())

    def test_mirror_follows_the_piece(self):
        piece = spine.piece_from_chain(self.chain, name="lobe", mirror=True)
        groups, info = build_piece(piece)
        self.assertTrue(info["mirror"])
        self.assertTrue(any(group.instance.endswith("mirrored")
                            for group in groups))


class TestSheetAndJoin(unittest.TestCase):
    """Gate 2 and gate 3: the sheet, and a declared contact at a real join."""

    @classmethod
    def setUpClass(cls):
        cls.package = spine.load()
        cls.trunk = cls.package.design.curl(peak=200, chord=6)
        anchor, cls.branch = cls.package.design.fork(
            cls.trunk, 47, steps=5, length=0.6, turn=0)
        cls.package.design.joined(cls.trunk, cls.branch, 47)
        cls.point = (float(anchor[0][0]), float(anchor[0][1]))

    def piece(self, contact=True):
        return Piece(
            name="spine sheet",
            stroke=0.5,
            contacts=([Contact(self.point, 2.0, "ink/trunk", "ink/branch")]
                      if contact else []),
            traces=[
                spine.trace_from_chain(self.trunk, "trunk", width=3.0),
                spine.trace_from_chain(self.branch, "branch", width=1.5),
            ],
        )

    def test_page_is_200_by_250_and_y_up(self):
        text, info = render_piece(self.piece(), frame=(200.0, 250.0), margin=12)
        self.assertTrue(info["fit_ok"])
        self.assertIn('width="200mm"', text)
        self.assertIn('height="250mm"', text)
        self.assertIn('viewBox="0 0 200 250"', text)
        # The design is +y up; the writer flips once. The trunk starts at y = 0,
        # the bottom of the drawing, so the first path point is low on the page.
        match = re.search(r'<path id="[^"]*" d="([^"]*)"', text)
        self.assertIsNotNone(match)
        command, values = svg.parse_d(match.group(1))[0]
        self.assertEqual(command, "M")
        self.assertGreater(values[1], 125.0,
                           "y = 0 should map to the lower half after the flip")

    def test_declared_contact_passes(self):
        report = piece_clearance(self.piece())
        self.assertTrue(report["ok"], report["violations"])
        self.assertEqual(len(report["merged"]), 1)
        self.assertLess(report["min"]["distance"], report["clearance"])
        self.assertFalse(report["crossings"])

    def test_the_same_gap_fails_without_the_contact(self):
        report = piece_clearance(self.piece(contact=False))
        self.assertFalse(report["ok"])
        self.assertTrue(report["violations"])
        self.assertFalse(report["merged"])


if __name__ == "__main__":
    unittest.main()
