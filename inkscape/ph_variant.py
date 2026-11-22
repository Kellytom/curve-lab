# The acted recipe becomes a registry-variant record.
#
# The round trip's last leg: after the receive snaps a drag and the file
# carries the acted recipe, the curve can enter the registry as a variant —
# a PROPOSAL payload, never written directly (the save endpoint owns the
# registry; this module builds the record and states its exactness).
#
# The rule (2026-11-21): a TRANSLATION is a view, not a curve — moving a
# curve on the page does not make a new curve, so a translated placement is
# refused as a variant. Rotation, scale, mirror and end-edits change what
# the curve IS; their placement bakes into the speed rows exactly:
#   rows' = (a + ib)·q·rows  (then conjugated when mirrored),
# and the baked rows' integral is the drawn curve minus its offset.
#
# A recipe swap is its own curve — the sibling is already in the registry,
# so a swapped file maps back to the sibling's uid, not a new variant.

import json
from fractions import Fraction

from curve_lab.measure import bend, grid
from inkscape.ph_actions import (act_translate, degree_of, identity_placement,
                                 place_rows)


def _row_cell(value):
    """A coefficient as the registry stores it: a plain decimal when the
    fraction round-trips through six places (the pages' precision), the
    exact 'n/d' text when it does not."""
    decimal = float(value)
    text = f"{decimal:.6f}"
    if Fraction(text) == value:
        return decimal if Fraction(text) == value else text
    # a clean decimal like -0.1 prints as '-0.100000'; give the short form
    short = f"{decimal:.10f}".rstrip("0").rstrip(".")
    return float(short) if Fraction(f"{decimal:.6f}") == value else f"{value.numerator}/{value.denominator}"


def _next_uid(registry, parent_uid):
    """The variant uid: the parent's uid with the next free letter."""
    taken = {r["uid"] for r in registry["curves"]}
    for letter in "abcdefghijklmnopqrstuvwxyz":
        candidate = f"{parent_uid}{letter}"
        if candidate not in taken:
            return candidate
    raise ValueError(f"no free variant uid under {parent_uid}")


def _descriptor(rows_x, rows_y, placement, parent_rows_x, parent_rows_y):
    """What changed, in one word — the name's honest suffix."""
    if (rows_x, rows_y) != (parent_rows_x, parent_rows_y):
        return "end-edited"
    if placement["m"] == -1:
        return "mirrored"
    if placement["a"] != 1 or placement["b"] != 0:
        if placement["a"] in (0, 1, -1) and placement["b"] in (0, 1, -1):
            return "turned"
        return "turned-exact"
    if placement["q"] != 1:
        return "grown" if placement["q"] > 1 else "shrunk"
    return "plain"


def variant_record(svg_recipe, registry, parent_uid=None):
    """The proposal payload for the acted recipe in an SVG.

    svg_recipe: (uid, name, rows, placement) as ph_svg.read_svg returns.
    Returns (record, note). note says what was refused, when it was."""
    uid, name, (rows_x, rows_y), placement = svg_recipe
    if parent_uid is None:
        parent_uid = uid.rstrip("abcdefghijklmnopqrstuvwxyz") or uid
    parent = next((r for r in registry["curves"] if r["uid"] == parent_uid),
                  None)
    if parent is None:
        return None, f"the parent {parent_uid} is not in the registry"
    parent_rows = ([Fraction(v) if not isinstance(v, str) or "/" in v
                    else Fraction(v) for v in parent["speedX"]],
                   [Fraction(v) if not isinstance(v, str) or "/" in v
                    else Fraction(v) for v in parent["speedY"]])
    from curve_lab.measure import to_fraction
    parent_rows = ([to_fraction(v) for v in parent["speedX"]],
                   [to_fraction(v) for v in parent["speedY"]])

    if placement["dx"] != 0 or placement["dy"] != 0:
        return None, ("a translation is a view, not a curve — the record "
                      "stays the parent; the offset stays in the SVG")

    baked_x, baked_y = place_rows(rows_x, rows_y, placement)
    descriptor = _descriptor(rows_x, rows_y, placement, *parent_rows)
    new_uid = _next_uid(registry, parent_uid)

    ca, cb = placement["a"] ** 2 - placement["b"] ** 2, 2 * placement["a"] * placement["b"]
    q = placement["q"]
    matrix = [[ca * q, -cb * q], [cb * q, ca * q]]
    record = {
        "uid": new_uid,
        "name": f"{parent['name']}-{descriptor}",
        "base_uid": parent_uid,
        "speedX": [_row_cell(v) for v in baked_x],
        "speedY": [_row_cell(v) for v in baked_y],
        "kind": "rows",
        "variant": "inkscape",
        "source": "inkscape-roundtrip",
        "transform": {"degrees": 0, "matrix": [[_row_cell(v) for v in row]
                                               for row in matrix],
                      "exact": True},
        "candidate": True,
        "starred": False,
        "importance": 0,
        "lists": [],
    }
    note = (f"position degree {degree_of(baked_x, baked_y)} · "
            f"grid {grid(baked_x, baked_y)} · bend {bend(baked_x, baked_y):.3f}")
    return record, note


def sandbox_payload(record):
    """The body for POST /api/sandbox-curves: one name, one curve, the
    record stored as written. The row's key is the uid; the chosen name
    (`curveName`) is what promotion reads."""
    return {"curves": [{
        "name": record["uid"],
        "curveName": record["name"],
        "base_uid": record["base_uid"],
        "speedX": record["speedX"],
        "speedY": record["speedY"],
        "kind": record["kind"],
        "variant": record["variant"],
        "source": record["source"],
        "transform": record["transform"],
        "candidate": True,
        "origin": "inkscape-roundtrip",
    }]}


def post_candidate(record, url):
    """POST the proposal to the app's sandbox-curves endpoint. Returns
    (status, response-text). stdlib only — the extension runs inside
    Inkscape's python."""
    from urllib.request import Request, urlopen
    body = json.dumps(sandbox_payload(record)).encode()
    request = Request(url, data=body, headers={"content-type": "application/json"})
    with urlopen(request, timeout=30) as response:
        return response.status, response.read().decode()
