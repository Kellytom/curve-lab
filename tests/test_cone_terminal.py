"""The two-arc cone terminal: R = 2 x half width, tangent at the base, a point at the tip.

Two things here are called a cone. The `cone` terminal kind is a **width law** —
the ribbon narrows on `w = ½(1−(1−t)³)`. This is a **construction**: one 60° arc
from each rail end, each of radius `2 × half`, meeting at a point on the
centreline. The names must not be mixed, so this file tests the construction by
its own geometry, not by the width-law spans.
"""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.terminals import cone_terminal, terminal_spans  # noqa: E402


def rails(half: float, length: float = 5.0):
    """Two straight rails running up the y axis and ending at y = 0."""
    def ribbon(x):
        return {"spans": [{
            "p0": (x, -length), "c1": (x, -length * 0.6),
            "c2": (x, -length * 0.4), "p3": (x, 0.0), "t": (0.0, 1.0),
        }]}

    return ribbon(+half), ribbon(-half)


def angle_between(a, b):
    cosine = (a[0] * b[0] + a[1] * b[1]) / (math.hypot(*a) * math.hypot(*b))
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


class TestConeTerminal(unittest.TestCase):
    def test_the_radius_is_twice_the_half_width(self):
        """goals.md: the cone terminal radius is 2 x the offset, at every offset."""
        for half in (0.5, 1.5, 3.0):
            with self.subTest(half=half):
                pos, neg = rails(half)
                cone = cone_terminal(pos, neg)
                self.assertAlmostEqual(2.0 * half, cone["radius"], places=12)
                self.assertAlmostEqual(2.0 * half, cone["half"] * 2, places=12)

    def test_the_arc_is_tangent_to_its_rail(self):
        """The control point leaves along the rail's own direction, so the join is smooth."""
        pos, neg = rails(1.0)
        cone = cone_terminal(pos, neg)
        first = cone["spans"][0]
        leave = (first["c1"][0] - first["p0"][0], first["c1"][1] - first["p0"][1])
        self.assertLess(angle_between(leave, (0.0, 1.0)), 1e-9)
        # The cap comes back down to the - rail, so it arrives against the rail's
        # travel direction: 180 degrees is smooth here, not a kink.
        last = cone["spans"][1]
        arrive = (last["p3"][0] - last["c2"][0], last["p3"][1] - last["c2"][1])
        self.assertAlmostEqual(180.0, angle_between(arrive, (0.0, 1.0)), places=6)

    def test_the_two_arcs_meet_at_the_tip(self):
        """One stroke: the first arc ends where the second begins, at √3 x half out."""
        pos, neg = rails(1.0)
        cone = cone_terminal(pos, neg)
        self.assertEqual(cone["spans"][0]["p3"], cone["spans"][1]["p0"])
        self.assertAlmostEqual(0.0, cone["tip"][0], places=12)
        self.assertAlmostEqual(math.sqrt(3.0), cone["tip"][1], places=12)

    def test_each_arc_is_centred_on_the_other_rail_end(self):
        """The construction, stated as a number a reader can check on the page."""
        pos, neg = rails(2.0)
        cone = cone_terminal(pos, neg)
        self.assertEqual((2.0, 0.0), cone["centres"]["neg"])
        self.assertEqual((-2.0, 0.0), cone["centres"]["pos"])
        for centre in cone["centres"].values():
            self.assertAlmostEqual(4.0, math.dist(centre, cone["tip"]), places=12)

    def test_a_bare_tip_is_rejected(self):
        """No terminal means the rails stop open; the gap is the full width, not a point."""
        pos, neg = rails(1.5)
        self.assertEqual([], terminal_spans(pos, neg, "butt"))
        gap = math.dist(pos["spans"][-1]["p3"], neg["spans"][-1]["p3"])
        self.assertAlmostEqual(3.0, gap, places=12)
        self.assertLess(gap, 3.0 + 1e-9, "a bare end is an open width, not a closed point")

    def test_a_ribbon_with_no_width_is_refused(self):
        pos, neg = rails(1.0)
        neg["spans"][0]["p0"] = pos["spans"][0]["p0"]
        neg["spans"][0]["c1"] = pos["spans"][0]["c1"]
        neg["spans"][0]["c2"] = pos["spans"][0]["c2"]
        neg["spans"][0]["p3"] = pos["spans"][0]["p3"]
        with self.assertRaises(ValueError):
            cone_terminal(pos, neg)


if __name__ == "__main__":
    unittest.main()


class TestSymmetricConeTerminal(unittest.TestCase):
    """The operator's "it is slightly offset", 2026-11-17.

    On a curved spine one rail is a little longer than the other, so the two rail
    ends do not sit square to the stroke. The cap then reads lopsided even though
    it is symmetric about its own axis. Symmetric mode puts it on the centreline.
    """

    def skewed_rails(self):
        """A pair whose ends disagree by 0.3 along the stroke: the usual lean."""
        pos = {"spans": [{"p0": (1, -5), "c1": (1, -2), "c2": (1, -1),
                          "p3": (1, 0.0), "t": (0, 1)}]}
        neg = {"spans": [{"p0": (-1, -5), "c1": (-1, -2), "c2": (-1, -1),
                          "p3": (-1, 0.3), "t": (0, 1)}]}
        return pos, neg

    def test_the_tip_lands_exactly_on_the_given_centreline(self):
        pos, neg = self.skewed_rails()
        cone = cone_terminal(pos, neg, symmetric=True, centre=(0, 0), tangent=(0, 1))
        self.assertAlmostEqual(0.0, cone["tip"][0], places=12)
        self.assertAlmostEqual(math.sqrt(3.0), cone["tip"][1], places=12)

    def test_the_rail_ends_become_an_exact_mirror_pair(self):
        pos, neg = self.skewed_rails()
        cone = cone_terminal(pos, neg, symmetric=True, centre=(0, 0), tangent=(0, 1))
        first, last = cone["spans"][0], cone["spans"][1]
        self.assertAlmostEqual(cone["half"], math.dist((0.0, 0.0), first["p0"]), places=12)
        self.assertAlmostEqual(cone["half"], math.dist((0.0, 0.0), last["p3"]), places=12)
        self.assertEqual(0.0, cone["shift"]["pos"], "the + end was already square")
        self.assertGreater(cone["shift"]["neg"], 0.29)

    def test_the_two_arcs_are_mirror_images_about_the_axis(self):
        pos, neg = self.skewed_rails()
        cone = cone_terminal(pos, neg, symmetric=True, centre=(0, 0), tangent=(0, 1))
        first, last = cone["spans"][0], cone["spans"][1]

        def mirror(point):
            """Reflect about the y axis through the centre (the axis is (0, 1))."""
            return (-point[0], point[1])

        self.assertAlmostEqual(mirror(last["p3"])[0], first["p0"][0], places=12)
        self.assertAlmostEqual(mirror(last["c2"])[0], first["c1"][0], places=9)
        self.assertAlmostEqual(mirror(last["c2"])[1], first["c1"][1], places=9)
        self.assertAlmostEqual(mirror(last["p3"])[1], first["p0"][1], places=12)

    def test_without_a_tangent_the_axis_is_squared_and_the_lean_is_reported(self):
        pos, neg = self.skewed_rails()
        cone = cone_terminal(pos, neg, symmetric=True, centre=(0, 0))
        self.assertGreater(cone["axis_twist"], 1.0, "a leaned pair must report its lean")
        self.assertAlmostEqual(cone["radius"], 2 * cone["half"], places=12)

    def test_the_default_mode_still_leaves_the_rails_where_they_are(self):
        """The feature is additive: a caller that does not ask keeps today's cap."""
        pos, neg = self.skewed_rails()
        cone = cone_terminal(pos, neg)
        self.assertEqual(0.0, cone["shift"]["pos"])
        self.assertEqual(0.0, cone["shift"]["neg"])
        self.assertEqual(0.0, cone["axis_twist"])
        self.assertAlmostEqual(0.0, cone["tip"][0], places=3)
        self.assertGreater(cone["tip"][1], math.sqrt(3.0))
