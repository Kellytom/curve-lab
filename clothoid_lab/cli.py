"""Command line: a preset or a design file in, one SVG out, the numbers printed.

The report is the point of the tool as much as the path is. It says how many
cubics were needed, how far they sit from the true clothoid, whether every join
is G2, the tightest radius on the chain, and for each rail whether it has folded
and by how much margin.

    python -m clothoid_lab.cli --preset s-curve --width 6 --out out/s-curve.svg

Exit status is 0 when the drawing is inside tolerance and the chain is G2, 1
when it is not. A fold in a rail is reported and does not fail the run, because
drawing the fold is a deliberate choice.
"""

from __future__ import annotations

import argparse
import os
import sys

from . import bezier, engine, presets, svg
from .model import Design
from .offsets import build_rails, rail_deviation


def render(design: Design, tol: float = 0.02, width: float | None = None,
           prec: int = 4, margin: float = 5.0,
           max_spans: int = 64) -> tuple[str, dict]:
    """Build a design into SVG text, with the report that justifies it."""
    chain = engine.build(design)
    spine, fit = bezier.fit_chain(chain, tol=tol, max_spans_per_segment=max_spans)
    spacing = bezier.path_deviation(spine, chain.point)

    distances = list(design.offsets)
    if width is not None:
        distances.extend([width / 2.0, -width / 2.0])
    rails = build_rails(chain, distances, tol=tol, max_spans_per_segment=max_spans)

    text = svg.document(design, chain, spine, rails, prec=prec, margin=margin)
    info = {
        "chain": engine.report(chain),
        "fit": fit,
        "spine_error": fit["error_max"],
        "spine_deviation": spacing,
        "rails": [
            {
                "distance": r["distance"],
                "spans": r["spans_count"],
                "error_max": r["error_max"],
                "deviation": rail_deviation(r, chain),
                "folds": r["folds"],
                "min_radius": r["min_radius"],
                "margin": r["margin"],
            }
            for r in rails
        ],
        "ok": fit["error_max"] <= tol and chain.g2,
    }
    return text, info


def format_report(info: dict, tol: float) -> str:
    c = info["chain"]
    lines = [
        f"segments      {c['segments']}   length {c['length']:.3f} mm",
        f"joins         {'G2' if c['join_g2'] else 'G1'}   "
        f"worst curvature jump {c['join_kappa_error_max']:.3e} 1/mm",
        f"tightest      radius {c['min_radius']:.3f} mm at s={c['min_radius_at']:.2f}",
        f"cubics        {info['fit']['spans']}  "
        f"per segment {info['fit']['spans_per_segment']}",
        f"fit           {info['spine_error']:.4f} mm worst, "
        f"{info['spine_deviation']:.4f} mm spacing  (tol {tol:g} mm)",
    ]
    for r in info["rails"]:
        fold = "fold" if r["folds"] else "clear"
        lines.append(
            f"rail {r['distance']:+.3f}  {fold}  {r['spans']} cubics  "
            f"error {r['error_max']:.4f} mm  margin {r['margin']:.3f} mm"
        )
        for s0, s1 in r["folds"]:
            lines.append(f"              folds from s={s0:.2f} to s={s1:.2f}")
    lines.append(f"verdict       {'inside tolerance' if info['ok'] else 'OVER TOLERANCE'}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="clothoid_lab", description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--preset", choices=sorted(presets.PRESETS), help="a named starting design")
    src.add_argument("--design", help="a design JSON file")
    ap.add_argument("--out", default=None, help="SVG path (default out/<name>.svg)")
    ap.add_argument("--json", default=None, help="also write the design JSON here")
    ap.add_argument("--tol", type=float, default=0.02, help="fit tolerance in mm")
    ap.add_argument("--width", type=float, default=None, help="ribbon width in mm, two rails")
    ap.add_argument("--prec", type=int, default=4, help="decimal places in the path data")
    ap.add_argument("--margin", type=float, default=5.0, help="page margin in mm")
    ap.add_argument("--quiet", action="store_true", help="write the file, print nothing")
    args = ap.parse_args(argv)

    design = Design.load(args.design) if args.design else presets.get(args.preset)
    if args.width is not None:
        if args.width <= 0:
            ap.error("--width must be positive")
    text, info = render(design, tol=args.tol, width=args.width,
                        prec=args.prec, margin=args.margin)

    out = args.out or os.path.join("out", f"{design.name.split()[0]}.svg")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    svg.write(out, text)

    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        design.save(args.json)

    if not args.quiet:
        print(format_report(info, args.tol))
        print(f"wrote         {out}")
    return 0 if info["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
