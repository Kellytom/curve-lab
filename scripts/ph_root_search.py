"""Exhaustive walk over the symmetric root construction.

    .venv/bin/python scripts/ph_root_search.py
    .venv/bin/python scripts/ph_root_search.py --degree 7 --write

A curve here is built from two speed rows, p(t) and q(t). Its shape is set by
where q is zero: at those t the vertical speed stops, so the tangent runs flat.
Those zeros are the roots of q.

If every root r is accompanied by its mirror 1 - r (and 1/2 is its own mirror),
then q(1 - t) = +q(t) or -q(t), and the curve is exactly symmetric: a mirror in
x for the plus sign, a half-turn about the centre for the minus sign. Throw a
random integer row at this and you will never see it, because symmetry is an
exact equation on the coefficients, not a tendency. Choose the roots first and
symmetry is true by construction. That is the whole trick.

So the walk is over root sets, not over numbers:

    positions   every fraction in (0, 1) whose denominator is in DENOMINATORS,
                taken below 1/2 (its mirror is 1 - r) plus the middle 1/2
    degree      up to --degree, which is the speed degree, so positions have
                degree + 1 (degree 5 is the degree-11 rung of the sandbox)
    x rows      the symmetric ones only: a constant, and c t(1 - t) forms

Anything found is measured exactly and reported with its rows, so it can be
pasted into the sandbox or written to workbench/root-family.json with --write.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from math import gcd, lcm
from itertools import combinations_with_replacement
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_metrics as metrics  # noqa: E402
import ph_root_family  # noqa: E402
from ph_crossings import pair_crossings, spine  # noqa: E402

DENOMINATORS = (2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16)
OUT = ROOT / "workbench" / "root-family.json"


def row_from_roots(roots) -> list[int]:
    """The coefficients of the product of (t - r), lowest power first, as integers."""
    coefficients = [Fraction(1)]
    for root in roots:
        wider = [Fraction(0)] * (len(coefficients) + 1)
        for power, value in enumerate(coefficients):
            wider[power] += -root * value
            wider[power + 1] += value
        coefficients = wider
    scale = 1
    for value in coefficients:
        scale = scale * value.denominator // gcd(scale, value.denominator)
    return [int(value * scale) for value in coefficients]


def mirrored_positions():
    """Fractions below 1/2 whose denominator is allowed, plus the middle."""
    out = set()
    for denominator in DENOMINATORS:
        for numerator in range(1, denominator):
            value = Fraction(numerator, denominator)
            if value < Fraction(1, 2):
                out.add(value)
    return sorted(out) + [Fraction(1, 2)]


def symmetric_sets(degree: int):
    """Every multiset of roots closed under r -> 1 - r, of total size `degree`.

    The middle root 1/2 is its own mirror, so it supplies whatever multiplicity
    the mirrored pairs leave over. Each pair contributes two roots, which is why
    the loop stops when 2 x pairs would exceed the degree.
    """
    pairs = mirrored_positions()[:-1]
    for size in range(0, degree // 2 + 1):
        for chosen in combinations_with_replacement(pairs, size):
            used = 2 * size
            middle = degree - used
            roots = []
            for value in chosen:
                roots.extend([value, 1 - value])
            if middle:
                roots.extend([Fraction(1, 2)] * middle)
            roots.sort()
            yield roots, ", ".join(str(value) for value in roots)


def x_rows():
    """The symmetric x rows.

    A constant, a bow c t(1 - t) on its own or on a constant, and rows with their
    own mirrored roots. The last group is the new axis: the x speed's flat spots
    turn the stroke vertically, so giving x roots adds loops without breaking the
    mirror, because the roots are mirrored too.
    """
    rows = [("flat", [Fraction(1)])]
    for c in (Fraction(1), Fraction(2), Fraction(4), Fraction(-1), Fraction(-2)):
        rows.append((f"bow{c}", [Fraction(0), c, -c]))
        rows.append((f"flat+bow{c}", [Fraction(1), c, -c]))
    for r in (Fraction(1, 2), Fraction(1, 3), Fraction(1, 4), Fraction(1, 6), Fraction(2, 5)):
        roots = [r] if r == Fraction(1, 2) else [r, 1 - r]
        built = [Fraction(v) for v in row_from_roots(roots)]
        rows.append((f"xroots-{r}", built))
        rows.append((f"flat+xroots-{r}", [Fraction(1)] + built[1:] if built[0] == 0 else
                     [Fraction(1) + built[0]] + built[1:]))
    return rows


def scaled(row, length: int) -> list[float]:
    """A row padded to the speed length, as floats for the measuring scripts."""
    out = [float(v) for v in row]
    return out + [0.0] * (length - len(out))


def mirror_of(points):
    """Flip across the vertical centre line."""
    centre = (min(x for x, _ in points) + max(x for x, _ in points)) / 2
    return [(2 * centre - x, y) for x, y in points]


def half_turn_of(points):
    """The same curve rotated 180 degrees about the centre of its box."""
    centre_x = (min(x for x, _ in points) + max(x for x, _ in points)) / 2
    centre_y = (min(y for _, y in points) + max(y for _, y in points)) / 2
    return [(2 * centre_x - x, 2 * centre_y - y) for x, y in points]


def distance_to(points, other) -> float:
    """Worst distance from one curve to the other, as a share of the size."""
    size = max(max(x for x, _ in points) - min(x for x, _ in points),
               max(y for _, y in points) - min(y for _, y in points)) or 1e-9

    def nearest(point, cloud):
        return min(((px - point[0]) ** 2 + (py - point[1]) ** 2) ** 0.5 for px, py in cloud)

    return max(max(nearest(p, other) for p in points),
               max(nearest(p, points) for p in other)) / size


def symmetry_of(points) -> float:
    """Worst distance to the curve's own vertical mirror, as a share of its size."""
    return distance_to(points, mirror_of(points))


def rotate(points, degrees):
    from math import cos, radians, sin
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    angle = radians(degrees)
    cos_a, sin_a = cos(angle), sin(angle)
    return [(cx + (x - cx) * cos_a - (y - cy) * sin_a,
             cy + (x - cx) * sin_a + (y - cy) * cos_a) for x, y in points]


def x_row_kind(row):
    """Which family an x row belongs to: 'flat', 'bow', or 'roots'.

    flat   a constant, so the stroke only moves sideways
    bow    1 + c t(1-t): the bow family, one lean
    roots  the row carries its own mirrored roots: the newer axis
    """
    values = [float(v) for v in row]
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    if len(values) == 1:
        return "flat"
    if len(values) == 3 and abs(values[1] + values[2]) < 1e-9:
        return "bow"
    return "roots"


def describe(speed_x, speed_y):
    """Everything the report needs, or None when the curve is unusable.

    The cheap tests run first: the spine gives the size, the aspect and the
    mirror distance, and only a survivor pays for the exact metrics. That is what
    makes a higher rung of the walk finish in minutes.
    """
    _, x, y = spine(speed_x, speed_y, 400)
    points = list(zip(x, y))
    width = max(x) - min(x)
    height = max(y) - min(y)
    if height <= 0 or width <= 0:
        return None
    aspect = width / height
    if not (0.25 < aspect < 4):
        return None
    # Odd-degree rows mirror in x; even-degree rows turn half way round. Both are
    # exact; the filter has to accept the one the curve actually has.
    if distance_to(points, mirror_of(points)) <= 1e-6:
        kind, partner, partner_name = "mirror", rotate(points, 180), "half-turn copy"
        symmetry = distance_to(points, mirror_of(points))
    elif distance_to(points, half_turn_of(points)) <= 1e-6:
        kind, partner, partner_name = "half-turn", mirror_of(points), "mirror copy"
        symmetry = distance_to(points, half_turn_of(points))
    else:
        return None
    measured = metrics.metrics(speed_x, speed_y)
    if measured["pitch"] > 5_000_000 or measured["bend"] > 40:
        return None
    return {
        "bend": round(measured["bend"], 3),
        "pitch": int(measured["pitch"]),
        "inflections": measured["inflection_count"],
        "aspect": round(aspect, 3),
        "symmetry": symmetry,
        "symmetryKind": kind,
        "partner": partner_name,
        "crossings180": len(pair_crossings(points, partner)),
        "crossings90": len(pair_crossings(points, rotate(points, 90))),
        "self": len(pair_crossings(points, points)),
    }


def search(degree: int):
    """Every symmetric root set and symmetric x row at this speed degree."""
    found = []
    seen = set()
    for roots, described in symmetric_sets(degree):
        speed_y = row_from_roots(roots)
        for label, x_row in x_rows():
            speed_x = scaled(x_row, len(speed_y))
            key = (tuple(round(v, 12) for v in speed_x), tuple(speed_y))
            if key in seen:
                continue
            seen.add(key)
            try:
                measured = describe(speed_x, speed_y)
            except (ZeroDivisionError, ValueError):
                continue
            if measured is None or measured["symmetry"] > 1e-6:
                continue
            found.append({"roots": described, "xRow": label, "rootList": roots,
                          "speedX": speed_x, "speedY": speed_y, **measured})
    return found


def name_of(curve) -> str:
    """A name that states the construction: kind, every mirrored pair, the middle count.

    `lace-1of8-3` is a lace (four or more self-crossings) with roots at 1/8 and
    7/8 and three roots at 1/2. `wave-1of4-1of3-1` carries two pairs. A reader can
    rebuild the row from the name alone, which is the point of the naming rule.
    """
    roots = curve["rootList"]
    counts = {}
    for value in roots:
        if value == Fraction(1, 2):
            continue
        pair = min(value, 1 - value)
        counts[pair] = counts.get(pair, 0) + 1
    middle = sum(1 for value in roots if value == Fraction(1, 2))
    kind = "lace" if curve["self"] >= 4 else "wave"
    if not counts:
        return f"{kind}-middle-{middle}"
    tokens = []
    for pair in sorted(counts):
        times = counts[pair] // 2          # a pair is two roots; the name counts pairs
        stem = f"{pair.numerator}of{pair.denominator}"
        tokens.append(stem if times == 1 else f"{times}x{stem}")
    return f"{kind}-{'-'.join(tokens)}-{middle}"


def proportional(first, second) -> bool:
    """True when two rows are the same row up to a positive scale."""
    if len(first) != len(second):
        return False
    ratio = None
    for a, b in zip(first, second):
        if b == 0:
            if a != 0:
                return False
            continue
        share = a / b
        if ratio is None:
            ratio = share
        elif abs(share - ratio) > 1e-9 * max(1, abs(ratio)):
            return False
    return ratio is not None and ratio > 0


def write_found(entries):
    """Append the best rows to workbench/found-curves.json, the gallery's own file."""
    path = ROOT / "workbench" / "found-curves.json"
    if path.exists():
        try:
            document = json.loads(path.read_text())
        except json.JSONDecodeError:
            document = {"name": "found-curves", "curves": []}
    else:
        document = {"name": "found-curves", "curves": []}
    known = {(tuple(c["speedX"]), tuple(c["speedY"])) for c in document["curves"]}
    names = {c["name"] for c in document["curves"]}
    seeds = ph_root_family.seeds()
    added = 0
    skipped = []
    for curve in entries:
        key = (tuple(curve["speedX"]), tuple(curve["speedY"]))
        if key in known:
            continue
        same = [name for name, seed_x, seed_y in seeds
                if proportional(curve["speedY"], seed_y) and proportional(curve["speedX"], seed_x)]
        if same:
            skipped.append(f"{curve['roots']} is already {same[0]}")
            continue
        name = name_of(curve)
        if name in names:
            suffix = 2
            while f"{name}-{suffix}" in names:
                suffix += 1
            name = f"{name}-{suffix}"
        names.add(name)
        known.add(key)
        document["curves"].append({
            "name": name,
            "speedX": curve["speedX"],
            "speedY": curve["speedY"],
            "bend": curve["bend"],
            "pitch": curve["pitch"],
            "inflections": curve["inflections"],
            "meetings180": curve["crossings180"],
            "partner": curve["partner"],
            "symmetryKind": curve["symmetryKind"],
            "self": curve["self"],
            "roots": curve["roots"],
            "rootsExact": [str(value) for value in curve["rootList"]],
            "from": "found",
        })
        added += 1
    document["note"] = ("written by scripts/ph_root_search.py (and ph_find.py); the gallery "
                        "reads this file at load, so no rebuild is needed")
    path.write_text(json.dumps(document, indent=1) + "\n")
    print(f"\n{path.relative_to(ROOT)}  {added} new, {len(document['curves'])} in all")
    for line in skipped:
        print(f"  skipped: {line}")
    return document


def rename_existing():
    """Bring every stored name back to the construction it states, without remeasuring.

    A name is a claim about the roots, so a file whose names disagree with its
    roots is wrong even when the curve is right. New names are checked against
    the whole file before they are kept.
    """
    path = ROOT / "workbench" / "found-curves.json"
    document = json.loads(path.read_text())
    curves = document["curves"]
    taken = {curve["name"] for curve in curves}
    changed = []
    touched = False
    for curve in curves:
        roots = [Fraction(text) for text in curve.get("rootsExact", [])]
        if not roots:
            continue
        wanted = name_of({"rootList": roots, "self": curve.get("self", 0)})
        if wanted == curve["name"]:
            continue
        name, suffix = wanted, 2
        while name in taken and name != curve["name"]:
            name = f"{wanted}-{suffix}"
            suffix += 1
        taken.discard(curve["name"])
        taken.add(name)
        changed.append(f"{curve['name']} -> {name}")
        curve["name"] = name
    # the two fields added after the first rows were written: the parity of the
    # speed degree decides the symmetry, and no measurement is needed for it
    for curve in curves:
        degree = len(curve["speedY"]) - 1
        kind = "half-turn" if degree % 2 == 0 else "mirror"
        partner = "mirror copy" if kind == "half-turn" else "half-turn copy"
        if curve.get("symmetryKind") != kind:
            curve["symmetryKind"] = kind
            curve["partner"] = partner
            touched = True
    if changed or touched:
        path.write_text(json.dumps(document, indent=1) + "\n")
    print(f"{len(changed)} names corrected")
    for line in changed:
        print("  " + line)
    return changed


def main():
    global DENOMINATORS

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--degree", type=int, default=5,
                        help="speed degree (5 is the degree-11 rung; positions have degree + 1)")
    parser.add_argument("--write", action="store_true",
                        help="write workbench/root-family.json")
    parser.add_argument("--found", action="store_true",
                        help="add the best row of each shape to workbench/found-curves.json")
    parser.add_argument("--rename", action="store_true",
                        help="correct the stored names in found-curves.json and stop")
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--denominators", default=",".join(str(value) for value in DENOMINATORS),
                        help="comma-separated denominators of the mirror positions")
    args = parser.parse_args()
    if args.rename:
        rename_existing()
        return
    DENOMINATORS = tuple(int(value) for value in args.denominators.split(",") if value.strip())

    found = search(args.degree)
    found.sort(key=lambda row: (-row["crossings180"], -row["crossings90"],
                                -row["inflections"], row["bend"], row["pitch"]))
    print(f"\nsymmetric root sets at speed degree {args.degree}: "
          f"{len(found)} curves survive the shape filter")
    print(f"{'roots':34s} {'x':10s} {'meets180':>8s} {'90':>3s} {'infl':>4s} "
          f"{'bend':>6s} {'pitch':>9s}  rows")
    for row in found[:args.top]:
        print(f"{row["roots"][:34]:34s} {row['xRow']:10s} {row['crossings180']:8d} "
              f"{row['crossings90']:3d} {row['inflections']:4d} {row['bend']:6.2f} "
              f"{row['pitch']:9d}  x {_short(row['speedX'])}  y {_short(row['speedY'])}")
    if args.write and found:
        document = {
            "name": "root-family",
            "note": ("written by scripts/ph_root_search.py; every curve is exactly symmetric "
                     "because its roots come in mirror pairs about t = 1/2"),
            "degree": args.degree,
            "curves": [{k: v for k, v in row.items() if k != "rootList"}
                       for row in found[:max(args.top, 24)]],
        }
        OUT.write_text(json.dumps(document, indent=1) + "\n")
        print(f"\n{OUT.relative_to(ROOT)}  {len(document['curves'])} curves")

    if args.found and found:
        best = []
        seen_rows = set()
        for row in found:
            key = tuple(row["speedY"])
            if key in seen_rows:
                continue
            seen_rows.add(key)
            best.append(row)
        write_found(best[:args.top])


def _short(row):
    trimmed = list(row)
    while len(trimmed) > 1 and trimmed[-1] == 0:
        trimmed.pop()
    return "[" + ",".join(f"{v:g}" for v in trimmed) + "]"


if __name__ == "__main__":
    main()
