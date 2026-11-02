"""Hearts from one Euler arc: rotate to tangency, mirror, cut on the lattice.

    .venv/bin/python scripts/hearts.py
    open workbench/hearts.html

The construction, in the order the pieces were found:

1.  A unit clothoid starts at the origin with its tangent along +x, and its
    heading is quadratic in arc length: theta(s) = s^2 / 2.
2.  Rotate the whole arc about the origin.  At one particular rotation the arc
    comes back and *touches* the y axis -- vertical tangent, zero distance.
    The origin is already on that axis, so the arc now has both ends on it:
    one at the bottom, one at the top where it only kisses it.
3.  Mirror about the y axis.  The two arcs share the origin and meet at the
    top -- a heart, with the cleft being the tangency.
4.  Carry the arc a little past the tangency, to the next lattice point, and
    the halves cross instead of meeting.  That crossing is the extra.

Nothing here is forced onto integers except the final cut, and where that cut
lands is reported in grid units so the price is visible.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generators as G  # noqa: E402
import euler_match as E  # noqa: E402

INK, GOLD, DOT = "#2e2413", "#c9a441", "#b23a2b"
GRID, LINE, MUTED = "#ece4cf", "#d8ccae", "#7b6c4e"

N = 4000
TURNS = 2.0
S_MAX = math.sqrt(4 * math.pi * TURNS)     # theta = s^2/2, so 2*pi*turns


def clothoid(s_max=S_MAX, n=N):
    ds = s_max / n
    x = y = 0.0
    out = [(0.0, 0.0, 0.0)]
    for i in range(1, n + 1):
        s = i * ds
        x += math.cos(s * s / 2) * ds
        y += math.sin(s * s / 2) * ds
        out.append((s, x, y))
    return out


def rotate(p, phi):
    c, s = math.cos(phi), math.sin(phi)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def tangencies(pts):
    """(s, phi) where a rotation by phi makes the arc touch x = 0.

    After rotating by phi the tangent at s points along theta(s) + phi, so it is
    vertical exactly when phi = pi/2 - theta(s).  The touch distance at that
    rotation is the rotated x.
    """
    out = []
    prev = None
    for s, x, y in pts:
        phi = math.pi / 2 - s * s / 2
        d = x * math.cos(phi) - y * math.sin(phi)
        if prev is not None and prev[1] * d < 0:
            a, b = prev[0], s
            for _ in range(60):
                m = (a + b) / 2
                mm = m * m / 2
                xm = _interp(pts, m)[1]
                ym = _interp(pts, m)[2]
                ph = math.pi / 2 - mm
                dm = xm * math.cos(ph) - ym * math.sin(ph)
                if d * dm > 0:
                    b = m
                else:
                    a = m
            s0 = (a + b) / 2
            out.append((s0, math.pi / 2 - s0 * s0 / 2))
        prev = (s, d)
    return out


def _interp(pts, s):
    i = min(len(pts) - 1, max(0, int(s / S_MAX * (len(pts) - 1))))
    return pts[i]


def next_lattice(pts, s_from, phi, scale, tol=0.5):
    """First s past the tangency whose rotated point is closest to a node."""
    best = None
    for s, x, y in pts:
        if s <= s_from:
            continue
        rx, ry = rotate((x, y), phi)
        fx, fy = round(rx * scale), round(ry * scale)
        d = math.hypot(rx - fx / scale, ry - fy / scale)
        if d <= tol / scale:
            snapped = (fx / scale, fy / scale)
            return s, (rx, ry), snapped, d
        if best is None or d < best[3]:
            best = (s, (rx, ry), (round(rx * scale) / scale,
                                  round(ry * scale) / scale), d)
    return best


def arc_between(pts, s0, s1):
    return [(x, y) for s, x, y in pts if s0 <= s <= s1]


def heart_figure(a, b, w=430.0, h=330.0):
    """a = the right-hand arc, b = optional overshoot past the kiss.

    Flipped vertically at the end so the point hangs down and the cleft sits on
    top, which is how a heart is read.  The construction puts it the other way
    up, and either is the same curve.
    """
    a = [(x, -y) for x, y in a]
    b = [(x, -y) for x, y in b] if b else b
    allpts = list(a) + [(-x, y) for x, y in a]
    if b:
        allpts += list(b)
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    pad = 0.08
    x0, x1 = x0 - pad * (x1 - x0 + 1e-9), x1 + pad * (x1 - x0 + 1e-9)
    y0, y1 = y0 - pad * (y1 - y0 + 1e-9), y1 + pad * (y1 - y0 + 1e-9)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    def path(points, colour, width):
        if len(points) < 2:
            return ""
        return ('<path d="M ' + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}"
                                           for p in points) +
                f'" fill="none" stroke="{colour}" stroke-width="{width}" '
                f'stroke-linecap="round"/>')

    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {path(a, INK, 2.4)}{path([(-x, y) for x, y in a], INK, 2.4)}
    {path(b, GOLD, 1.6) if b else ""}
    <line x1="{put((0, y0))[0]:.1f}" y1="{put((0, y0))[1]:.1f}"
          x2="{put((0, y1))[0]:.1f}" y2="{put((0, y1))[1]:.1f}"
          stroke="{GOLD}" stroke-width="1" stroke-dasharray="5 4"/>
  </svg>"""


def heart_half():
    """The positive-x half of the sextic, as one ordered arc.

    The heart is symmetric in x, so the right half runs from the bottom point
    (0, -1) out around the lobe and back to the cleft (0, 1).  Sampling gives
    the upper and lower branches separately; this walks the upper one outward
    and the lower one back.
    """
    # the page sampler is deliberately coarse; the fit needs a dense one
    upper, lower = G.heart_branches(400)
    up = [p for p in upper if p[0] >= -1e-9]
    lo = [p for p in lower if p[0] >= -1e-9]
    return [(float(a), float(b)) for a, b in up] + \
           [(float(a), float(b)) for a, b in reversed(lo)]


def half_figure(pts, w=430.0, h=330.0, poly=None, spans=None):
    allpts = list(pts) + ([p for p in poly] if poly else [])
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.10
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(q):
        return ox + (q[0] - x0) * k, h - (oy + (q[1] - y0) * k)

    def path(points, colour, width):
        return ('<path d="M ' + " L ".join(f"{put(q)[0]:.1f} {put(q)[1]:.1f}"
                                           for q in points) +
                f'" fill="none" stroke="{colour}" stroke-width="{width}"/>')

    body = path(pts, INK, 2.4)
    if poly:
        body += path(poly, GOLD, 1.3)
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {body}
    <line x1="{put((0, y0))[0]:.1f}" y1="{put((0, y0))[1]:.1f}"
          x2="{put((0, y1))[0]:.1f}" y2="{put((0, y1))[1]:.1f}"
          stroke="{GOLD}" stroke-width="1" stroke-dasharray="5 4"/>
  </svg>"""


def sampled_figure(spec, w=430.0, h=300.0):
    """A curve with no parametrisation: draw the samples, claim nothing more."""
    paths = G.named_data(spec)["paths"] or []
    pts = [p for br in paths for p in br]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.08
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(q):
        return ox + (q[0] - x0) * k, h - (oy + (q[1] - y0) * k)

    body = "".join(
        '<path d="M ' + " L ".join(f"{put(q)[0]:.1f} {put(q)[1]:.1f}" for q in br) +
        f'" fill="none" stroke="{INK}" stroke-width="2.2"/>' for br in paths)
    return (f'<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7"'
            f' stroke="{LINE}"/>{body}</svg>')


def main():
    pts = clothoid()
    tans = tangencies(pts)
    print(f"  {len(tans)} tangencies on a {TURNS:g}-turn arc")
    for s, phi in tans:
        x = _interp(pts, s)[1]
        y = _interp(pts, s)[2]
        rx, ry = rotate((x, y), phi)
        print(f"    s={s:.3f} ({s*s/(4*math.pi):.2f} turns)  rotation "
              f"{math.degrees(phi) % 360:6.2f} deg  touch at (0, {ry:.3f})")

    gallery = []
    for key in ("heart", "cardioid", "bean", "gerono"):
        spec = [x for x in G.NAMED if x["key"] == key][0]
        data = G.named_data(spec)
        if data["exact"]:
            item = E.run(spec)
            gal = E.figure(item)
            note = (f"{item['n']} chords · Euler polygon error "
                    f"{100*item['dev']:.2f}% of size")
        else:
            gal = sampled_figure(spec)
            note = "no parametrisation: sampled, so no chain to fit"
        gallery.append(f"""<section><h2>{key}</h2>
  <div class="art">{gal}</div><p class="cap">{note}</p></section>""")

    cards = []
    for i, (s_t, phi) in enumerate(tans[:-1]):        # the last one folds back
        right = [rotate((x, y), phi) for s, x, y in pts if 0 <= s <= s_t]
        s_cut, exact, snapped, d = next_lattice(pts, s_t, phi, scale=8)
        over = [rotate((x, y), phi) for s, x, y in pts if s_t <= s <= s_cut]
        cap = (f"{s_t*s_t/(4*math.pi):.2f} turns · rotation "
               f"{math.degrees(phi) % 360:.1f}° · cut {d*8:.2f} grid units early")
        cards.append(f"""<section><h2>Fig. {i+1}</h2>
  <div class="art">{heart_figure(right, over)}</div>
  <p class="cap">{cap}</p></section>""")

    half = heart_half()
    n, dev, poly, L = E.fit_branch(half)
    k_spans, dev_spans, span_poly = None, None, None
    for k in (4, 8, 16, 32, 64):
        sp = E.clothoid_spans(half, k)
        d = E.deviation(sp, half) / E.size(half)
        if dev_spans is None or d < dev_spans:
            k_spans, dev_spans, span_poly = k, d, sp
        if d <= 0.01:
            break
    print(f"  heart, positive-x half: {n} chords, Euler error {100*dev:.2f}% of size;"
          f" {k_spans} clothoid spans, error {100*dev_spans:.2f}%")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hearts — one Euler arc, mirrored</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1040px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 22px}}
h2{{font:600 11px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.12em;
text-transform:uppercase;color:{MUTED};margin:0 0 4px}}
.cap{{font-size:12px;color:{MUTED};margin:0}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
section{{background:#fffdf7;border:1px solid {LINE};padding:12px}}
.art{{background:#fffdf7;margin:4px 0 8px}}
svg{{display:block;width:100%;height:auto}}
.panel{{background:#fffdf7;border:1px solid {LINE};padding:16px 18px;margin:0 0 20px}}
li{{margin:0 0 6px}}
</style></head><body><main>
<h1>Hearts</h1>
<p class="lead">One Euler arc, rotated until it kisses the y axis, then mirrored.
The cleft is the kiss; the little extra is where it carries on past it.</p>
<div class="panel">
<p><strong>The construction.</strong> A unit clothoid starts at the origin
heading along +x, with heading <code>theta(s) = s²/2</code> — the curvature grows
linearly, which is what makes it an Euler spiral. Rotate the whole arc about the
origin and, at particular angles, it comes back and touches the y axis with a
vertical tangent. Since the origin is already on that axis, the arc then has
<em>both</em> ends on it — one at the bottom, one where it only kisses.</p>
<p>Mirror that about the y axis and the two halves share the origin and meet at
the kiss. That is a heart, with the cleft at the top. Carry the arc a little
past the kiss — to the next lattice point — and the halves cross instead of
touching, which is the extra at the end.</p>
<p style="font-size:12px;color:{MUTED}">Every percentage on this page, and on
every page in the workbench, is an <strong>error</strong>: a distance between
what was drawn and what was wanted, as a share of a stated reference. Where a
number is not an error it says so in words.</p>
</div>
<div class="grid2">{''.join(cards)}</div>
<h2 style="margin-top:32px">The heart, split at x = 0</h2>
<p style="font-size:14px;color:{MUTED};max-width:70ch">The heart is symmetric
in x, so it is two curves. Taking the positive-x half alone gives one open arc
from the bottom point to the cleft — the shape we actually have to build. Gold
is an Euler polygon over that arc; the error is <strong>{100*dev:.2f}% of the
half's own size</strong>, at {n} chords.</p>
<div class="grid2">
<section><h2>positive x</h2><div class="art">{half_figure(half, poly=poly)}</div>
<p class="cap">{n} chords · Euler error {100*dev:.2f}% of size</p></section>
<section><h2>negative x</h2><div class="art">{half_figure([(-x, y) for x, y in half], poly=[(-x, y) for x, y in poly])}</div>
<p class="cap">the mirror — the same curve, and the same chain flipped</p></section>
</div>
<h2 style="margin-top:32px">The existing curves, as Euler chains</h2>
<p style="font-size:14px;color:{MUTED};max-width:70ch">Gold is the chain, ink is
the curve. The heart has no parametrisation at all — it is a smooth sextic of
genus 4 — so it has no chain and is drawn by sampling. The cardioid, the bean and
Gerono's lemniscate do, and are matched under 1 per cent.</p>
<div class="grid2">{''.join(gallery)}</div>
</main></body></html>
"""
    out = ROOT / "workbench" / "hearts.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
