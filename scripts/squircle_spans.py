#!/usr/bin/env python3
"""The squircle as Bézier spans: 4 (one per quadrant) and 8 (two per quadrant).

    .venv/bin/python scripts/squircle_spans.py

The squircle |x|⁴ + |y|⁴ = 1 has no rational parametrisation. Cutting it into spans does not
make it exact; it makes it *exportable*. Each span is a cubic with its end points and end
tangents taken from the curve itself and its two handle lengths solved by least squares; the
figure prints the worst distance from the true curve to the fitted spans, in percent of the
radius. A miss is stated, never hidden.
"""

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "public" / "extra-curves"
SIZE = (600, 400)


def squircle_quarter(n=4000):
    x = np.linspace(1.0, 0.0, n)
    y = (1 - x ** 4) ** 0.25
    return np.stack([x, y], axis=1)


def fit_span(points):
    """A cubic through the span's ends: end tangents, handle length searched for the least miss.

    A least-squares solve for the two handles was tried first and gave a worse curve (4.5 % on
    a quadrant against 0.85 %), because the two handles are not independent enough for the
    normal equations to be well posed. The one-parameter search is honest about that: the same
    length on both handles, chosen by measurement.
    """
    p0, p3 = points[0], points[-1]
    t0 = points[1] - points[0]
    t0 = t0 / np.linalg.norm(t0)
    t1 = points[-2] - points[-1]
    t1 = t1 / np.linalg.norm(t1)
    chord = float(np.linalg.norm(p3 - p0))
    best = (1e9, None)
    for k in np.linspace(0.2, 1.4, 121):
        handle = k * chord
        ctrl = np.stack([p0, p0 + handle * t0, p3 + handle * t1, p3])
        miss = worst_miss(points, ctrl)
        if miss < best[0]:
            best = (miss, ctrl)
    return best[1]


def bezier(ctrl, n=900):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = ctrl
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * (t ** 2) * p2 + (t ** 3) * p3


def worst_miss(segment, ctrl):
    curve = bezier(ctrl)
    d = np.sqrt(((segment[:, None, :] - curve[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    return float(d.max())


def span_figure(name, spans_per_quarter, quarter):
    spans = []
    for k in range(spans_per_quarter):
        lo = int(len(quarter) * k / spans_per_quarter)
        hi = int(len(quarter) * (k + 1) / spans_per_quarter) - 1
        segment = quarter[lo:hi + 1]
        ctrl = fit_span(segment)
        # mirror this quarter into the other three
        for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            spans.append((ctrl * np.array([sx, sy]), worst_miss(segment, ctrl)))
    miss = max(m for _, m in spans)
    # one path per span: joining them in sequence would draw chords across the shape
    return draw(name, [bezier(ctrl) for ctrl, _ in spans],
                f"fitted · {4 * spans_per_quarter} spans · worst miss {miss * 100:.2f} % of the radius"), miss


def draw(name, lines, note):
    pts = np.concatenate(lines)
    x0, x1 = pts[:, 0].min(), pts[:, 0].max()
    y0, y1 = pts[:, 1].min(), pts[:, 1].max()
    pad = 0.08 * max(x1 - x0, y1 - y0)
    x0, x1, y0, y1 = x0 - pad, x1 + pad, y0 - pad, y1 + pad
    w, h = SIZE
    margin = 26
    k = min((w - 2 * margin) / (x1 - x0), (h - 2 * margin - 26) / (y1 - y0))
    ox = (w - (x1 - x0) * k) / 2
    oy = (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k) - 22

    path = "".join(
        '<path d="M ' + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in line) + '" '
        'fill="none" stroke="#2b2b2b" stroke-width="2.4" stroke-linecap="round" '
        'stroke-linejoin="round"/>'
        for line in lines
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{name}">'
        f'<rect width="{w}" height="{h}" fill="#fff"/>'
        f"{path}"
        f'<text x="{margin}" y="{h - 8}" font-family="ui-monospace, Menlo, monospace" '
        f'font-size="14" fill="#5a4a36">{name}</text>'
        f'<text x="{margin}" y="20" font-family="ui-monospace, Menlo, monospace" '
        f'font-size="12" fill="#8a7a62">{note}</text>'
        "</svg>\n"
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    quarter = squircle_quarter()
    for count, slug in ((1, "squircle-4-span"), (2, "squircle-8-span")):
        svg, miss = span_figure("squircle", count, quarter)
        (OUT / f"{slug}.svg").write_text(svg)
        print(f"{slug}.svg  worst miss {miss * 100:.2f} % of the radius")


if __name__ == "__main__":
    main()
