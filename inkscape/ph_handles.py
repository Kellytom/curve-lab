# The drawn chain, exactly — and the drag→action map.
#
# The path Inkscape shows is a cubic Bézier chain through the exact
# stations, Catmull-Rom: the tangent at station k is the exact central
# difference (p_{k+1} − p_{k−1})/2, the end stations use one-sided
# differences. Every node and handle is an exact Fraction, and the rule is
# deterministic — the same recipe always draws the same handles, which is
# what makes a drag snap back to the same spot.
#
# The drag→action map: the user drags on-curve nodes in Inkscape, saves,
# and the receiver reads the drawn node positions from the path data. For
# each permitted action in the closed vocabulary, the map re-draws the
# chain and compares node positions. One action must explain ALL the moved
# nodes — the vocabulary applies to the curve, not to single nodes. The
# winner is the action with the smallest total miss; a refusal states the
# miss in curve units, never a percentage.

from fractions import Fraction

Frac = Fraction


# ── the exact chain ─────────────────────────────────────────────────────────

def chain(rows_x, rows_y, placement, stations_fn, count=33):
    """The drawn chain: nodes and handle pairs, exact.

    stations_fn(rows_x, rows_y, placement, count) supplies the exact
    stations (ph_svg.stations). Node k is station k; the tangent at node k
    is the central difference of its neighbours, halves and all exact."""
    pts = stations_fn(rows_x, rows_y, placement, count)

    def tangent(k):
        if k == 0:
            return (pts[1][0] - pts[0][0], pts[1][1] - pts[0][1])
        if k == len(pts) - 1:
            return (pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1])
        return ((pts[k + 1][0] - pts[k - 1][0]) / 2,
                (pts[k + 1][1] - pts[k - 1][1]) / 2)

    nodes = [((Frac(p[0]), Frac(p[1])) if not isinstance(p[0], Frac) else p)
             for p in pts]
    out = []
    for k in range(len(nodes) - 1):
        m0 = tangent(k)
        m1 = tangent(k + 1)
        p0, p3 = nodes[k], nodes[k + 1]
        c1 = (p0[0] + m0[0] / 3, p0[1] + m0[1] / 3)
        c2 = (p3[0] - m1[0] / 3, p3[1] - m1[1] / 3)
        out.append({"p0": p0, "c1": c1, "c2": c2, "p3": p3})
    return out


def nodes_of(rows_x, rows_y, placement, stations_fn, count=33):
    """The on-curve nodes, exact — what a drag is measured against."""
    return [s for s in stations_fn(rows_x, rows_y, placement, count)]


# ── reading the drag from the file ──────────────────────────────────────────

def path_nodes(d_attribute):
    """The on-curve node positions from a path 'd', in file order.

    Inkscape may rewrite the numbers in its own precision; a node is read
    through the decimal text (six places, the pages' precision)."""
    from curve_lab.measure import to_fraction
    tokens = d_attribute.replace(",", " ").split()
    nodes = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("M", "L"):
            nodes.append((to_fraction(tokens[i + 1]), to_fraction(tokens[i + 2])))
            i += 3
        elif t == "C":
            # the node is the segment's endpoint: the last two numbers
            nodes.append((to_fraction(tokens[i + 5]), to_fraction(tokens[i + 6])))
            i += 7
        else:
            i += 1
    return nodes


# The drawing's text precision: Inkscape rewrites path data with its own
# rounding (measured 5e-05 curve units on 1.4.4). A shift below DRIFT is
# the file's rounding, not a drag; a legal action moves nodes by the
# curve's grid unit or more.
DRIFT = Frac(1, 1000)


def moved_nodes(file_nodes, expected_nodes):
    """Which nodes moved, and by how much — the pairs (index, file point)
    whose distance from the recipe's own nodes exceeds the drawing's
    rounding drift."""
    moved = []
    for k, (fx, fy) in enumerate(file_nodes):
        if k >= len(expected_nodes):
            break
        ex, ey = expected_nodes[k]
        dx, dy = fx - ex, fy - ey
        if abs(dx) > DRIFT or abs(dy) > DRIFT:
            moved.append({"index": k, "from": (ex, ey),
                          "dragged": (fx, fy),
                          "shift": (dx, dy)})
    return moved


# ── the snap ────────────────────────────────────────────────────────────────

def _acted_rows(rows_x, rows_y, action, registry=None):
    """The rows an action produces. Rigid motions act on the placement, not
    the rows — handled by the caller; this covers the row-level actions."""
    if action == "end-edit-u+":
        return ph_act_end(rows_x, rows_y, 1, 0)
    if action == "end-edit-u-":
        return ph_act_end(rows_x, rows_y, -1, 0)
    if action == "end-edit-v+":
        return ph_act_end(rows_x, rows_y, 0, 1)
    if action == "end-edit-v-":
        return ph_act_end(rows_x, rows_y, 0, -1)
    if action.startswith("recipe "):
        from curve_lab.measure import to_fraction
        uid = action[len("recipe "):]
        for record in registry["curves"]:
            if record["uid"] == uid:
                return ([to_fraction(v) for v in record["speedX"]],
                        [to_fraction(v) for v in record["speedY"]])
        raise KeyError(uid)
    return rows_x, rows_y


def ph_act_end(rows_x, rows_y, du, dv):
    from inkscape.ph_actions import act_end_edit
    return act_end_edit(rows_x, rows_y, du, dv)


def _acted_placement(placement, action, unit):
    """The placement a rigid-motion action produces, at the curve's unit."""
    from inkscape.ph_actions import (act_translate, act_mirror_x)
    if action == "translate +x":
        return act_translate(placement, unit, 0)
    if action == "translate -x":
        return act_translate(placement, -unit, 0)
    if action == "translate +y":
        return act_translate(placement, 0, unit)
    if action == "translate -y":
        return act_translate(placement, 0, -unit)
    if action == "mirror":
        return act_mirror_x(placement)
    return placement


def candidate_actions(rows_x, rows_y, placement, registry=None, ceiling=11):
    """The closed vocabulary, as (name, rows, placement) triples. The
    degree gate runs here: an action whose acted rows pass the ceiling is
    offered; one that does not is not."""
    from inkscape.ph_actions import (act_rotate_p_triple, act_scale_square,
                                     degree_gate)
    out = [("stay", rows_x, rows_y, placement)]
    for name in ("end-edit-u+", "end-edit-u-", "end-edit-v+", "end-edit-v-"):
        rx, ry = _acted_rows(rows_x, rows_y, name)
        ok, _ = degree_gate(rx, ry, ceiling)
        if ok:
            out.append((name, rx, ry, placement))
    for name in ("translate +x", "translate -x", "translate +y",
                 "translate -y", "mirror"):
        out.append((name, rows_x, rows_y,
                    _acted_placement(placement, name, _unit(rows_x, rows_y))))
    # one p-triple turn and its inverse, the (3,4,5) half angle
    for name, a, b in (("rotate (3,4,5)", Fraction(3, 5), Fraction(4, 5)),
                       ("rotate (3,-4,5)", Fraction(3, 5), Fraction(-4, 5)),
                       ("rotate (4,3,5)", Fraction(4, 5), Fraction(3, 5)),
                       ("rotate (4,-3,5)", Fraction(4, 5), Fraction(-3, 5))):
        out.append((name, rows_x, rows_y,
                    act_rotate_p_triple(placement, a, b)))
    for q, name in ((Fraction(2), "scale ×2"), (Fraction(1, 2), "scale ×½")):
        out.append((name, rows_x, rows_y, act_scale_square(placement, q)))
    if registry:
        for record in registry["curves"]:
            if not record.get("speedX"):
                continue
            name = f"recipe {record['uid']}"
            try:
                rx, ry = _acted_rows(rows_x, rows_y, name, registry)
            except KeyError:
                continue
            ok, _ = degree_gate(rx, ry, ceiling)
            if ok:
                out.append((name, rx, ry, placement))
    return out


def _unit(rows_x, rows_y):
    """The curve's coarse unit: one over the lcm of the rows' denominators."""
    from math import gcd

    def lcm(a, b):
        return a * b // gcd(a, b)

    denom = 1
    for row in (rows_x, rows_y):
        for c in row:
            if c:
                denom = lcm(denom, c.denominator)
    return Frac(1, denom)


def snap_drag(rows_x, rows_y, placement, dragged_nodes, stations_fn,
              registry=None, ceiling=11, count=33, tolerance=None):
    """Match a drag against the closed vocabulary.

    dragged_nodes: [(index, point)] — the nodes the user moved, file order.
    Every candidate action re-draws the chain; its miss is the total, over
    the dragged nodes, of the Manhattan distance from the drawn node to the
    dropped point. The winner explains all the drags with one action.

    tolerance: the largest total miss (curve units) that is still a snap;
    beyond it the answer is a refusal. None means never refuse.

    Returns (action, miss, per_node) with action None on a refusal."""
    best = (None, None, None)
    for name, rx, ry, pl in candidate_actions(rows_x, rows_y, placement,
                                              registry, ceiling):
        drawn = nodes_of(rx, ry, pl, stations_fn, count)
        total = Frac(0)
        per_node = []
        for index, point in dragged_nodes:
            if index >= len(drawn):
                total = None
                break
            ex, ey = drawn[index]
            dx = abs(Frac(point[0]) - Frac(ex))
            dy = abs(Frac(point[1]) - Frac(ey))
            total = total + dx + dy
            per_node.append((index, dx + dy))
        if total is None:
            continue
        if best[1] is None or total < best[1]:
            best = (name, total, per_node)
    if tolerance is not None and best[1] is not None and best[1] > Frac(tolerance):
        return (None, best[1], best[2])
    return best


def apply_snap(svg_path, rows_x, rows_y, placement, stations_fn,
               registry=None, ceiling=11, count=33, write=True,
               tolerance=None):
    """Read the dragged nodes from a saved SVG, snap them, and — when the
    winner is not 'stay' — rewrite the file with the acted recipe.

    tolerance: the largest total miss (curve units) accepted as a snap;
    None never refuses. Returns a report dict: the action, the miss in
    units, the per-node misses, and whether the file was rewritten."""
    import xml.etree.ElementTree as ET
    NS = "http://www.w3.org/2000/svg"
    root = ET.parse(svg_path).getroot()
    node = root.find(f"{{{NS}}}path")
    if node is None:
        raise ValueError(f"{svg_path} carries no path")
    file_nodes = path_nodes(node.get("d"))
    expected = nodes_of(rows_x, rows_y, placement, stations_fn, count)
    dragged = moved_nodes(file_nodes, expected)
    if not dragged:
        return {"action": "stay", "miss": Frac(0), "per_node": [],
                "rewritten": False,
                "note": "every node sits where the recipe drew it"}
    drags = [(m["index"], m["dragged"]) for m in dragged]
    action, miss, per_node = snap_drag(rows_x, rows_y, placement, drags,
                                       stations_fn, registry, ceiling, count,
                                       tolerance)
    report = {"action": action, "miss": miss, "per_node": per_node,
              "rewritten": False}
    if action in (None, "stay"):
        report["note"] = ("no legal action explains the drag; refused with "
                          f"a miss of {float(miss):.4f} curve units"
                          if action is None else
                          "the drag matches the recipe as drawn")
        return report
    # apply: the acted rows and placement replace the file's recipe
    for name, rx, ry, pl in candidate_actions(rows_x, rows_y, placement,
                                              registry, ceiling):
        if name == action:
            from inkscape import ph_svg
            ph_svg.write_svg(svg_path, _uid_of(svg_path), _name_of(svg_path),
                             rx, ry, pl)
            report["rewritten"] = True
            break
    return report


def _uid_of(svg_path):
    from inkscape.ph_svg import read_svg
    return read_svg(svg_path)[0]


def _name_of(svg_path):
    from inkscape.ph_svg import read_svg
    return read_svg(svg_path)[1]
