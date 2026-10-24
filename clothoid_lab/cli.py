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
           max_spans: int = 64, split: int = 2,
           backend: str | None = None,
           page: tuple[float, float] | None = None,
           frame: tuple[float, float] | None = None,
           view: str | None = None) -> tuple[str, dict]:
    """Build a design into SVG text, with the report that justifies it."""
    chain = engine.build(design, backend=backend)
    spine, fit = bezier.fit_chain(chain, tol=tol, max_spans_per_segment=max_spans,
                                  split=split)
    spacing = bezier.path_deviation(spine, chain.point)

    distances = list(design.offsets)
    if width is not None:
        distances.extend([width / 2.0, -width / 2.0])
    rails = build_rails(chain, distances, tol=tol, max_spans_per_segment=max_spans,
                        split=split)

    text = svg.document(design, chain, spine, rails, prec=prec, margin=margin,
                        page=page, frame=frame, view=view)
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
                "clamped": r["clamped"],
                "min_radius": r["min_radius"],
                "margin": r["margin"],
            }
            for r in rails
        ],
        "fit_ok": fit["error_max"] <= tol,
        "ok": fit["error_max"] <= tol and chain.g2,
        "worst_join": max(chain.joins, key=lambda j: abs(j["d_kappa"]), default=None),
    }
    return text, info


def format_report(info: dict, tol: float) -> str:
    c = info["chain"]
    lines = [
        f"engine        {c['backend']}",
        f"segments      {c['segments']}   length {c['length']:.3f} mm",
        f"joins         {'G2' if c['join_g2'] else 'G1'}   "
        f"worst curvature jump {c['join_kappa_error_max']:.3e} 1/mm",
        f"tightest      radius {c['min_radius']:.3f} mm at s={c['min_radius_at']:.2f}",
        f"cubics        {info['fit']['spans']}  split {info['fit']['split']}  "
        f"per segment {info['fit']['spans_per_segment']}",
        f"fit           {info['spine_error']:.4f} mm worst, "
        f"{info['spine_deviation']:.4f} mm spacing  (tol {tol:g} mm)",
    ]
    for r in info["rails"]:
        fold = "fold" if r["folds"] else "clear"
        clamp = f"  {r['clamped']} clamped at the reversal" if r.get("clamped") else ""
        lines.append(
            f"rail {r['distance']:+.3f}  {fold}  {r['spans']} cubics  "
            f"error {r['error_max']:.4f} mm  margin {r['margin']:.3f} mm{clamp}"
        )
        for s0, s1 in r["folds"]:
            lines.append(f"              folds from s={s0:.2f} to s={s1:.2f}")
    lines.append(f"verdict       {_verdict(info, tol)}")
    return "\n".join(lines)


def _verdict(info: dict, tol: float) -> str:
    """Say which promise failed, because the two failures look nothing alike."""
    if info.get("ok"):
        return "inside tolerance, joins G2"
    reasons = []
    if not info.get("fit_ok", True):
        reasons.append(f"fit {info['spine_error']:.4f} mm over tol {tol:g} mm")
    join = info.get("worst_join")
    if join and abs(join["d_kappa"]) >= 1e-9:
        reasons.append(
            f"join at s={join['at']:.2f} jumps {join['d_kappa']:+.3e} 1/mm, so G1 not G2 "
            f"(set kappa0 to null to inherit)")
    return "; ".join(reasons) if reasons else "over tolerance"


def backend_names() -> list[str]:
    from . import backend as backends
    return list(backends.BACKENDS)


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
    size = ap.add_mutually_exclusive_group()
    size.add_argument("--page", default=None, metavar="WxH",
                      help="fixed page in mm, true size, drawing centred")
    size.add_argument("--frame", default=None, metavar="WxH",
                      help="fixed page in mm with the drawing scaled to fill it, "
                           "so the view never moves between rebuilds")
    ap.add_argument("--split", type=int, default=2,
                    help="pieces a span is cut into when it misses the tolerance")
    ap.add_argument("--backend", choices=sorted(backend_names()), default=None,
                    help="geometry backend (default: the compiled library)")
    ap.add_argument("--watch", action="store_true",
                    help="stay running and rebuild when the design file changes")
    ap.add_argument("--seed", choices=sorted(presets.PRESETS), default=None,
                    help="preset to write when --watch starts with no design file")
    ap.add_argument("--reopen", nargs="?", const="Inkscape", default=None,
                    metavar="APP",
                    help="ask this app to reopen the drawing after each rebuild")
    ap.add_argument("--keep-view", action="store_true",
                    help="carry Inkscape's zoom and pan over from the file being replaced")
    ap.add_argument("--quiet", action="store_true", help="write the file, print nothing")
    args = ap.parse_args(argv)

    def size_of(text, flag):
        try:
            w, h = (float(v) for v in text.lower().split("x"))
        except ValueError:
            ap.error(f"{flag} takes WxH in mm, for example 210x148")
        return (w, h)

    page = size_of(args.page, "--page") if args.page else None
    frame = size_of(args.frame, "--frame") if args.frame else None

    if args.watch:
        if not args.design:
            ap.error("--watch needs --design: there must be a file to watch")
        from . import watch as watcher
        return watcher.run(
            args.design,
            args.out or os.path.join("out", "watched.svg"),
            render,
            interval=0.4,
            seed_preset=args.seed,
            reopen_app=args.reopen,
            tol=args.tol,
            width=args.width,
            prec=args.prec,
            margin=args.margin,
            split=args.split,
            backend=args.backend,
            page=page,
            frame=frame,
        )

    design = Design.load(args.design) if args.design else presets.get(args.preset)
    if args.width is not None:
        if args.width <= 0:
            ap.error("--width must be positive")
    if args.split < 2:
        ap.error("--split must be at least 2")
    out_path = args.out or os.path.join("out", f"{design.name.split()[0]}.svg")
    text, info = render(design, tol=args.tol, width=args.width,
                        prec=args.prec, margin=args.margin, split=args.split,
                        backend=args.backend, page=page, frame=frame,
                        view=svg.read_view(out_path) if args.keep_view else None)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    svg.write(out_path, text)

    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        design.save(args.json)

    if not args.quiet:
        print(format_report(info, args.tol))
        print(f"wrote         {out_path}")
    return 0 if info["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
