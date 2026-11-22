# Send a curve to Inkscape and read it back, exactly.
#
# The SVG is a view; the recipe is the truth. Every file this module writes
# carries a <metadata> block with the curve's identity, its speed rows and
# its placement as Fraction strings — so reading the file back reproduces
# the rows bit for bit, and the round trip is lossless by construction.
#
# The path data is the house drawing rule: exact stations joined by a cubic
# Bézier chain (curve_lab.bezier.fit_span), approximate between stations,
# and the file says so in its metadata note.

import json
import xml.etree.ElementTree as ET

from curve_lab.bezier import fit_span
from curve_lab.measure import curve_polynomials, to_fraction
from fractions import Fraction

from inkscape.ph_actions import identity_placement, position_of

NS = "http://www.w3.org/2000/svg"
META_TAG = f"{{{NS}}}metadata"


def stations(rows_x, rows_y, placement, count=33):
    """The exact stations, as Fractions — the drawing converts to float
    only at the path text, so a drag snaps against exact numbers."""
    px, py = position_of(rows_x, rows_y, placement)
    out = []
    for k in range(count):
        t = Fraction(k, count - 1)
        x = sum(c * t ** i for i, c in enumerate(px))
        y = sum(c * t ** i for i, c in enumerate(py))
        out.append((x, y))
    return out


def spans_from_stations(points, station_points):
    """Cubic spans through the stations, on the parabola rule."""
    spans = []
    for i in range(len(points) - 1):
        spans.append(fit_span(station_points[i], station_points[i + 1],
                              lambda s: points[i], lambda s: None))
    return spans


def path_d(rows_x, rows_y, placement, count=33):
    """The path data: cubic spans through the exact stations. The handles
    are the house Catmull-Rom rule (the exact central difference), written
    as plain decimals; the stations they ride on stay exact."""
    from inkscape.ph_handles import chain
    spans = chain(rows_x, rows_y, placement, stations, count)
    def f(v):
        return f"{float(v):.4f}"
    parts = [f"M {f(spans[0]['p0'][0])} {f(spans[0]['p0'][1])}"]
    for s in spans:
        parts.append(
            f"C {f(s['c1'][0])} {f(s['c1'][1])} {f(s['c2'][0])} {f(s['c2'][1])}"
            f" {f(s['p3'][0])} {f(s['p3'][1])}"
        )
    return " ".join(parts)


def metadata_block(uid, name, rows_x, rows_y, placement, ceiling=11):
    """The recipe, as the file carries it. Fractions as 'n/d' strings."""
    def cell(value):
        return f"{value.numerator}/{value.denominator}"

    payload = {
        "kind": "curve-lab-recipe",
        "uid": uid,
        "name": name,
        "speedX": [cell(v) for v in rows_x],
        "speedY": [cell(v) for v in rows_y],
        "placement": {k: cell(v) for k, v in placement.items()},
        "drawing": "cubic spans through exact stations; approximate between them",
    }
    return json.dumps(payload, indent=1)


def write_svg(path, uid, name, rows_x, rows_y, placement=None, ceiling=11):
    placement = placement or identity_placement()
    ET.register_namespace("", NS)
    root = ET.Element(f"{{{NS}}}svg",
                      {"width": "210mm", "height": "210mm", "version": "1.1"})
    meta = ET.SubElement(root, META_TAG)
    meta.text = metadata_block(uid, name, rows_x, rows_y, placement, ceiling)
    node = ET.SubElement(root, f"{{{NS}}}path",
                         {"id": "curve-lab-spine",
                          "style": "fill:none;stroke:#3b2d1c;stroke-width:1",
                          "d": path_d(rows_x, rows_y, placement)})
    tree = ET.ElementTree(root)
    ET.indent(tree)
    tree.write(path, xml_declaration=True, encoding="utf-8")
    return path


def read_svg(path):
    """Read the recipe back out. Returns (uid, name, rows, placement)."""
    root = ET.parse(path).getroot()
    meta = root.find(META_TAG)
    if meta is None or not meta.text:
        raise ValueError(f"{path} carries no curve-lab recipe metadata")
    payload = json.loads(meta.text)
    if payload.get("kind") != "curve-lab-recipe":
        raise ValueError(f"{path} metadata is not a curve-lab recipe")
    def read_cell(text):
        n, _, d = text.partition("/")
        return Fraction(int(n), int(d or 1))
    rows = (
        [read_cell(v) for v in payload["speedX"]],
        [read_cell(v) for v in payload["speedY"]],
    )
    placement = {k: read_cell(v) for k, v in payload["placement"].items()}
    return payload["uid"], payload["name"], rows, placement
