"""Draw a curve's loop view from its flat spots, not from the expanded row.

    .venv/bin/python scripts/curve_svg.py curves/<slug>/curve.json [out.svg]

Why this exists: the page draws from the speed row, and for a row whose coefficients run
to 10^8 the difference p^2 - q^2 loses its low bits to cancellation — the picture comes
out as a flat line. The same curve written as a product of (t - r) factors has no such
cancellation: q is a product, p is a constant, and the integral is evaluated from those.

The output is an SVG, drawn to the figure rules in AGENTS.md: a figure number and title
inside the figure, axis labels, a legend, and the key numbers. Rasterise it with
`node scripts/svg_png.mjs in.svg out.png 900`.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 900, 560
PAD_LEFT, PAD_RIGHT, PAD_TOP, PAD_BOTTOM = 78, 40, 64, 76


def spots_of(record):
    text = record.get("roots") or ""
    return [F(part.strip()) for part in text.split(",") if part.strip()]


def curve_points(record, samples=1400, balance=None):
    """z(t) = integral of w^2, in exact fractions.

    Both rows come from the record when it has them, so the picture is the record's curve and
    not an approximation of it. Only when a record carries flat spots and no rows is q built
    from the roots — the census convention, p = 1 — and the figure says which p it used.

    This was wrong until 2026-11-16: it always used p = 1 and ignored the record's x row, so
    an imported curve came out as a straight sliver — "you are only making 1/2 the curve".
    """
    speed_x = record.get("speedX") or []
    speed_y = record.get("speedY") or []
    spots = spots_of(record)

    if speed_x and speed_y:
        p_row = [F(str(value)) for value in speed_x]
        q_row = [F(str(value)) for value in speed_y]
        source = "the record's two rows, exact"
    elif spots:
        q_row = [F(1)]
        for root in spots:
            nxt = [F(0)] * (len(q_row) + 1)
            for power, value in enumerate(q_row):
                nxt[power] += -root * value
                nxt[power + 1] += value
            q_row = nxt
        p_row = [F(1)]
        source = "the flat spots, with p = 1 (the census convention)"
    else:
        return None

    def at(row, t):
        total = F(0)
        power = F(1)
        for coefficient in row:
            total += coefficient * power
            power *= t
        return total

    points = []
    x = y = F(0)
    step = F(1, samples)
    for i in range(samples + 1):
        points.append((float(x), float(y)))
        if i < samples:
            tm = F(i, samples) + step / 2
            p_m, q_m = at(p_row, tm), at(q_row, tm)
            x += (p_m * p_m - q_m * q_m) * step
            y += 2 * p_m * q_m * step
    curve_points.source = source
    return points


def exaggerate(points, factor):
    """Stretch y for the picture only, and say so on it.

    These rows make curves that hug the x axis: q is odd about 1/2, so the vertical
    excursion cancels almost completely and the stroke is a sliver a hundredth of its own
    length deep. No renderer fixes that; the honest picture stretches y and labels it.
    """
    if not factor or factor == 1:
        return points
    return [(x, y * factor) for x, y in points]


def frame_of(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    pad_x = (max(xs) - min(xs)) * 0.15 or 1.0
    pad_y = (max(ys) - min(ys)) * 0.15 or 1.0
    return min(xs) - pad_x, max(xs) + pad_x, min(ys) - pad_y, max(ys) + pad_y


def svg_for(record, number=1):
    figure = record.get("figure", {})
    base = curve_points(record)
    aspect = figure.get("aspect", 1)
    if aspect == "auto":
        # enough stretch to make the curve about twice as long as it is deep
        xs = [p[0] for p in base]
        ys = [p[1] for p in base]
        span_x = max(xs) - min(xs)
        span_y = max(ys) - min(ys)
        aspect = round(min(50000, max(1, (span_x / span_y) / 2))) if span_y > 0 else 1
    points = exaggerate(base, aspect)
    if not points:
        return None
    min_x, max_x, min_y, max_y = frame_of(points)
    inner_w = WIDTH - PAD_LEFT - PAD_RIGHT
    inner_h = HEIGHT - PAD_TOP - PAD_BOTTOM
    scale = min(inner_w / (max_x - min_x), inner_h / (max_y - min_y))
    ox = PAD_LEFT + (inner_w - (max_x - min_x) * scale) / 2
    oy = PAD_TOP + (inner_h - (max_y - min_y) * scale) / 2
    fx = lambda v: ox + (v - min_x) * scale
    fy = lambda v: oy + (max_y - v) * scale
    path = "M" + "L".join(f"{fx(x):.1f},{fy(y):.1f}" for x, y in points)
    name = record.get("name", "curve")
    balance = record.get("figure", {}).get("balance", None)
    aspect_label = "" if aspect in (1, None) else f" &middot; y stretched {aspect:,}x to be seen"
    p_label = getattr(curve_points, "source", "the record's rows")
    crossings = record.get("crossings", "?")
    grid = record.get("grid", "?")
    spots = record.get("roots", "")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect width="{WIDTH}" height="{HEIGHT}" fill="#fbf7ec"/>
  <text x="{PAD_LEFT}" y="28" font-family="Georgia, serif" font-size="16" font-weight="600" fill="#2e2413">Fig. {number} &middot; {name}</text>
  <text x="{PAD_LEFT}" y="48" font-family="ui-monospace, Menlo, monospace" font-size="11" fill="#7b6c4e">flat spots {spots} &middot; {crossings} crossings &middot; grid 1/{grid} &middot; drawn from the factored form &middot; {p_label}{aspect_label}</text>
  <line x1="{PAD_LEFT}" y1="{fy(0):.1f}" x2="{WIDTH - PAD_RIGHT}" y2="{fy(0):.1f}" stroke="#c9bfa6" stroke-dasharray="3 5"/>
  <line x1="{fx(0):.1f}" y1="{PAD_TOP}" x2="{fx(0):.1f}" y2="{HEIGHT - PAD_BOTTOM}" stroke="#c9bfa6" stroke-dasharray="3 5"/>
  <path d="{path}" fill="none" stroke="#2e2413" stroke-width="1.8" stroke-linejoin="round"/>
  <text x="{WIDTH / 2:.0f}" y="{HEIGHT - 34}" text-anchor="middle" font-family="Georgia, serif" font-size="13" fill="#2e2413">x</text>
  <text x="30" y="{HEIGHT / 2:.0f}" text-anchor="middle" font-family="Georgia, serif" font-size="13" fill="#2e2413" transform="rotate(-90 30 {HEIGHT / 2:.0f})">y</text>
  <text x="{PAD_LEFT}" y="{HEIGHT - 14}" font-family="ui-monospace, Menlo, monospace" font-size="11" fill="#7b6c4e">black: the spine, z(t) = integral of w^2 &middot; dashed: x = 0 and y = 0 &middot; axes in curve units, y up</text>
</svg>
"""


def main():
    record_path = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else record_path.with_name("figure-exact.svg")
    record = json.loads(record_path.read_text())
    svg = svg_for(record)
    if svg is None:
        print("no flat spots in the record; nothing drawn")
        return
    out.write_text(svg)
    print(out, len(svg), "bytes")


if __name__ == "__main__":
    main()
