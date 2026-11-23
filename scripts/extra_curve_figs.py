#!/usr/bin/env python3
"""Draw the named classical curves the collection is missing, one SVG each.

    .venv/bin/python scripts/extra_curve_figs.py

The equations are the generators' own (`scripts/generators.py`, `NAMED`); this script only
samples them and writes a small figure to `app/public/extra-curves/<slug>.svg`, so the
extra-curves page can show what it is proposing without inventing a second definition.
"""

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from fig_sides import side_curves, line_path  # noqa: E402
import generators as G  # noqa: E402

OUT = ROOT / "app" / "public" / "extra-curves"
SIZE = (600, 400)
SAMPLES = 400


def slug(key: str) -> str:
    out = []
    for ch in key.lower():
        out.append(ch if ch.isalnum() else "-")
    return "".join(out).strip("-").replace("--", "-")


def branches(spec):
    data = G.named_data(spec)
    return data["ctrl"]


def points_of(ctrl):
    deg = len(ctrl) - 1
    if len(ctrl[0]) == 2:
        # already a plain Bézier control polygon (x, y)
        out = []
        for i in range(SAMPLES + 1):
            s = Fraction(i, SAMPLES)
            x = sum(Fraction(ctrl[j][0]) * G.bern_n(j, deg, s) for j in range(len(ctrl)))
            y = sum(Fraction(ctrl[j][1]) * G.bern_n(j, deg, s) for j in range(len(ctrl)))
            out.append((float(x), float(y)))
        return out
    pts = []
    for i in range(SAMPLES + 1):
        s = Fraction(i, SAMPLES)
        w = sum(Fraction(p[2]) * G.bern_n(j, deg, s) for j, p in enumerate(ctrl))
        if w == 0:
            pts.append(None)
            continue
        x, y = G.homog_point(ctrl, s)
        pts.append((float(x), float(y)))
    return pts


def figure(key, spec):
    lines = []
    if "branches" not in spec:
        # an n / h / u / v preset: its integer control points are the Bézier form
        built = G.build_preset(spec)
        ctrl_list = [built["cps"]]
    else:
        ctrl_list = branches(spec)
    if not ctrl_list:
        return None
    for ctrl in ctrl_list:
        pts = points_of(ctrl)
        run = []
        for p in pts:
            if p is None:
                if len(run) > 1:
                    lines.append(run)
                run = []
            else:
                run.append(p)
        if len(run) > 1:
            lines.append(run)
    allpts = [p for line in lines for p in line]
    if not allpts:
        return None
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.08 * max(x1 - x0, y1 - y0) or 0.1
    x0, x1 = x0 - pad, x1 + pad
    y0, y1 = y0 - pad, y1 + pad
    w, h = SIZE
    margin = 26
    k = min((w - 2 * margin) / (x1 - x0), (h - 2 * margin - 26) / (y1 - y0))
    ox = (w - (x1 - x0) * k) / 2
    oy = (h - (y1 - y0) * k) / 2

    def put(p):
        # +y is up in the model, so the pixel y is flipped here
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k) - 22

    spine = "".join(line_path(line, put, "#2b2b2b", 2.4) for line in lines)
    # the plate's own side curves, drawn faintly: inside capped, outside at the ask
    sides = ""
    for line in lines:
        if len(line) < 4:
            continue
        left, right = side_curves(line)
        sides += line_path(left, put, "#a06a2c", 1.1) + line_path(right, put, "#a06a2c", 1.1)
    path = sides + spine
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{key}">'
        f'<rect width="{w}" height="{h}" fill="#fff"/>'
        f"{path}"
        f'<text x="{margin}" y="{h - 8}" font-family="ui-monospace, Menlo, monospace" '
        f'font-size="14" fill="#5a4a36">{key}</text>'
        "</svg>\n"
    )


def main():
    import json

    # the page's own list is the authority: draw exactly the keys it proposes
    page = json.loads((ROOT / "app" / "src" / "data" / "extra-curves.json").read_text())
    wanted = [row["key"] for row in page["missingNamed"]]
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    # NAMED holds the equations with branches; PRESETS holds the ones written as n / h / u / v
    # (quartic, sextic); named_data builds both.
    for spec in list(G.NAMED) + list(getattr(G, "PRESETS", [])):
        key = spec["key"]
        if key not in wanted:
            continue
        svg = figure(key, spec)
        if not svg:
            print(f"  {key}: no drawable branch")
            continue
        (OUT / f"{slug(key)}.svg").write_text(svg)
        written += 1
    size = sum((OUT / f).stat().st_size for f in OUT.iterdir() if f.suffix == ".svg")
    print(f"{written} figures -> {OUT.relative_to(ROOT)} ({size // 1024} KB)")


if __name__ == "__main__":
    main()
