"""Command line: build one chain, report it exactly, optionally draw it."""

from __future__ import annotations

import argparse
import math
from fractions import Fraction

from . import design, spans as spanmod, svg
from .closure import closure_pairs, g2_pairs
from .spiral import Spiral
from .triples import Triple, thinnest


def _triangle(text: str, limit: int) -> Triple:
    if text in ("thin", "thinnest"):
        return thinnest(limit)
    parts = text.replace("-", ",").split(",")
    if len(parts) != 3:
        raise SystemExit(f"--triangle wants a-b-c or 'thin', got {text!r}")
    a, b, c = (int(p) for p in parts)
    return Triple(min(a, b), max(a, b), c)


def _build(args, triangle: Triple) -> Spiral:
    length = Fraction(args.length)
    if args.mode == "spiral":
        return design.spiral(triangle, args.steps, length)
    if args.mode == "lobe":
        return design.lobe(triangle, args.steps, length)
    if args.mode == "hook":
        return design.hook(triangle, args.multiplier, args.n_out, length)
    return design.g2_lobe(triangle, args.steps, length)


def report(path: Spiral, digits: int = 6) -> str:
    x, y = path.final
    ints, scale = path.integer_form()
    ix, iy = ints[-1]
    head = path.heading.axis_name()
    cloth = path.equivalent_clothoid()
    lines = [
        f"triangle      {path.triangle}   alpha = {path.triangle.degrees:.6f} deg"
        f"   tan = {path.triangle.slope}",
        f"chords        {len(path.turns)}   step = {path.length}"
        f"   arc = {path.arc_length}",
        f"turn coeff    {path.coeff}   heading = {path.heading.degrees:.6f} deg"
        f"   axis = {head or 'not axis-aligned'}",
        f"final x       {x}",
        f"final y       {y}",
        f"final (float) ({float(x):.{digits}f}, {float(y):.{digits}f})",
        f"final (int)   ({ix}, {iy})   after exact scale {scale}",
        f"clothoid      kappa0 = {cloth['kappa0']:.9g}   kd = {cloth['kd']:.9g}"
        f"   A^2 = {cloth['A2']:.6f}",
        f"resolution    usable steps ~ {path.usable_steps()}"
        f"   widest chord angle = {math.degrees(path.chord_angle()):.2f} deg",
        f"exactness     coefficient {path.coeff} -> "
        f"{'exactly on the axis' if path.heading.is_axis_aligned() else 'off axis'}",
    ]
    if path.chord_angle() > 0.9:
        lines.append("warning       a chord turns more than ~52 deg: the chain is "
                     "aliased here, not a curve")
    if path.cusps:
        lines.append(f"cusps         {path.cusps} (exact quarter turns)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="triples-clothoid", description=__doc__)
    p.add_argument("--triangle", default="thin",
                   help="'thin', or a primitive triple like 79-3120-3121")
    p.add_argument("--limit", type=int, default=3125,
                   help="hypotenuse bound when choosing the thin triangle")
    p.add_argument("--mode", default="lobe",
                   choices=["spiral", "lobe", "hook", "g2"])
    p.add_argument("--steps", type=int, default=15)
    p.add_argument("--multiplier", type=int, default=3,
                   help="hook: how much faster the exit unwinds")
    p.add_argument("--n-out", type=int, default=None,
                   help="hook: force an exit length instead of the first closure")
    p.add_argument("--length", default="1", help="chord length, integer or a/b")
    p.add_argument("--page", type=float, default=200.0)
    p.add_argument("--max-turn", type=float, default=20.0,
                   help="degrees of heading change allowed inside one cubic")
    p.add_argument("--out", default=None, help="write an SVG here")
    p.add_argument("--list-closures", action="store_true",
                   help="print exact closure pairs and exit")
    args = p.parse_args(argv)

    if args.list_closures:
        print("hook closures  (n_wind, n_unwind) with T(n_wind) = m*T(n_unwind)")
        for m in (2, 3, 4, 8, 15):
            print(f"  m={m:2d}  {closure_pairs(m, 60)}")
        print("g2 closures    (m, j) with j(j+1) = 2m(m+1)")
        print(f"  {g2_pairs(120)}")
        return 0

    triangle = _triangle(args.triangle, args.limit)
    path = _build(args, triangle)
    print(report(path))

    curves = spanmod.spans(path, math.radians(args.max_turn))
    nodes = path.floats()
    worst = max((spanmod.deviation(s, nodes) for s in curves), default=0.0)
    floor = spanmod.sagitta(path)
    print(f"cubics        {len(curves)}   worst distance to the chords "
          f"{worst:.6g} ({100 * worst / max(1e-9, float(path.length)):.2f}% of a chord)")
    print(f"chord floor   {floor:.6g}   (fit is at the chain's own resolution)")

    if args.out:
        text = svg.document(path, curves, page=(args.page, args.page),
                            title=f"triples-clothoid {path.triangle}")
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote         {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
