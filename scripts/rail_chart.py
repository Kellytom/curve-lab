"""A labelled SVG chart for the rail pages.

The house figure rules: a title inside the figure, axis names, ticks with
numbers, a legend, the key coordinates written on the figure, and +y up in the
rendered result. SVG is y-down, so the mapping flips it once at output.

    from rail_chart import chart, INK, BLUE, RED, GOLD, MUTED, PAPER, GRID, LINE
    svg = chart(items, 900, 580, title, subtitle, "x (units)", "y (units)")

`items` is `(points, colour, width, dash, legend label)`. One implementation for
every rail page; do not copy this code into a generator.

This is the Python chart for the Python-generated pages. When a rail page moves
to JavaScript, its chart moves with it; there is no cross-language sharing of
layout.
"""

from __future__ import annotations

import math

from grid_view import nice_step

INK, BLUE, RED, GOLD, MUTED = "#2e2413", "#1f5fa8", "#a23b2a", "#b58312", "#7b6c4e"
PAPER, GRID, LINE = "#fffdf7", "#e4dcc6", "#d8ccae"


def _format_number(value, step):
    text = f"{value:.3f}" if step < 0.1 else f"{value:.2f}"
    return text.rstrip("0").rstrip(".")


def chart(items, w, h, title, subtitle, xlabel, ylabel, marks=(),
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
