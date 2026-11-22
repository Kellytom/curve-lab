#!/usr/bin/env python3
"""The two classical curves that are not rational, drawn as sampled outlines.

    .venv/bin/python scripts/extra_curve_figs.py

The heart, (x² + y² − 1)³ = x² y³, has no rational parametrisation (genus 4, three cusps).
There is no exact point set to store, so this script solves the equation numerically — for
each y it solves the cubic in s = x², keeps the real roots s ≥ 0 and mirrors x = ±√s — and
writes a figure that says **sampled** inside it. Same for the squircle, |x|⁴ + |y|⁴ = 1.

Nothing here claims exactness, and nothing here writes a record: the figure is a picture of
the equation, not a curve for the collection.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "public" / "extra-curves"
SIZE = (600, 400)


def cubic_roots_nonneg(c, rhs_coeff):
    """roots s >= 0 of (s + c)^3 = s * rhs_coeff, by scanning and bisection."""
    def f(s):
        return (s + c) ** 3 - s * rhs_coeff
    roots = []
    steps = 800
    lo, hi = 0.0, 6.0
    prev_s = lo
    prev = f(prev_s)
    for i in range(1, steps + 1):
        s = lo + (hi - lo) * i / steps
        value = f(s)
        if prev == 0:
            roots.append(prev_s)
        elif prev * value < 0:
            a, b = prev_s, s
            for _ in range(60):
                m = (a + b) / 2
                if f(a) * f(m) <= 0:
                    b = m
                else:
                    a = m
            roots.append((a + b) / 2)
        prev_s, prev = s, value
    return [r for r in roots if r >= -1e-12]


def heart_points(samples=900):
    """The heart as one closed loop: solve s = x² at each y, collect both sides, then order
    the points by angle about the centroid so the outline is traced, not zig-zagged."""
    y_lo, y_hi = -1.05, 1.12
    pts = []
    for i in range(samples + 1):
        y = y_lo + (y_hi - y_lo) * i / samples
        c = y * y - 1
        for s in cubic_roots_nonneg(c, y ** 3):
            x = s ** 0.5
            if x > 1e-9:
                pts.append((x, y))
                pts.append((-x, y))
    # the top and bottom points on the axis close the loop
    for y in (y_lo, y_hi):
        c = y * y - 1
        if any(abs(s) < 1e-12 for s in cubic_roots_nonneg(c, y ** 3)):
            pts.append((0.0, y))
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    import math
    pts.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    pts.append(pts[0])
    return [pts]


def squircle_points(samples=1200):
    """|x|^4 + |y|^4 = 1, the two branches y = ±(1 − |x|^4)^(1/4)."""
    top, bottom = [], []
    for i in range(samples + 1):
        x = -1 + 2 * i / samples
        y = (max(0.0, 1 - abs(x) ** 4)) ** 0.25
        top.append((x, y))
        bottom.append((x, -y))
    return [top, bottom]


def svg_for(name, lines, note):
    pts = [p for line in lines for p in line]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.08 * max(x1 - x0, y1 - y0)
    x0, x1, y0, y1 = x0 - pad, x1 + pad, y0 - pad, y1 + pad
    w, h = SIZE
    margin = 26
    k = min((w - 2 * margin) / (x1 - x0), (h - 2 * margin - 26) / (y1 - y0))
    ox = (w - (x1 - x0) * k) / 2
    oy = (h - (y1 - y0) * k) / 2

    def put(p):
        # +y is up in the model, so the pixel y is flipped here
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k) - 22

    path = "".join(
        '<path d="M ' + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in line) + '" '
        'fill="none" stroke="#2b2b2b" stroke-width="2.4" stroke-linecap="round" '
        'stroke-linejoin="round"/>'
        for line in lines if len(line) > 1
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{name}, sampled">'
        f'<rect width="{w}" height="{h}" fill="#fff"/>'
        f"{path}"
        f'<text x="{margin}" y="{h - 8}" font-family="ui-monospace, Menlo, monospace" '
        f'font-size="14" fill="#5a4a36">{name} · sampled</text>'
        f'<text x="{margin}" y="20" font-family="ui-monospace, Menlo, monospace" '
        f'font-size="12" fill="#8a7a62">{note}</text>'
        "</svg>\n"
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    heart = heart_points()
    if heart[0]:
        (OUT / "heart.svg").write_text(
            svg_for("heart", heart, "(x² + y² − 1)³ = x²y³ · genus 4, three cusps"))
        written += 1
    else:
        print("heart: no roots found")
    squircle = squircle_points()
    (OUT / "squircle.svg").write_text(
        svg_for("squircle", squircle, "|x|⁴ + |y|⁴ = 1 · the rounded square"))
    written += 1
    print(f"{written} sampled figure(s) -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
