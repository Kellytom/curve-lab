"""Quintic sheet: draw a curve from the shared record into Inkscape.

The other half of the contract (`workbench/quintic.schema.json`,
`curve-lab.quintic/1`): the extension WRITES that format, this one READS it and
puts a curve on the canvas so it can be worked on with a trackball or a pencil.

    workbench/quintic-guides.json   ->  a curve, its six control points marked
                                        on every span, and the drawn chain

The record is y up (the house rule). The document is y down, so `to_svg` is the
ONE flip, and it happens here, at the point of drawing. Nothing else flips.

The drawn cubic chain is an approximation and says so in the element's own
attributes; the six points are carried as text so the record travels with the
drawing.
"""

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("CURVE_LAB_ROOT", HERE.parent)).resolve()
if not (ROOT / "curve_lab").is_dir():
    ROOT = Path.home() / "developer" / "curve-lab"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inkscape import quintic_math as qm  # noqa: E402

try:
    import inkex
except ImportError:  # importable outside Inkscape for linting
    inkex = None

MARK = "data-quintic-sheet"
DEFAULT_SHEET = str(ROOT / "workbench" / "quintic-guides.json")


def load_sheet(path):
    document = json.loads(Path(path).expanduser().read_text())
    if document.get("format") != "curve-lab.quintic/1":
        raise ValueError("%s is %s, not curve-lab.quintic/1"
                         % (path, document.get("format")))
    return document


def find_curve(document, uid):
    for curve in document.get("curves", []):
        if curve.get("uid") == uid:
            return curve
    known = [c.get("uid") for c in document.get("curves", [])][:8]
    raise ValueError("no curve %r in that file; it has %d curves, first: %s"
                     % (uid, len(document.get("curves", [])), ", ".join(known)))


def to_svg(points, scale, origin):
    """The ONE flip: the record is y up, the document is y down."""
    return [(origin[0] + p[0] * scale, origin[1] - p[1] * scale) for p in points]


class QuinticSheet(inkex.EffectExtension if inkex else object):
    """Place one curve of the shared record, with its six points marked."""

    def add_arguments(self, pars):
        pars.add_argument("--sheet", type=str, default=DEFAULT_SHEET)
        pars.add_argument("--uid", type=str, default="")
        pars.add_argument("--scale", type=float, default=2.0)
        pars.add_argument("--originx", type=float, default=60.0)
        pars.add_argument("--originy", type=float, default=60.0)
        pars.add_argument("--segments", type=int, default=0)
        pars.add_argument("--tolerance", type=float, default=0.01)
        pars.add_argument("--showcage", type=inkex.Boolean, default=True)
        pars.add_argument("--strokecolour", type=str, default="#000000")

    def effect(self):
        uid = (self.options.uid or "").strip()
        if not uid:
            inkex.errormsg("Quintic sheet: give the curve uid, e.g. q6-parabola-01")
            return
        try:
            document = load_sheet(self.options.sheet)
            curve = find_curve(document, uid)
        except (OSError, ValueError) as exc:
            inkex.errormsg("Quintic sheet: %s" % exc)
            return

        origin = (self.options.originx, self.options.originy)
        scale = float(self.options.scale) or 1.0
        colour = self.options.strokecolour or "#000000"
        layer = self.svg.get_current_layer()

        drawn = []
        points_all = []
        worst = 0.0
        for index, span in enumerate(curve.get("spans", [])):
            control_y_up = [tuple(p) for p in span["points"]]
            control = to_svg(control_y_up, scale, origin)
            points_all.append(control)
            if self.options.segments <= 0:
                chain, miss, used = qm.fit_to_tolerance(control, self.options.tolerance)
            else:
                used = int(self.options.segments)
                chain = qm.cubic_chain(control, used)
                miss = qm.measure_max_error(control, chain)
            worst = max(worst, miss)
            path = inkex.elements.PathElement()
            path.set("d", qm.chain_to_d(chain))
            path.set(MARK, "%s:%d" % (uid, index))
            path.set("data-quintic-points", " ".join(
                "%s,%s" % (qm.num(p[0]), qm.num(p[1])) for p in control))
            path.set("data-format", "curve-lab.quintic/1")
            path.style = {"fill": "none", "stroke": colour,
                          "stroke-width": "1.2", "stroke-linecap": "round"}
            layer.append(path)
            drawn.append("span %d: %d cubics, %.4f px" % (index, used, miss))

        marks = inkex.elements.Group()
        marks.set(MARK + "-marks", uid)
        for control in points_all:
            if self.options.showcage:
                line = inkex.elements.Polyline()
                line.set("points", " ".join("%s,%s" % (qm.num(p[0]), qm.num(p[1]))
                                            for p in control))
                line.style = {"fill": "none", "stroke": "#b9c6d6",
                              "stroke-width": "0.8", "stroke-dasharray": "3 3"}
                marks.append(line)
            for x, y in control:
                dot = inkex.elements.Circle()
                dot.set("cx", qm.num(x))
                dot.set("cy", qm.num(y))
                dot.set("r", "3")
                dot.style = {"fill": "#c0392b", "stroke": "none"}
                marks.append(dot)
        layer.append(marks)

        inkex.errormsg("Quintic sheet: %s, %d span%s drawn at scale %g; %s; "
                       "worst chain miss %.4f px. The six points are the record, "
                       "the drawn path is the view."
                       % (uid, len(points_all), "" if len(points_all) == 1 else "s",
                          scale, "; ".join(drawn), worst))


if __name__ == "__main__":
    QuinticSheet().run()
