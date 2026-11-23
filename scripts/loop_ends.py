"""Loop-end curves: a Tschirnhausen-style tail that ends in a loop, at several loop sizes.

    .venv/bin/python scripts/loop_ends.py

These are the curves to append to a leg. The family is x = t² − c, y = t(t² − c): the loop
sits between t = −√c and t = +√c, so c sets the loop's size while the tail stays the same
shape. The figure set shows three sizes and the mirror; the page's slider rotates any of them
to the leg's angle, because a rotation cannot change a tangent's length, only its direction.

Nothing is stored: the slider's curve is drawn in the browser from the same formula.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from fig_sides import side_curves, line_path  # noqa: E402

OUT = ROOT / "app" / "public" / "extra-curves"
SIZE = (600, 400)
T_LO, T_HI = -2.4, 2.4
SAMPLES = 500


def loop_points(c, t_lo=T_LO, t_hi=T_HI):
    pts = []
    for i in range(SAMPLES + 1):
        t = t_lo + (t_hi - t_lo) * i / SAMPLES
        pts.append((t * t - c, t * (t * t - c)))
    return pts


def figure(name, points, note):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.10 * max(x1 - x0, y1 - y0)
    x0, x1, y0, y1 = x0 - pad, x1 + pad, y0 - pad, y1 + pad
    w, h = SIZE
    margin = 26
    k = min((w - 2 * margin) / (x1 - x0), (h - 2 * margin - 26) / (y1 - y0))
    ox = (w - (x1 - x0) * k) / 2
    oy = (h - (y1 - y0) * k) / 2

    def put(p):
        # +y is up in the model; the pixel y is flipped here
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k) - 22

    left, right = side_curves(points, width_percent=2.0)
    body = (line_path(left, put, "#a06a2c", 1.1) + line_path(right, put, "#a06a2c", 1.1) +
            line_path(points, put, "#2b2b2b", 2.4))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{name}">'
        f'<rect width="{w}" height="{h}" fill="#fff"/>{body}'
        f'<text x="{margin}" y="{h - 8}" font-family="ui-monospace, Menlo, monospace" '
        f'font-size="14" fill="#5a4a36">{name}</text>'
        f'<text x="{margin}" y="20" font-family="ui-monospace, Menlo, monospace" '
        f'font-size="12" fill="#8a7a62">{note}</text>'
        "</svg>\n"
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    variants = [
        ("loop-end-small", 1.5, "x = t² − 1.5, y = t(t² − 1.5) · a tight loop"),
        ("loop-end", 3.0, "x = t² − 3, y = t(t² − 3) · the Tschirnhausen loop"),
        ("loop-end-large", 6.0, "x = t² − 6, y = t(t² − 6) · a wide loop"),
        ("loop-end-mirror", 3.0, "the Tschirnhausen loop mirrored across x = 0"),
    ]
    for name, c, note in variants:
        pts = loop_points(c)
        if "mirror" in name:
            pts = [(-x, y) for x, y in pts]
        (OUT / f"{name}.svg").write_text(figure(name, pts, note))
        print(f"{name}.svg")


if __name__ == "__main__":
    main()
