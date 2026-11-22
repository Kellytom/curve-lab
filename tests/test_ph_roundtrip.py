# The drag→action map and the round trip through Inkscape's own files.
#
# The fixture `through-inkscape-c-0002.svg` is an Inkscape 1.4.4
# re-serialization of a recipe-carrying SVG that the extension wrote — the
# real file a user's Inkscape would hand back. The tests run against it so
# the snap is proven against Inkscape's own precision, not just against
# self-produced numbers (register row 55's lesson).
import json
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inkscape import ph_actions, ph_handles, ph_svg
from curve_lab.measure import to_fraction

FIXTURE = ROOT / "tests" / "fixtures" / "through-inkscape-c-0002.svg"
NS = "{http://www.w3.org/2000/svg}"


def rows_of(uid="c-0002"):
    registry = json.load(open(ROOT / "workbench" / "curve-registry.json"))
    record = next(r for r in registry["curves"] if r["uid"] == uid)
    return ([to_fraction(v) for v in record["speedX"]],
            [to_fraction(v) for v in record["speedY"]])


def node_at(svg, k):
    d = ET.parse(svg).getroot().find(NS + "path").get("d")
    return ph_handles.path_nodes(d)[k]


def set_node(svg, k, point):
    """Move one on-curve node in the path data — what a saved drag looks
    like, at Inkscape's six-place precision."""
    tree = ET.parse(svg)
    node = tree.getroot().find(NS + "path")
    tokens = node.get("d").replace(",", " ").split()
    index = []
    i = 0
    while i < len(tokens):
        if tokens[i] == "M":
            index.append((i + 1, i + 2)); i += 3
        elif tokens[i] == "C":
            index.append((i + 5, i + 6)); i += 7
        else:
            i += 1
    tokens[index[k][0]] = f"{float(point[0]):.6f}"
    tokens[index[k][1]] = f"{float(point[1]):.6f}"
    node.set("d", " ".join(tokens))
    tree.write(svg)


class FixtureTest(unittest.TestCase):
    """The file Inkscape itself re-serialized."""

    def test_the_recipe_survives_inkscape(self):
        uid, name, (rx, ry), placement = ph_svg.read_svg(FIXTURE)
        self.assertEqual(uid, "c-0002")
        self.assertEqual(name, "euler-hook")
        base = rows_of()
        self.assertEqual((rx, ry), base)

    def test_inkscape_precision_is_drift_not_drag(self):
        _, _, (rx, ry), placement = ph_svg.read_svg(FIXTURE)
        file_nodes = ph_handles.path_nodes(
            ET.parse(FIXTURE).getroot().find(NS + "path").get("d"))
        expected = ph_handles.nodes_of(rx, ry, placement, ph_svg.stations, 33)
        moved = ph_handles.moved_nodes(file_nodes, expected)
        self.assertEqual(moved, [],
                         "Inkscape's rounding must not read as a drag")
        worst = max(
            max(abs(fn[0] - en[0]), abs(fn[1] - en[1]))
            for fn, en in zip(file_nodes, expected)
        )
        self.assertLess(float(worst), 0.0001)

    def test_the_drawn_nodes_are_the_exact_stations(self):
        _, _, (rx, ry), placement = ph_svg.read_svg(FIXTURE)
        file_nodes = ph_handles.path_nodes(
            ET.parse(FIXTURE).getroot().find(NS + "path").get("d"))
        self.assertEqual(len(file_nodes), 33)
        # the drawn chain passes through the exact stations (drift ≤ text)
        expected = ph_handles.nodes_of(rx, ry, placement, ph_svg.stations, 33)
        for fn, en in zip(file_nodes, expected):
            self.assertLess(abs(fn[0] - en[0]), ph_handles.DRIFT)


class DragSnapTest(unittest.TestCase):
    """The drag→action map, against Inkscape's own file."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.svg = str(Path(self.tmp) / "dragtest.svg")
        shutil.copy(FIXTURE, self.svg)
        self.rx, self.ry = rows_of()
        self.placement = ph_actions.identity_placement()

    def test_a_translate_drag_snaps_and_rewrites_the_placement(self):
        p = node_at(self.svg, 8)
        set_node(self.svg, 8, (p[0] + Fraction(1, 10), p[1]))
        report = ph_handles.apply_snap(self.svg, self.rx, self.ry,
                                       self.placement, ph_svg.stations)
        self.assertEqual(report["action"], "translate +x")
        self.assertLess(float(report["miss"]), 0.001)
        self.assertTrue(report["rewritten"])
        _, _, (rx, ry), placement = ph_svg.read_svg(self.svg)
        self.assertEqual(placement["dx"], Fraction(1, 10))
        self.assertEqual((rx, ry), (self.rx, self.ry))  # rows untouched

    def test_an_end_handle_drag_snaps_to_the_end_edit(self):
        ex, ey = ph_actions.act_end_edit(self.rx, self.ry, Fraction(1), 0)
        target = ph_handles.nodes_of(ex, ey, self.placement,
                                     ph_svg.stations, 33)[32]
        set_node(self.svg, 32, target)
        report = ph_handles.apply_snap(self.svg, self.rx, self.ry,
                                       self.placement, ph_svg.stations)
        self.assertEqual(report["action"], "end-edit-u+")
        self.assertLess(float(report["miss"]), 0.000001)
        _, _, (rx, ry), _ = ph_svg.read_svg(self.svg)
        self.assertEqual(rx[5], Fraction(-1, 10))  # the acted top coefficient
        self.assertEqual((rx, ry), (ex, ey))

    def test_one_action_explains_two_dragged_nodes(self):
        p4, p12 = node_at(self.svg, 4), node_at(self.svg, 12)
        set_node(self.svg, 4, (p4[0] + Fraction(1, 10), p4[1]))
        set_node(self.svg, 12, (p12[0] + Fraction(1, 10), p12[1]))
        report = ph_handles.apply_snap(self.svg, self.rx, self.ry,
                                       self.placement, ph_svg.stations)
        self.assertEqual(report["action"], "translate +x")
        self.assertEqual(len(report["per_node"]), 2)

    def test_a_far_drag_is_refused_with_the_miss_in_units(self):
        set_node(self.svg, 4, (Fraction(50000), Fraction(-777)))
        report = ph_handles.apply_snap(self.svg, self.rx, self.ry,
                                       self.placement, ph_svg.stations,
                                       tolerance=Fraction(1))
        self.assertIsNone(report["action"])
        self.assertIn("refused", report["note"])
        self.assertIn("curve units", report["note"])


if __name__ == "__main__":
    unittest.main()
