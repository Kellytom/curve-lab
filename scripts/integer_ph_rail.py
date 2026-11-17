"""The integer PH curve's exact rail, and the grid where the lattice begins.

    .venv/bin/python scripts/integer_ph_rail.py

`integer-105` is written by a speed pair, so it is a Pythagorean-hodograph
curve: its speed is a polynomial and its offset is a ratio of two polynomials.
The rail on this page is therefore exact, drawn from exact rational points. No
cubic is drawn: a cubic chain is the export step, not the working form. The
Levien fit is measured for comparison and printed as a number, because the
number is the honest cost of the fitted tier.

The lattice section is the part that decides whether branches can sit at
precise points: the pitch, the first interior lattice hit, the scale that
carries it, and the same question for the two rails. The midpoint's mirror
station is included with its translated coordinates, and with the measured
reason the vertical line through it does not bisect the curve.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import septic_curves  # noqa: E402
from curve_lab import measure  # noqa: E402
from curve_lab import ph_offset as ph  # noqa: E402
from curve_lab.parallel_bezier import fit_offset  # noqa: E402
from grid_view import nice_step  # noqa: E402

NAME = "integer-105"
D = Fraction(41, 1120)          # 0.0366 model units, 41/1120 of the half-width
PLAIN_D = Fraction(3, 100)      # the contrast: an unchosen distance
FIT_TOL = 1e-5

INK, BLUE, RED, GOLD, MUTED = "#2e2413", "#1f5fa8", "#a23b2a", "#b58312", "#7b6c4e"
PAPER, GRID, LINE = "#fffdf7", "#e4dcc6", "#d8ccae"


# -- the source --------------------------------------------------------------

def _speeds():
    """The curve's speed pair, from the one table that owns the named curves."""
    for name, speed_x, speed_y in septic_curves.CURVES:
        if name == NAME:
            return [Fraction(value) for value in speed_x], \
                [Fraction(value) for value in speed_y]
    raise KeyError(f"{NAME} is not in scripts/septic_curves.CURVES")


def _curve_point(t):
    u, v = _speeds()
    return ph.point_at(u, v, 0, t)


def _ladder(u, v):
    """The scale at which each new interior parameter first lands, q <= 24."""
    rows = {}
    for q in range(2, 25):
        for k in range(1, q):
            if gcd(k, q) != 1:
                continue
            t = Fraction(k, q)
            rows.setdefault(ph.lattice_scale(ph.point_at(u, v, 0, t)),
                            []).append(t)
    return [(scale, rows[scale]) for scale in sorted(rows)]


def _symmetry(u, v):
    """How far the curve is from a half turn and from a vertical mirror."""
    size = _size(u, v)
    central = 0.0
    vertical = 0.0
    half = Fraction(1, 2)
    middle = ph.point_at(u, v, 0, half)
    for s in (Fraction(1, 10), Fraction(1, 4), Fraction(3, 10), Fraction(2, 5)):
        ahead = ph.point_at(u, v, 0, half + s)
        behind = ph.point_at(u, v, 0, half - s)
        central = max(central, float(max(
            abs(ahead[0] + behind[0] - 2 * middle[0]),
            abs(ahead[1] + behind[1] - 2 * middle[1]))))
        vertical = max(vertical, float(max(
            abs(ahead[0] + behind[0] - 2 * middle[0]),
            abs(ahead[1] - behind[1]))))
    return {"central": central / size, "vertical": vertical / size}


def _size(u, v):
    point, _ = ph.float_sampler(u, v, 0)
    xs, ys = [], []
    for i in range(2001):
        x, y = point(i / 2000)
        xs.append(x)
        ys.append(y)
    return math.hypot(max(xs) - min(xs), max(ys) - min(ys))


def _axis_crossings(u, v, shift):
    """Parameters where the translated curve crosses x = 0."""
    x = ph.curve(u, v)[0]

    def value(t):
        total = 0.0
        for coefficient in reversed(x):
            total = total * t + float(coefficient)
        return total + float(shift)

    found = []
    previous = value(0.0)
    for i in range(1, 20001):
        t = i / 20000
        current = value(t)
        if previous == 0.0:
            found.append((i - 1) / 20000)
        elif previous * current < 0:
            low, high = (i - 1) / 20000, t
            for _ in range(60):
                middle = (low + high) / 2
                if value(low) * value(middle) <= 0:
                    high = middle
                else:
                    low = middle
            found.append((low + high) / 2)
        previous = current
    return found


def proof_data():
    u, v = _speeds()
    x, y = ph.curve(u, v)
    sigma = ph.speed_squared(u, v)
    pitch = measure.grid(u, v)
    at_pitch = ph.hits_at_scale(u, v, pitch)
    first = ph.first_interior_hit(u, v, q_max=200)
    scale = first["scale"]
    at_scale = ph.hits_at_scale(u, v, scale)
    rail_first = ph.first_interior_hit(u, v, D, q_max=200)
    plain_first = ph.first_interior_hit(u, v, PLAIN_D, q_max=200)
    size = _size(u, v)
    point, tangent = ph.float_sampler(u, v, D)
    fitted = fit_offset(point, tangent, tol=FIT_TOL)
    kappa = ph.curvature_peak(u, v)

    midpoint = ph.point_at(u, v, 0, Fraction(1, 2))
    shift = -midpoint[0]
    station = []
    for label, distance in (("spine", 0), ("rail +d", D), ("rail -d", -D)):
        at = ph.point_at(u, v, distance, Fraction(1, 2))
        translated = (at[0] + shift, at[1])
        station.append({
            "label": label,
            "model": translated,
            "lattice": (translated[0] * scale, translated[1] * scale),
        })

    angle = math.degrees(tangent(0.5))
    crossings = _axis_crossings(u, v, shift)
    inflection = measure.inflection(u, v)
    return {
        "name": NAME,
        "u": u,
        "v": v,
        "x": x,
        "y": y,
        "sigma": sigma,
        "pitch": pitch,
        "at_pitch": at_pitch,
        "first": first,
        "scale": scale,
        "at_scale": at_scale,
        "rail_first": rail_first,
        "rail_at_scale": ph.hits_at_scale(u, v, scale, D),
        "plain_d": PLAIN_D,
        "plain_first": plain_first,
        "distance": D,
        "size": size,
        "fit": {"spans": len(fitted["spans"]),
                "error": fitted["error_max"],
                "share": fitted["error_max"] / size,
                "drawn": False},
        "fold": float(D) * kappa,
        "min_radius": 1.0 / kappa,
        "midpoint": midpoint,
        "shift": shift,
        "station": station,
        "tangent_deg": angle,
        "off_vertical_deg": abs(angle + 90.0),
        "crossings": crossings,
        "symmetry": _symmetry(u, v),
        "inflection": inflection,
        "ladder": _ladder(u, v)[:7],
    }


# -- the figure --------------------------------------------------------------

def _format_number(value, step):
    text = f"{value:.3f}" if step < 0.1 else f"{value:.2f}"
    return text.rstrip("0").rstrip(".")


def _chart(items, w, h, title, subtitle, xlabel, ylabel, marks=(),
           vertical=None, notes=(), mark_legend=None):
    """A labelled figure. SVG is y-down; the mapping flips it so +y reads up."""
    points = [point for item in items for point in item[0]]
    points += [mark[0] for mark in marks]
    if vertical is not None:
        points += [(vertical[0], min(p[1] for p in points)),
                   (vertical[0], max(p[1] for p in points))]
    x0, x1 = min(p[0] for p in points), max(p[0] for p in points)
    y0, y1 = min(p[1] for p in points), max(p[1] for p in points)
    pad = 0.08
    dx, dy = (x1 - x0) or 1.0, (y1 - y0) or 1.0
    x0, x1 = x0 - pad * dx, x1 + pad * dx
    y0, y1 = y0 - pad * dy, y1 + pad * dy
    left, right, bottom = 66, 18, 96
    top = 64 + 16 * len(notes)
    k = min((w - left - right) / (x1 - x0), (h - top - bottom) / (y1 - y0))
    ox = left + ((w - left - right) - (x1 - x0) * k) / 2
    oy = top + ((h - top - bottom) - (y1 - y0) * k) / 2

    def put(point):
        return ox + (point[0] - x0) * k, h - (oy + (point[1] - y0) * k)

    step = nice_step(max(x1 - x0, y1 - y0), 8)
    body = [f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="{LINE}"/>']
    start = math.ceil(x0 / step) * step
    value = start
    while value <= x1:
        a, b = put((value, y0)), put((value, y1))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                    f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
        label = _format_number(value, step)
        body.append(f'<text x="{a[0]:.1f}" y="{h - bottom + 16:.1f}" '
                    f'font-size="11" text-anchor="middle" fill="{MUTED}">'
                    f'{label}</text>')
        value += step
    value = math.ceil(y0 / step) * step
    while value <= y1:
        a, b = put((x0, value)), put((x1, value))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                    f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
        label = _format_number(value, step)
        body.append(f'<text x="{left - 8:.1f}" y="{a[1] + 4:.1f}" '
                    f'font-size="11" text-anchor="end" fill="{MUTED}">'
                    f'{label}</text>')
        value += step
    if vertical is not None:
        a, b = put((vertical[0], y0)), put((vertical[0], y1))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                    f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{RED}" '
                    f'stroke-width="1.4" stroke-dasharray="6 4"/>')
        body.append(f'<text x="{a[0] + 6:.1f}" y="{top + 12:.1f}" '
                    f'font-size="12" fill="{RED}">{vertical[1]}</text>')
    for points, colour, width, dash, _label in items:
        d = " ".join(f"{put(point)[0]:.1f} {put(point)[1]:.1f}"
                     for point in points)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" '
                    f'stroke-width="{width}" stroke-linecap="round" '
                    f'stroke-linejoin="round"{dash_attr}/>')
    for point, label, off_x, off_y in marks:
        px, py = put(point)
        body.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" '
                    f'fill="{GOLD}" stroke="{INK}" stroke-width="1"/>')
        anchor = "start" if off_x >= 0 else "end"
        body.append(f'<text x="{px + off_x:.1f}" y="{py + off_y:.1f}" '
                    f'font-size="12" text-anchor="{anchor}" fill="{INK}">'
                    f'{label}</text>')
    body.append(f'<text x="{left}" y="26" font-size="17" fill="{INK}">'
                f'{title}</text>')
    body.append(f'<text x="{left}" y="46" font-size="12" fill="{MUTED}">'
                f'{subtitle}</text>')
    for index, note in enumerate(notes):
        body.append(f'<text x="{left}" y="{64 + 16 * index}" font-size="12" '
                    f'fill="{INK}">{note}</text>')
    body.append(f'<text x="{(left + w - right) / 2:.1f}" y="{h - 34}" '
                f'font-size="13" text-anchor="middle" fill="{INK}">'
                f'{xlabel}</text>')
    body.append(f'<text x="18" y="{(top + h - bottom) / 2:.1f}" '
                f'font-size="13" text-anchor="middle" fill="{INK}" '
                f'transform="rotate(-90 18 {(top + h - bottom) / 2:.1f})">'
                f'{ylabel}</text>')
    cursor = left
    for _points, colour, width, dash, label in items:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        body.append(f'<line x1="{cursor}" y1="{h - 14}" '
                    f'x2="{cursor + 22}" y2="{h - 14}" stroke="{colour}" '
                    f'stroke-width="{width}"{dash_attr}/>')
        body.append(f'<text x="{cursor + 28}" y="{h - 10}" font-size="12" '
                    f'fill="{INK}">{label}</text>')
        cursor += 66 + 7 * len(label)
    if mark_legend:
        body.append(f'<circle cx="{cursor + 6}" cy="{h - 14}" r="4" '
                    f'fill="{GOLD}" stroke="{INK}" stroke-width="1"/>')
        body.append(f'<text x="{cursor + 16}" y="{h - 10}" font-size="12" '
                    f'fill="{INK}">{mark_legend}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            + "".join(body) + "</svg>")


def _rail_points(u, v, distance, steps=400, low=0.0, high=1.0):
    point, _ = ph.float_sampler(u, v, distance)
    return [point(low + (high - low) * i / steps) for i in range(steps + 1)]


def _translated(points, shift):
    return [(x + float(shift), y) for x, y in points]


def _formula(poly):
    powers = ["", "t", "t²", "t³", "t⁴", "t⁵", "t⁶", "t⁷"]
    parts = []
    for i, coefficient in enumerate(poly):
        if coefficient == 0:
            continue
        magnitude = (str(abs(coefficient.numerator))
                     if coefficient.denominator == 1
                     else f"{abs(coefficient.numerator)}/{coefficient.denominator}")
        if magnitude == "1" and i:
            magnitude = ""
        sign = "−" if coefficient < 0 else (" + " if parts else "")
        parts.append(f"{sign}{magnitude}{powers[i]}")
    return "".join(parts) or "0"


def main() -> int:
    d = proof_data()
    shift = float(d["shift"])
    spine = _rail_points(d["u"], d["v"], 0)
    upper = _rail_points(d["u"], d["v"], d["distance"])
    lower = _rail_points(d["u"], d["v"], -d["distance"])

    station_grid = d["station"]
    figure_whole = _chart(
        [
            (spine, INK, 2.4, None, "spine · integer-105"),
            (upper, BLUE, 1.6, None, "exact rail, +d"),
            (lower, RED, 1.6, None, "exact rail, −d"),
        ],
        900, 580,
        "Fig. R1 · integer-105 with its exact PH rails",
        f"d = 41/1120 = 0.0366 model units · no cubic drawn · +y up",
        "x (model units)", "y (model units)",
        marks=[(tuple(map(float, d["midpoint"])), "station", 8, -8)],
        notes=[f"grid {d['scale']}: station at "
               f"({d['first']['point'][0] * d['scale']:.0f}, "
               f"{d['first']['point'][1] * d['scale']:.0f}) · the two ends are "
               f"the pitch-{d['pitch']} lattice points"],
        mark_legend=f"lattice point, grid {d['scale']}",
    )

    station_low, station_high = 0.46, 0.54
    zoom_spine = _translated(
        _rail_points(d["u"], d["v"], 0, 200, station_low, station_high), shift)
    zoom_upper = _translated(
        _rail_points(d["u"], d["v"], d["distance"], 200, station_low, station_high),
        shift)
    zoom_lower = _translated(
        _rail_points(d["u"], d["v"], -d["distance"], 200, station_low, station_high),
        shift)
    station_marks = []
    for row, (off_x, off_y) in zip(station_grid,
                                   ((8, -10), (8, 10), (-8, 10))):
        station_marks.append((
            (float(row["model"][0]), float(row["model"][1])),
            row["label"], off_x, off_y,
        ))
    figure_station = _chart(
        [
            (zoom_spine, INK, 2.6, None, "spine"),
            (zoom_upper, BLUE, 1.8, None, "exact rail, +d"),
            (zoom_lower, RED, 1.8, None, "exact rail, −d"),
        ],
        900, 520,
        "Fig. R2 · the branch station, translated so the y axis passes through it",
        f"labels are grid-{d['scale']} integers · spine at x = 0, rails at "
        f"x = ±{abs(station_grid[1]['lattice'][0]):.0f} · +y up",
        "x (model units, translated)", "y (model units)",
        marks=station_marks, vertical=(0.0, "y axis"),
        notes=[f"grid {d['scale']}: "
               + " · ".join(f"{row['label']} ({row['lattice'][0]:.0f}, "
                            f"{row['lattice'][1]:.0f})"
                            for row in station_grid),
               "rail distance d = 41/1120, chosen so this station is whole"],
    )

    translated_spine = _translated(spine, shift)
    figure_axis = _chart(
        [(translated_spine, INK, 2.4, None, "integer-105, translated")],
        900, 500,
        "Fig. R3 · the same y axis meets the curve four times",
        "so the line through the midpoint is a station, not a mirror line · +y up",
        "x (model units, translated)", "y (model units)",
        marks=[((0.0, float(d["midpoint"][1])), "midpoint", 8, -8)],
        vertical=(0.0, "y axis"),
        notes=[f"grid {d['scale']}: the midpoint is (0, "
               f"{d['station'][0]['lattice'][1]:.0f}) after translating by "
               f"+{d['shift']}"],
    )

    ladder_rows = "".join(
        f"<tr><td>{scale:,}</td><td>{', '.join(str(t) for t in parameters)}</td></tr>"
        for scale, parameters in d["ladder"])

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{d['name']}: the exact PH rail and the lattice grid</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1020px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.panel{{background:{PAPER};border:1px solid {LINE};padding:16px 18px;margin:0 0 18px}}
.art{{background:{PAPER};border:1px solid {LINE};padding:8px;margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
table{{border-collapse:collapse;width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;margin:8px 0 0}}
td,th{{border-bottom:1px solid {LINE};padding:5px 8px;text-align:left;vertical-align:top}}
th{{color:{MUTED};font-weight:600}}
code{{font:12px ui-monospace,Menlo,monospace}}
.warn{{border-left:4px solid {RED};padding-left:12px}}
</style></head><body><main>
<h1>The integer PH curve and its exact rail</h1>
<p class="lead">{d['name']} is PH by construction, so its rail is a ratio of two
polynomials — not a fitted cubic. The cubic fit is computed and printed as a
number; nothing cubic is drawn, because cubics are the export step.</p>

<div class="panel">
<p><strong>The source.</strong> The curve is written by the speed pair</p>
<p><code>u(t) = {_formula(d['u'])}</code><br>
<code>v(t) = {_formula(d['v'])}</code></p>
<p>and the curve is <code>C(t) = ∫(u² − v², 2uv) dt</code>, with
<code>C(0) = (0, 0)</code>. Both coordinates are polynomials:</p>
<p><code>x(t) = {_formula(d['x'])}</code><br>
<code>y(t) = {_formula(d['y'])}</code><br>
<code>σ(t) = u² + v² = {_formula(d['sigma'])}</code></p>
<p>The pitch is <strong>{d['pitch']}</strong>: at that scale the eight position
control points are whole numbers. It is the small grid the curve is written on,
and it is not the grid its lattice points live on.</p>
</div>

<div class="art">{figure_whole}</div>

<h2>The rail is exact</h2>
<div class="panel">
<p><strong>The form.</strong> Because the speed σ is a polynomial, the unit
normal is rational and the rail at signed distance d is</p>
<p><code>O(t) = C(t) + d·(−y'(t), x'(t)) / σ(t)</code></p>
<p>— a ratio of two exact polynomials, with no square root left in it. The page
draws both rails at <strong>d = 41/1120 = {float(d['distance']):.4f}</strong>
model units from exact rational points. The distance is chosen for the lattice
station below, not for looks: it is 1.8% of the curve size, and
<code>|d·κ| ≤ {d['fold']:.3f}</code> against the closest radius
{d['min_radius']:.4f}, so neither rail folds.</p>
<p><strong>The fit, as a number.</strong> A cubic chain fitted to the same
exact rail needs <strong>{d['fit']['spans']} spans</strong> to reach
{d['fit']['error']:.2e}, which is <strong>{d['fit']['share']:.2e} of the
curve size</strong> ({d['size']:.3f} model units, the bounding-box diagonal).
It is not drawn. The exact rail costs one rational expression; the cubic
version costs {d['fit']['spans']} spans and still misses.</p>
</div>

<h2>The lattice: where the hits begin</h2>
<div class="panel">
<p><strong>The spine.</strong> At its own pitch {d['pitch']} the curve has
exactly <strong>{len(d['at_pitch'])}</strong> lattice points — the two ends
{d['at_pitch'][0]['point']} and {d['at_pitch'][-1]['point']} at scale
{d['pitch']}. A search of every rational parameter t = k/q up to q = 200 finds
no smaller interior hit.</p>
<p>The first interior hit is at <strong>t = {d['first']['t'][0]}/{d['first']['t'][1]}</strong>,
the midpoint, and it needs <strong>grid {d['scale']}</strong> — 32 times the
pitch. At that scale the spine has <strong>{len(d['at_scale'])}</strong>
points:</p>
<table>
<tr><th>point at grid {d['scale']}</th><th>parameter</th></tr>
{''.join(f"<tr><td>{row['point']}</td><td>t = {row['t']}</td></tr>" for row in d['at_scale'])}
</table>
<p>Further stations cost more, one at a time:</p>
<table>
<tr><th>grid</th><th>new parameters</th></tr>
{ladder_rows}
</table>
</div>

<h2>The mirror station</h2>
<div class="panel">
<p><strong>Where it is.</strong> The midpoint is
<code>C(1/2) = ({d['midpoint'][0]}, {d['midpoint'][1]})</code>
= ({float(d['midpoint'][0]):.4f}, {float(d['midpoint'][1]):.4f}). At grid
{d['scale']} it is the integer point
({d['first']['point'][0] * d['scale']:.0f}, {d['first']['point'][1] * d['scale']:.0f}).
Translating the curve by <code>+{d['shift']}</code> puts it exactly on the y
axis at <strong>(0, {d['station'][0]['lattice'][1]:.0f})</strong>. The two exact
rails land on the same grid at the same station:</p>
<table>
<tr><th>curve</th><th>point at grid {d['scale']}</th></tr>
{''.join(f"<tr><td>{row['label']}</td><td>({row['lattice'][0]:.0f}, {row['lattice'][1]:.0f})</td></tr>" for row in d['station'])}
</table>
<p>So the station is one grid where the spine and both rails are whole-number
points, and the spine's point sits on the y axis after one integer translation.
That is the precise branch station this curve can give.</p>
<p class="warn"><strong>But the y axis does not bisect it.</strong> Measured:
the curve is not symmetric about the midpoint (half-turn gap
{d['symmetry']['central'] * 100:.0f}% of the size, vertical-mirror gap
{d['symmetry']['vertical'] * 100:.0f}%); the tangent at the station is
{d['tangent_deg']:.1f}°, which is {d['off_vertical_deg']:.1f}° off vertical; the
inflection is at t = {d['inflection']:.4f}, not 1/2; and the line x = 0 meets
the curve at four parameters ({', '.join(f'{t:.4f}' for t in d['crossings'])}).
It is a station on the centreline, not a mirror line.</p>
<p>A true mirror axis needs a symmetric curve. The Pythagorean integer cubic
family is half-turn symmetric with its midpoint at (c, 0) — a lattice point at
scale 1, at its inflection, with a horizontal tangent there — but it is not PH,
so its rail is fitted, not exact. A symmetric PH curve is the third option and
is not built.</p>
</div>

<div class="art">{figure_station}</div>

<h2>What this means for branches</h2>
<div class="panel">
<p><strong>On the spine.</strong> At grid {d['scale']} there is exactly one
interior station, the midpoint. Branches that need several precise points need
a larger grid ({d['ladder'][1][0]:,} gives t = 1/3, {d['ladder'][2][0]:,} gives
t = 2/3) or a different curve.</p>
<p><strong>On the rails.</strong> A rail shares this station only because d was
chosen for it. The first hit of the rail at the unchosen distance
{d['plain_d']} = {float(d['plain_d']):.3f} needs grid
<strong>{d['plain_first']['scale']:,}</strong>. The rule is arithmetic: the
rail's normal at the station is (40/41, −9/41), so d must carry the factor 41
to land on the grid. A rail at an arbitrary distance does not hit the lattice
at any usable scale.</p>
<p><strong>Side curves that are not rails.</strong> A branch is its own curve,
not a parallel offset, so it is not bound by the spine's normal: build it with
whole-number data on the grid you need and it can hit the lattice by
construction. The rails are the only side curves where the hit is dictated by
the parent.</p>
</div>

<div class="art">{figure_axis}</div>

<div class="panel">
<p><strong>Re-derive.</strong>
<code>python scripts/integer_ph_rail.py</code> ·
<code>python -m unittest tests.test_integer_ph_rail</code></p>
<p>Exactness is checked by the normal equations in the test, in
<code>Fraction</code>: the offset is perpendicular to the tangent and exactly
d from the spine. Every lattice number is exact; the fit error alone is a
float.</p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "integer-ph-rail.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"pitch {d['pitch']}, first interior grid {d['scale']} at t={d['first']['t']}")
    print(f"rail first grid {d['rail_first']['scale']}, plain d first grid {d['plain_first']['scale']}")
    print(f"fit {d['fit']['spans']} spans, error {d['fit']['error']:.2e} "
          f"({d['fit']['share']:.2e} of size)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
