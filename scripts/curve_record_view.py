"""Annotate every finder curve with its formula, variables, grid and sandbox verdict.

    .venv/bin/python scripts/curve_record_view.py           # write workbench/finder.json
    .venv/bin/python scripts/curve_record_view.py --dry     # print only

The point is to show the work, not hide it: on each card the operator sees the
formula the curve is defined by, the numbers in it, the integer grid it needs, and
whether the sandbox can load it — with the reason when it cannot.

Kinds:
    position-poly   x(t), y(t) polynomials            (septic, solved, weighted)
    rational        ratio of polynomials per coordinate (limacons, roses, mobiles)
    ph-speed        two speed rows u, v with x' = u^2 - v^2, y' = 2uv
                    (the only kind the sandbox gallery loads today)
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

FINDER = ROOT / "workbench" / "finder.json"


def lcm(a, b):
    return a * b // gcd(a, b) if a and b else max(a, b)


def frac(value):
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError):
        return Fraction(0)


def grid_of(coefficients):
    g = 1
    for c in coefficients:
        g = lcm(g, frac(c).denominator)
    return g


def poly_text(coefficients, symbol="t"):
    parts = []
    for power, c in enumerate(coefficients):
        value = frac(c)
        if value == 0:
            continue
        term = (f"{value}" if value.denominator == 1 else f"({value})")
        if power == 0:
            parts.append(term)
        elif power == 1:
            parts.append(f"{term}{symbol}")
        else:
            parts.append(f"{term}{symbol}^{power}")
    return " + ".join(parts).replace("+ -", "- ") or "0"


def septic_rows(spec):
    k = frac(spec.get("k", 1)); a = frac(spec.get("a", 0)); b = frac(spec.get("b", 0))
    c = frac(spec.get("c", 0)); d = frac(spec.get("d", 0)); e = frac(spec.get("e", 0))
    f = frac(spec.get("f", 0))
    P = [0, k, 0, d, 0, b, 0, 1]
    Q = [f, 0, e, 0, c, 0, a, 0]
    x = [frac(q) - frac(p) for p, q in zip(P, Q)]
    y = [frac(q) + frac(p) for p, q in zip(P, Q)]
    return x, y, "x = Q - P, y = Q + P (P odd, Q even)"


def solved_rows(coefficients):
    d = frac(coefficients.get("d", 0)); e = frac(coefficients.get("e", 0))
    c = frac(coefficients.get("c", 1))
    P = [0, 1, 0, d, 0, 0, 0, 1]
    Q = [1, 0, e, 0, c]
    n = max(len(P), len(Q))
    P += [0] * (n - len(P)); Q += [0] * (n - len(Q))
    x = [frac(q) - frac(p) for p, q in zip(P, Q)]
    y = [frac(q) + frac(p) for p, q in zip(P, Q)]
    return x, y, "x = Q - P, y = Q + P"


def annotate(curve):
    family = curve.get("family")
    definition = curve.get("definition") or {}
    record = {"kind": None, "formula": "", "variables": {}, "grid": None,
              "sandbox": False, "sandboxReason": ""}

    if family in ("septic",):
        spec = definition.get("spec") or {}
        x, y, note = septic_rows(spec)
        record.update(kind="position-poly", variables=spec, note=note)
        record["grid"] = lcm(grid_of(x), grid_of(y))
        record["formula"] = f"x = {poly_text(x)} ; y = {poly_text(y)}"
        record["sandboxReason"] = "position rows, not a speed pair — the sandbox gallery loads u, v only"
    elif family == "solved-crossings":
        coeff = definition.get("coefficients") or {}
        x, y, note = solved_rows(coeff)
        record.update(kind="position-poly", variables=coeff, note=note)
        record["grid"] = lcm(grid_of(x), grid_of(y))
        record["formula"] = f"x = {poly_text(x)} ; y = {poly_text(y)}"
        record["sandboxReason"] = "position rows, not a speed pair"
    elif family == "weighted-balance":
        coeff = definition.get("coefficients") or {}
        x, y, note = solved_rows({**coeff, "c": "1"})
        record.update(kind="position-poly", variables={**coeff, "kind": definition.get("kind"), "t0": definition.get("t0")})
        record["grid"] = lcm(grid_of(x), grid_of(y))
        record["formula"] = f"x = {poly_text(x)} ; y = {poly_text(y)}"
        record["sandboxReason"] = "position rows, not a speed pair"
    elif family == "bounded":
        spec = definition.get("spec") or {}
        record.update(kind="rational", variables=spec)
        if "polar" in spec:
            raw = spec["polar"]
            if isinstance(raw, str):
                raw = raw.strip("()[] ").replace(",", " ").split()
            a, b = raw[0], raw[1]
            record["formula"] = (f"r = {a} + {b}cos θ,  x = r cos θ, y = r sin θ, "
                                 f"cos θ = (1−t²)/(1+t²)")
        else:
            record["formula"] = ("x = (ax t² + bx t + cx)/(1+t²), "
                                 "y = (ay t² + by t + cy)/(1+t²)")
            record["grid"] = grid_of([spec.get(k, 0) for k in
                                      ("ax", "bx", "cx", "ay", "by", "cy")] + [1])
        record["sandboxReason"] = "rational coordinates — the sandbox has no ratio rows"
    elif family in ("roses-rational",):
        spec = definition
        record.update(kind="rational", variables={"a": spec.get("a"), "b": spec.get("b"), "k": spec.get("k")})
        record["formula"] = (f"r = {spec.get('a')} + {spec.get('b')}cos({spec.get('k')}θ), "
                             "with cos(kθ) a Chebyshev polynomial in cos θ")
        record["sandboxReason"] = "rational coordinates — no speed rows"
    elif family in ("mobile-exact", "mobile", "mobile-arcs"):
        vanes = definition.get("vanes") or []
        record.update(kind="rational", variables={"vanes": vanes})
        record["formula"] = "z(t) = Σ a_k R(n_k t), R = ((1−t²) + 2it)/(1+t²)"
        if definition.get("t1") is not None:
            record["formula"] += f", cut from t = {definition['t1']} to {definition['t2']}"
        record["sandboxReason"] = "rational rotations — no speed rows"
    elif family == "tschirnhausen":
        record.update(kind="ph-speed", variables={"form": definition.get("kind")})
        record["formula"] = ("x = 1 − 3t², y = 3t − t³  (PH: speed 3(1 + t²)); "
                             "elevated forms add one handle move")
        record["grid"] = 1
        record["sandbox"] = False
        record["sandboxReason"] = ("PH, so speed rows exist — but after a scale and a "
                                   "Möbius change of parameter, not as these coefficients")
    else:
        record["sandboxReason"] = "no definition recorded"

    curve["record"] = record
    return record


def main(argv):
    data = json.loads(FINDER.read_text(encoding="utf-8"))
    counts = {"position-poly": 0, "rational": 0, "ph-speed": 0, None: 0}
    for curve in data["curves"]:
        record = annotate(curve)
        counts[record["kind"]] = counts.get(record["kind"], 0) + 1
        print(f'{curve["name"]:34} {str(record["kind"]):14} grid {str(record["grid"]):>6}  '
              f'sandbox {"yes" if record["sandbox"] else "no"} — {record["sandboxReason"][:60]}')
    print("\nkinds:", counts)
    if "--dry" not in argv:
        FINDER.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("annotated workbench/finder.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
