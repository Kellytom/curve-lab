"""Attach a cap to a recovered terminal, and a terminal to a chain node.

Both sides now carry a framework: a point and an outward direction. This script
uses it twice, and measures what can actually be measured:

    python3 scripts/attach.py

1. A cap's *geometry* is placed at a terminal's seam. The anchor gap must be
   zero; the direction must agree; and the cap's length is compared with the
   terminal's cut length, which is the only reach both sides state.
2. A terminal's geometry is placed at a chain node. The seam must land on the
   node and point along its heading.

Nothing is scaled: caps and terminals are already in page units.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pythagorean_spiral import design, place  # noqa: E402
from pythagorean_spiral.triples import thinnest  # noqa: E402

CAPS = json.loads((ROOT.parent / "out" / "caps" / "cap-1.json").read_text())
CAP_FILES = sorted((ROOT.parent / "out" / "caps").glob("cap-*.json"))


def cap_points(cap, per_unit=16.0):
    """The cap as a polyline: kappa(s) = k0 + kd*s, integrated finely."""
    pts = [(0.0, 0.0)]
    h = x = y = 0.0
    for seg in cap["segments"]:
        k0, kd, L = seg["kappa0"], seg["kd"], seg["length"]
        n = max(2, int(L * per_unit))
        ds = L / n
        for i in range(n):
            s = i * ds
            kappa = k0 + kd * s
            theta = h + 0.5 * kappa * ds
            x += ds * math.cos(theta)
            y += ds * math.sin(theta)
            h += kappa * ds
            pts.append((x, y))
    return pts


def cap_length(cap):
    return sum(seg["length"] for seg in cap["segments"])


def terminal_points(t, per_span=16):
    """The recovered end as a polyline, from its cubic spans."""
    out = []
    for sp in t["spans"]:
        p0, c1, c2, p3 = sp["p0"], sp["c1"], sp["c2"], sp["p3"]
        for i in range(per_span + 1):
            u = i / per_span
            v = 1 - u
            out.append((
                v**3 * p0[0] + 3 * v * v * u * c1[0] + 3 * v * u * u * c2[0] + u**3 * p3[0],
                v**3 * p0[1] + 3 * v * v * u * c1[1] + 3 * v * u * u * c2[1] + u**3 * p3[1],
            ))
    return out


def localize(points, framework):
    """Move a placed thing back to its own frame: seam at the origin, +x outward."""
    ax, ay = framework["anchor"]
    hx, hy = framework["heading"]
    out = []
    for x, y in points:
        # the stored spans are y-down; the framework is y-up
        dx, dy = x - ax, -y - ay
        out.append((dx * hx + dy * hy, -dx * hy + dy * hx))
    return out


def main() -> int:
    caps = [json.loads(p.read_text()) for p in CAP_FILES]
    caps.sort(key=cap_length)
    page = json.loads((ROOT.parent / "docs" / "terminals" / "stage-two.json").read_text())
    terms = [t for f in page["figures"] for t in f["terminals"]]

    gaps, angles, ratios, within = [], [], [], 0
    cap_by_len = [(cap_length(c), c) for c in caps]

    for t in terms:
        fr = t["framework"]
        cut = t["cut"]
        best = min(cap_by_len, key=lambda pair: abs(math.log(pair[0] / cut)))[1]
        placed = place.place_at_frame(cap_points(best), fr["anchor"], fr["heading"])
        gaps.append(math.dist(placed[0], fr["anchor"]))
        ax = place.place_at_frame([(1, 0)], fr["anchor"], fr["heading"])[0]
        v = (ax[0] - fr["anchor"][0], ax[1] - fr["anchor"][1])
        angles.append(math.degrees(math.acos(max(-1, min(1,
            v[0] * fr["heading"][0] + v[1] * fr["heading"][1])))))
        ratio = cap_length(best) / cut
        ratios.append(ratio)
        if 0.8 <= ratio <= 1.25:
            within += 1

    print(f"1. cap on a terminal ({len(terms)} ends, best-matching cap by length)")
    print(f"   anchor gap      max {max(gaps):.1e}")
    print(f"   direction       max {max(angles):.3f} deg (six-decimal heading rounding)")
    print(f"   reach / cut     median {statistics.median(ratios):.2f}, "
          f"range {min(ratios):.2f}–{max(ratios):.2f}")
    print(f"   within 0.8–1.25 of the cut: {within}/{len(terms)}")

    # reverse: a terminal on a chain node
    lobe = design.lobe(thinnest(3125), 6)
    node = 5
    point, heading = lobe.knots()[node]
    fr = {"anchor": (float(point[0]), float(point[1])),
          "heading": (float(heading.re), float(heading.im))}
    t = terms[0]
    local = localize(terminal_points(t), t["framework"])
    placed = place.place_at_frame(local, fr["anchor"], fr["heading"])
    gap = math.dist(placed[0], fr["anchor"])
    tip = max(math.dist(p, fr["anchor"]) for p in placed)
    print(f"\n2. terminal on chain node {node} of a lobe")
    print(f"   node            ({fr['anchor'][0]:.3f}, {fr['anchor'][1]:.3f})")
    print(f"   seam gap        {gap:.1e}")
    print(f"   tip reaches     {tip:.1f} page units along the outward direction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
