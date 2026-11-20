"""The circle the walk cannot see — one idea, four implementations, all exact.

    .venv/bin/python scripts/circle_split.py            # the numbers, and the checks
    .venv/bin/python scripts/circle_split.py --write    # also workbench/circle-split.json

The idea (spec: "Priority: the circle the walk cannot see"): a curve's circular part is
a constant on the walk, so the walk is blind to it. Take the circle out, read what is
left at the walk's stations, and the curve is reformed on the exact lattice.

Four ways, each checked in `Fraction` on a small exact walk — `(3, 4, 5)`, whose stations
are ratios of numbers no bigger than 25 raised to a power, so the check is exact without
being slow:

1. **The quadratic split.** `A x² + 2B xy + C y²` splits into `((A + C)/2)(x² + y²)` plus
   `((A − C)/2)(x² − y²) + 2B xy`. The first is the constant the walk cannot see.
2. **The general split.** Any polynomial is reduced by `x² + y² = 1` to `a(y) + x·b(y)`;
   its constant term is the blind part, the rest is the remainder the walk reads.
3. **The lace curve is a circle walk.** Its rows are `u, v`, and its speed is
   `x' = u² − v²`, `y' = 2uv` — the double-angle form of a circle of radius `u² + v²`.
   So `(x'/Q, y'/Q)` is an exact rational point of the unit circle at every station, and
   the curve's character is circular through and through.
4. **Circle parameters reform a stored curve.** With `t = Y / (1 + X)` taken from the
   walk, `t` is rational and every coordinate of the stored curve is rational with it, so
   the curve can be re-stationed on the lattice without a decimal.

A non-zero error exits 1. Nothing here is a float check: the floats printed are only for
reading, the fractions are the evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "workbench" / "circle-split.json"

# Small exact walk: apex (4, 3), rotation (7, 24, 25) — every station is a ratio of
# numbers no bigger than 25^k, so exact arithmetic stays quick.
EXACT_TRIPLE = (3, 4, 5)
STATIONS = 12

FORMS = [
    ("x² + 2xy + y² = 1", 1, 1, 1),
    ("2x² + 2xy − 2y² = 1", 2, 1, -2),
    ("x² + y² = 1, the circle itself", 1, 0, 1),
    ("3x² + 4xy + 3y² = 1, equal squares", 3, 2, 3),
]

GENERAL = [
    ("(x² + y²)² = 1", {(4, 0): 1, (2, 2): 2, (0, 4): 1}),
    ("x³ + y³ = 1", {(3, 0): 1, (0, 3): 1}),
    ("x⁴ + x y = 1", {(4, 0): 1, (1, 1): 1}),
]


# ---------------------------------------------------------------- exact walk

def exact_stations(triple, count):
    """The walk's stations as exact fractions, one step at a time.

    `(X, Y) <- ((X A - Y B) / z², (X B + Y A) / z²)` with `A = a² - b²`, `B = 2ab`,
    starting at the apex `(a, b)` with the longer leg on x. The modulus is 1 by
    construction, and the first check below proves it at every station.
    """
    a, b, z = triple
    if b > a:
        a, b = b, a
    A, B, Z = a * a - b * b, 2 * a * b, z * z
    X, Y = Fraction(a, z), Fraction(b, z)   # normalised: the walk sits on the unit circle
    out = []
    for _ in range(count):
        out.append((X, Y))
        X, Y = (X * A - Y * B) / Z, (X * B + Y * A) / Z
    return out


# ---------------------------------------------------------------- polynomials

def pmul(p, q):
    out = [Fraction(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            out[i + j] += x * y
    return out


def padd(p, q):
    n = max(len(p), len(q))
    return [(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0) for i in range(n)]


def psub(p, q):
    n = max(len(p), len(q))
    return [(p[i] if i < len(p) else 0) - (q[i] if i < len(q) else 0) for i in range(n)]


def peval(p, t):
    total = Fraction(0)
    for coefficient in reversed(p):
        total = total * t + coefficient
    return total


def pintegral(p):
    return [Fraction(0)] + [Fraction(c, i + 1) for i, c in enumerate(p)]


def trim(p):
    p = [Fraction(c) for c in p]
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


# ------------------------------------------------------- implementation 1 and 2

def split_quadratic(A, B, C):
    return (Fraction(A + C, 2),
            (Fraction(A - C, 2), Fraction(2 * B), Fraction(C - A, 2)))


def check_quadratic(name, A, B, C, stations):
    circular, remainder = split_quadratic(A, B, C)
    worst = Fraction(0)
    for X, Y in stations:
        left = A * X * X + 2 * B * X * Y + C * Y * Y - circular
        right = remainder[0] * X * X + remainder[1] * X * Y + remainder[2] * Y * Y
        worst = max(worst, abs(left - right))
        worst = max(worst, abs(X * X + Y * Y - 1))   # the walk is on the circle
    return {
        "way": "quadratic split",
        "form": name,
        "circularPart": str(circular),
        "remainder": [str(v) for v in remainder],
        "identityWorstError": str(worst),
    }


def reduce_mod_circle(terms):
    """`x² -> 1 - y²` until no power of x above one is left: normal form a(y) + x b(y)."""
    stack = [((int(i), int(j)), Fraction(c)) for (i, j), c in terms.items()]
    normal: dict[tuple[int, int], Fraction] = {}
    while stack:
        (i, j), c = stack.pop()
        if i >= 2:
            stack.append(((i - 2, j), c))
            stack.append(((i - 2, j + 2), -c))
        else:
            normal[(i, j)] = normal.get((i, j), Fraction(0)) + c
    return {key: value for key, value in normal.items() if value != 0}


def check_general(name, terms, stations):
    normal = reduce_mod_circle(terms)
    circular = normal.get((0, 0), Fraction(0))
    remainder = {key: value for key, value in normal.items() if key != (0, 0)}
    worst = Fraction(0)
    for X, Y in stations:
        left = sum(c * X ** int(i) * Y ** int(j) for (i, j), c in terms.items())
        right = circular + sum(c * X ** int(i) * Y ** int(j) for (i, j), c in remainder.items())
        worst = max(worst, abs(left - right))
    return {
        "way": "general split",
        "form": name,
        "circularPart": str(circular),
        "remainderTerms": [[list(key), str(value)] for key, value in remainder.items()],
        "identityWorstError": str(worst),
    }


# --------------------------------------------------------------- implementation 3

def lace_rows(uid, registry):
    record = next(r for r in registry["curves"] if r["uid"] == uid)
    u = trim(record["speedX"])
    v = trim(record["speedY"])
    return record, u, v


def check_lace(uid, registry):
    """The rows are u and v; the speed is (u² − v², 2uv); the tangent is a circle point."""
    record, u, v = lace_rows(uid, registry)
    uu, vv = pmul(u, u), pmul(v, v)
    speed_x, speed_y = trim(psub(uu, vv)), trim(padd(padd(uu, vv), pmul(v, v)))  # 2uv built below
    speed_y = trim([Fraction(2) * c for c in pmul(u, v)])
    radius = trim(padd(uu, vv))

    worst = Fraction(0)
    for t in (Fraction(-2), Fraction(-1), Fraction(0), Fraction(1, 3),
              Fraction(1, 2), Fraction(2, 3), Fraction(1), Fraction(3)):
        xp, yp, q = peval(speed_x, t), peval(speed_y, t), peval(radius, t)
        worst = max(worst, abs(xp * xp + yp * yp - q * q))
        if q != 0:
            worst = max(worst, abs((xp / q) ** 2 + (yp / q) ** 2 - 1))
    return {
        "way": "lace curve is a circle walk",
        "uid": uid,
        "name": record["name"],
        "speedRadius": [str(c) for c in radius],
        "speedX": [str(c) for c in speed_x],
        "speedY": [str(c) for c in speed_y],
        "worstError": str(worst),
    }


# --------------------------------------------------------------- implementation 4

def check_circle_parameters(uid, registry, stations):
    """`t = Y / (1 + X)` from the walk; the stored curve's coordinates stay rational."""
    record, u, v = lace_rows(uid, registry)
    speed_x = trim(psub(pmul(u, u), pmul(v, v)))
    speed_y = trim([Fraction(2) * c for c in pmul(u, v)])
    radius = trim(padd(pmul(u, u), pmul(v, v)))
    position_x = pintegral(speed_x)
    position_y = pintegral(speed_y)
    worst = Fraction(0)
    rows = []
    total = 0
    for X, Y in stations:
        if X == -1:
            continue
        t = Y / (1 + X)
        total += 1
        # the half-angle parameter covers the whole line, so a station near (-1, 0)
        # sends t to infinity and the polynomial with it. The lace curve is built on
        # 0 <= t <= 1, so only those stations can reform it.
        if not (0 <= t <= 1):
            continue
        # the reformed station carries the curve's own speed identity with it
        xp, yp, q = peval(speed_x, t), peval(speed_y, t), peval(radius, t)
        worst = max(worst, abs(xp * xp + yp * yp - q * q))
        rows.append({
            "t": str(t),
            "tDecimal": round(float(t), 6),
            "x": str(peval(position_x, t)),
            "xDecimal": round(float(peval(position_x, t)), 6),
            "y": str(peval(position_y, t)),
            "yDecimal": round(float(peval(position_y, t)), 6),
        })
    return {"way": "circle parameters", "uid": uid, "name": record["name"],
            "usable": len(rows), "total": total,
            "interval": "0 <= t <= 1", "worstError": str(worst), "rows": rows}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    stations = exact_stations(EXACT_TRIPLE, STATIONS)
    report = {
        "triple": ",".join(str(v) for v in EXACT_TRIPLE),
        "stations": len(stations),
        "ways": [],
    }
    print(f"the exact walk: {report['triple']}, {len(stations)} stations, fractions only\n")

    for name, A, B, C in FORMS:
        row = check_quadratic(name, A, B, C, stations)
        report["ways"].append(row)
        print(f'{row["way"]:22}  {row["form"]:38}  blind part {row["circularPart"]:>4}  '
              f'error {row["identityWorstError"]}')

    for name, terms in GENERAL:
        row = check_general(name, terms, stations)
        report["ways"].append(row)
        print(f'{row["way"]:22}  {row["form"]:38}  blind part {row["circularPart"]:>4}  '
              f'{len(row["remainderTerms"])} remainder terms  error {row["identityWorstError"]}')

    registry = json.loads((ROOT / "workbench" / "curve-registry.json").read_text())
    for uid in ("c-0028", "c-0029", "c-0060"):
        row = check_lace(uid, registry)
        report["ways"].append(row)
        print(f'{row["way"]:22}  {uid} {row["name"]:16}  speed radius degree '
              f'{len(row["speedRadius"]) - 1}  error {row["worstError"]}')

    params = check_circle_parameters("c-0028", registry, stations)
    report["ways"].append(params)
    print(f'\n{params["way"]} on {params["uid"]}: t = Y/(1+X), {params["usable"]} of '
          f'{params["total"]} stations inside 0 <= t <= 1')
    for row in params["rows"][:3]:
        print(f'   t {row["tDecimal"]:>10}   x {row["xDecimal"]:>12}   y {row["yDecimal"]:>12}')
        print(f'   exact x = {row["x"]}')

    failures = [row for row in report["ways"]
                if row.get("identityWorstError", "0") != "0"
                or row.get("worstError", "0") != "0"]
    if failures:
        print("FAIL: an identity is not exact")
        return 1

    if args.write:
        OUT.write_text(json.dumps({"format": "curve-lab.circle-split/1", **report}, indent=1) + "\n")
        print(f"\nwrote {OUT.relative_to(ROOT)}")
    print("all identities exact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
