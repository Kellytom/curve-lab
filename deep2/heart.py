#!/usr/bin/env python3
"""A broken heart whose break is a curve, not a jagged cut.

    .venv/bin/python deep2/heart.py

The construction: a heart, split along a vertical seam. The seam is ONE curve
taken from the catalogue — the same curve on both halves, so the two pieces
fit back together exactly: what is missing on the left is exactly what is
left on the right. The halves are drawn apart, and a reassembled view shows
the join.

Samples: three catalogue curves as the seam (an S, a hook, a curlicue — see
the registry names printed), plus the same heart with a straight seam as the
reference the samples are judged against.

Outputs (deep2/out/):
  heart-<name>.svg          the halves apart, the seam in both, labels
  heart-<name>-joined.svg   the halves together again
"""

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from fractions import Fraction  # noqa: E402

from curve_lab.measure import curve_polynomials, to_fraction  # noqa: E402


# the parametric heart, sampled to stations; y up, height 1, tip at (0,0),
# notch at (0,1)
def heart_stations():
    """The heart's right side, tip (0,0) to notch (0,1), as explicit stations.

    The parametric formula was tried first and failed three times: the
    normalisation inverted its middle while the forced endpoints stayed put,
    and the outline crossed itself. These stations are the construction: the
    lobes are deliberate, and the seam connects the tip to the notch.
    """
    return [
        (0.0, 0.0),
        (0.16, 0.06),
        (0.30, 0.16),
        (0.42, 0.30),
        (0.48, 0.46),
        (0.51, 0.62),
        (0.53, 0.78),
        (0.50, 0.92),
        (0.42, 1.02),
        (0.28, 1.06),
        (0.12, 1.03),
        (0.0, 0.97),
    ]


def catmull_spans(points):
    """Catmull-Rom cubic spans through the points — the house drawing rule."""

    def tangent(k):
        if k == 0:
            return (points[1][0] - points[0][0], points[1][1] - points[0][1])
        if k == len(points) - 1:
            return (points[-1][0] - points[-2][0], points[-1][1] - points[-2][1])
        return (
            (points[k + 1][0] - points[k - 1][0]) / 2,
            (points[k + 1][1] - points[k - 1][1]) / 2,
        )

    spans = []
    for k in range(len(points) - 1):
        p0, p3 = points[k], points[k + 1]
        m0, m1 = tangent(k), tangent(k + 1)
        spans.append(
            {
                "p0": p0,
                "c1": (p0[0] + m0[0] / 3, p0[1] + m0[1] / 3),
                "c2": (p3[0] - m1[0] / 3, p3[1] - m1[1] / 3),
                "p3": p3,
            }
        )
    return spans


def catalogue_seam(uid):
    """A catalogue curve's spans, mapped so its ENDS land on the heart's
    notch (top) and tip (bottom): uniform scale to the height, the chord
    turned vertical, then translated. Affine maps keep cubics cubics."""
    registry = json.load(open(ROOT / "workbench" / "curve-registry.json"))
    record = next(r for r in registry["curves"] if r["uid"] == uid)
    x, y = curve_polynomials(
        [to_fraction(v) for v in record["speedX"]], [to_fraction(v) for v in record["speedY"]]
    )
    stations = []
    n = 21
    for k in range(n):
        t = k / (n - 1)
        px = sum(float(c) * t**i for i, c in enumerate(x))
        py = sum(float(c) * t**i for i, c in enumerate(y))
        stations.append((px, py))
    # the chord, start → end
    (ax, ay), (bx, by) = stations[0], stations[-1]
    cx, cy = bx - ax, by - ay
    length = math.hypot(cx, cy) or 1
    # rotate the chord to point DOWN (0,-1): cos/sin of the needed turn
    cos_a, sin_a = cy / length, cx / length  # rotate (cx,cy) to (0,length)
    # after the turn the chord points up; flip y to point down, then scale so
    # the chord has length 1 and translate the start to the notch (0,1)
    s = 1 / length

    def place(p):
        dx, dy = p[0] - ax, p[1] - ay
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        # the chord now runs up; map: start → (0,1), end → (0,0)
        return (rx * s, NOTCH_Y - ry * s * NOTCH_Y)

    mapped = [place(p) for p in stations]
    # the seam's own width is whatever the curve's is; keep it as it maps
    return record["name"], catmull_spans(mapped)


def ph_seam(a=Fraction(1, 2), stations_count=25):
    """A seam from OUR equations: u = 1, v = a·(2t − 1).

    The position curve sags laterally by about a/2 and runs monotone along its
    length — turned vertical it is a clean break line, and the rows are exact
    rationals (a is a Fraction). Different a = a different break strength.
    """
    from fractions import Fraction

    from curve_lab.measure import curve_polynomials, to_fraction

    u = [Fraction(1)]
    v = [-Fraction(a), 2 * Fraction(a)]
    x, y = curve_polynomials([to_fraction(c) for c in u], [to_fraction(c) for c in v])
    stations = []
    for k in range(stations_count):
        t = k / (stations_count - 1)
        px = sum(float(c) * t**i for i, c in enumerate(x))
        py = sum(float(c) * t**i for i, c in enumerate(y))
        stations.append((px, py))
    spans = catmull_spans(stations)
    return map_seam(spans)


def s_seam(amplitude, stations_count=25):
    """A balanced break: lateral x(t) = A·sin(2πt), zero at both ends. The
    seam leans one way in the upper half and the other below, so BOTH pieces
    gain an interlocking lobe — the one-sided PH sag made the right piece a
    crescent."""
    stations = []
    for k in range(stations_count):
        t = k / (stations_count - 1)
        stations.append((amplitude * math.sin(2 * math.pi * t), t))
    return map_seam(catmull_spans(stations))


def preset_seam(name):
    """A preset design (ogee, s-curve, bracket) rendered by the project's own
    engine and fitted to spans — the presets ARE vertical-graph-like designs,
    which the catalogue curves mostly are not."""
    from curve_lab import bezier, engine, presets

    design = presets.get(name)
    chain = engine.build(design)
    spine, _fit = bezier.fit_chain(chain, tol=0.01, max_spans_per_segment=32, split=2)
    spans = [
        {"p0": tuple(s["p0"]), "c1": tuple(s["c1"]), "c2": tuple(s["c2"]), "p3": tuple(s["p3"])}
        for s in spine
    ]
    return name, map_seam(spans)


NOTCH_Y = 0.97


def map_seam(spans):
    """Uniform scale to height 1, chord turned to run down the page, start at
    the notch (0,1), end at the tip (0,0) — the same affine rule for every
    seam source."""
    (ax, ay), (bx, by) = spans[0]["p0"], spans[-1]["p3"]
    cx, cy = bx - ax, by - ay
    length = math.hypot(cx, cy) or 1
    cos_a, sin_a = cy / length, cx / length
    s = 1 / length

    def place(p):
        dx, dy = p[0] - ax, p[1] - ay
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        return (rx * s, NOTCH_Y - ry * s * NOTCH_Y)

    return [
        {"p0": place(sp["p0"]), "c1": place(sp["c1"]), "c2": place(sp["c2"]), "p3": place(sp["p3"])}
        for sp in spans
    ]


def path_from(spans, close=False):
    # the design is y-up; SVG's y is down, so y is flipped HERE and only here
    def f(v):
        return f"{v:.4f}"

    def y(v):
        return 1.0 - v

    parts = [f"M {f(spans[0]['p0'][0])} {f(y(spans[0]['p0'][1]))}"]
    for s in spans:
        parts.append(
            f"C {f(s['c1'][0])} {f(y(s['c1'][1]))} {f(s['c2'][0])} {f(y(s['c2'][1]))} "
            f"{f(s['p3'][0])} {f(y(s['p3'][1]))}"
        )
    if close:
        parts.append("Z")
    return " ".join(parts)


def draw(seam_spans, seam_label, out_path, joined=False, gap=0.22):
    """The heart as two halves. Left: notch → left outline → tip → up the
    seam. Right: tip → right outline → notch → down the seam (reversed).
    The seam is the SAME curve in both — reversed, not mirrored."""
    right_side = catmull_spans(heart_stations())  # tip → notch
    left_side = [
        {
            "p0": (-s["p0"][0], s["p0"][1]),
            "c1": (-s["c1"][0], s["c1"][1]),
            "c2": (-s["c2"][0], s["c2"][1]),
            "p3": (-s["p3"][0], s["p3"][1]),
        }
        for s in right_side
    ]
    [
        {"p0": s["p3"], "c1": s["c2"], "c2": s["c1"], "p3": s["p0"]} for s in seam_spans[::-1]
    ]

    # BOTH halves append the SAME seam (notch → tip): the break line is the
    # same curve in both pieces — that is the operator's requirement, and it
    # is what makes the halves fit back together exactly. (The reversed copy
    # was tried and put the seam outside the right piece.)
    right = right_side + seam_spans
    left = left_side + seam_spans

    ox = gap if not joined else 0

    def shift(spans, dx):
        return [{k: (v[0] + dx, v[1]) for k, v in s.items()} for s in spans]

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1.3 -0.12 2.9 1.34" '
        'width="900" height="520">'
        '<rect x="-1.3" y="-0.12" width="2.9" height="1.34" fill="#fffef9"/>'
    ]
    if not joined:
        svg.append(
            f'<path d="{path_from(shift(left, -ox))}" fill="none" stroke="#3b2d1c" stroke-width="0.006"/>'  # noqa: E501
        )
        svg.append(
            f'<path d="{path_from(shift(right, ox))}" fill="none" stroke="#3b2d1c" stroke-width="0.006"/>'  # noqa: E501
        )
        svg.append(
            f'<text x="-1.25" y="-0.06" font-size="0.045" fill="#5a4a36" font-family="Georgia, serif">'  # noqa: E501
            f"broken heart · seam: {seam_label} · the same curve in both halves</text>"
        )
    else:
        svg.append(
            f'<path d="{path_from(left)}" fill="none" stroke="#3b2d1c" stroke-width="0.006"/>'
        )
        svg.append(
            f'<path d="{path_from(right)}" fill="none" stroke="#3b2d1c" stroke-width="0.006"/>'
        )
        svg.append(
            '<text x="-1.25" y="-0.06" font-size="0.045" fill="#5a4a36" font-family="Georgia, serif">'  # noqa: E501
            "together again · the break line is identical on both halves</text>"
        )
    svg.append("</svg>")
    Path(out_path).write_text("".join(svg))


def half_width(y, stations=None):
    """The heart's half-width at height y, from the outline stations."""
    pts = stations or heart_stations()
    best = 0.0
    for x, yy in pts:
        if abs(yy - y) < 0.06:
            best = max(best, abs(x))
    return best or 0.05


def seam_is_clean(spans, stations):
    """A break line must: run downward along its stations, keep its CONTROL
    points inside the heart's height (no spurs above the notch — the first
    samples had them), and stay inside the heart's body at every height."""
    ys = [p[1] for p in stations]
    steps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    if any(s > 0.004 for s in steps):
        return False
    for s in spans:
        for key in ("c1", "c2"):
            if s[key][1] > 1.02 or s[key][1] < -0.02:
                return False
    xs = [p[0] for p in stations]
    if max(xs) - min(xs) > 0.75:
        return False
    for x, y in stations:
        if abs(x) > half_width(y) * 0.85:
            return False
    return True


def choose_seams(count=3):
    """Scan the registry for curves that make clean break lines: monotone
    downward, lateral reach between 0.12 and 0.45 of the height."""
    registry = json.load(open(ROOT / "workbench" / "curve-registry.json"))
    found = []
    for record in registry["curves"]:
        if not record.get("speedX"):
            continue
        try:
            name, spans = catalogue_seam(record["uid"])
        except Exception:
            continue
        stations = [s["p0"] for s in spans] + [spans[-1]["p3"]]
        xs = [p[0] for p in stations]
        reach = max(xs) - min(xs)
        if not (0.10 <= reach <= 0.45) or not seam_is_clean(spans, stations):
            continue
        found.append((abs(reach - 0.22), record["uid"], name, spans))
    found.sort()
    picked, seen = [], set()
    for _, uid, name, spans in found:
        if uid in seen:
            continue
        seen.add(uid)
        picked.append((uid, name, spans))
        if len(picked) >= count:
            break
    return picked


def main():
    samples = choose_seams(3)
    straight = [{"p0": (0.0, 1.0), "c1": (0.0, 0.667), "c2": (0.0, 0.333), "p3": (0.0, 0.0)}]
    from fractions import Fraction

    preset_samples = []
    for amp, slug in ((0.10, "s-1of10"), (0.18, "s-9of50"), (0.26, "s-13of50")):
        spans = s_seam(amp)
        label = f"S seam, lateral {amp:.2f}"
        preset_samples.append((slug, label, spans))
        xs = [v for s in spans for v in (s["c1"][0], s["c2"][0], s["p3"][0])]
        print(f"seam {label}: side reach {max(xs) - min(xs):.3f} (balanced)")
    for a in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)):
        spans = ph_seam(a)
        stations = [s["p0"] for s in spans] + [spans[-1]["p3"]]
        xs = [v for s in spans for v in (s["c1"][0], s["c2"][0], s["p3"][0])]
        label = f"PH seam u=1, v={a}·(2t−1)"
        preset_samples.append((f"ph-{a.numerator}of{a.denominator}", label, spans))
        print(
            f"seam {label}: side reach {max(xs) - min(xs):.3f} of the heart height · clean {seam_is_clean(spans, stations)}"  # noqa: E501
        )
    for name in ("ogee", "s-curve", "bracket"):
        try:
            label, spans = preset_seam(name)
            stations = [s["p0"] for s in spans] + [spans[-1]["p3"]]
            if seam_is_clean(spans, stations):
                preset_samples.append((name, label, spans))
                xs = [v for s in spans for v in (s["c1"][0], s["c2"][0])]
                print(f"seam preset {name}: side reach {max(xs) - min(xs):.3f} of the heart height")
            else:
                print(f"seam preset {name}: fails the clean-graph rules (skipped)")
        except Exception as error:
            print(f"seam preset {name}: {type(error).__name__}: {error}")
    for uid, name, seam_spans in preset_samples + samples:
        slug = uid if uid.startswith("ph-") else name
        draw(
            seam_spans,
            f"{name} · {uid}" if uid.startswith("ph-") else f"{name} ({uid})",
            HERE / "out" / f"heart-{slug}.svg",
        )
        draw(
            seam_spans,
            f"{name} · {uid}" if uid.startswith("ph-") else f"{name} ({uid})",
            HERE / "out" / f"heart-{slug}-joined.svg",
            joined=True,
        )
        xs = [v for s in seam_spans for v in (s["c1"][0], s["c2"][0], s["p3"][0])]
        print(f"seam {uid} {name}: side reach {max(xs) - min(xs):.3f} of the heart height")
    draw(straight, "a straight line (reference)", HERE / "out" / "heart-straight.svg")
    draw(
        straight,
        "a straight line (reference)",
        HERE / "out" / "heart-straight-joined.svg",
        joined=True,
    )
    print("wrote out/heart-*.svg and out/heart-*-joined.svg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
