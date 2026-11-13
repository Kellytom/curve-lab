"""Sample septic curves from small integer speeds.

    .venv/bin/python scripts/septic_samples.py

Searches speed coefficients in [-2, 2] with the first x coefficient positive and
gcd 1 (scaling does not change the shape), keeps the interesting ones, and
writes workbench/septic-samples.json plus the panel sheet used on the sandbox
page.
"""

from __future__ import annotations

import itertools
import json
import random
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys_path = ROOT / "scripts"
import sys
sys.path.insert(0, str(sys_path))

import ph_quintic_metrics as M  # noqa: E402

OUT = ROOT / "workbench" / "septic-samples.json"


def fast_bend(speed_x, speed_y):
    """The exact bend in floats: centred coefficients and the 1/(2^m (m+1)) weights."""
    def centred(coefficients):
        out = [0.0] * len(coefficients)
        for j, coefficient in enumerate(coefficients):
            for k in range(j + 1):
                out[k] += coefficient * math.comb(j, k) * 0.5 ** (j - k)
        return out

    cx, cy = centred(speed_x), centred(speed_y)
    size = max(len(cx), len(cy))
    cx += [0.0] * (size - len(cx))
    cy += [0.0] * (size - len(cy))
    arc = chord_re = chord_im = 0.0
    for k in range(size):
        for l in range(size):
            power = k + l
            if power % 2:
                continue
            w = 1.0 / ((2 ** power) * (power + 1))
            arc += (cx[k] * cx[l] + cy[k] * cy[l]) * w
            chord_re += (cx[k] * cx[l] - cy[k] * cy[l]) * w
            chord_im += (cx[k] * cy[l] + cy[k] * cx[l]) * w
    chord = math.hypot(chord_re, chord_im)
    return arc / chord if chord > 1e-15 else float("inf")


def gcd_of(values):
    result = 0
    for value in values:
        result = math.gcd(result, abs(value))
    return result


def search(limit=2, bend_range=(1.30, 8.0)):
    candidates = []
    values = list(range(-limit, limit + 1))
    for sx0 in range(1, limit + 1):
        for rest in itertools.product(values, repeat=7):
            speeds = (sx0,) + rest
            if gcd_of(speeds) != 1:
                continue
            speed_x = list(speeds[:4])
            speed_y = list(speeds[4:])
            bend = fast_bend(speed_x, speed_y)
            if not (bend_range[0] <= bend <= bend_range[1]):
                continue
            candidates.append((max(abs(value) for value in speeds), abs(bend - 2), bend, speed_x, speed_y))
    candidates.sort()
    return candidates[:400]


def interesting(candidates, wanted=16):
    rows = []
    for _size, _distance, bend, speed_x, speed_y in candidates:
        metrics = M.metrics(speed_x, speed_y)
        if metrics["inflection"] is None:
            continue
        if not (0.05 < metrics["inflection"] < 0.95):
            continue
        if metrics["closest"] <= 0.1:
            continue
        x, y = M.curve_polynomials(speed_x, speed_y)
        if max(len(x), len(y)) - 1 != 7:
            continue
        rows.append({
            "speedX": speed_x,
            "speedY": speed_y,
            "bend": round(metrics["bend"], 3),
            "pitch": metrics["pitch"],
            "inflection": round(metrics["inflection"], 3),
            "closest": round(metrics["closest"], 3),
            "size": max(abs(value) for value in speed_x + speed_y),
        })
    # the same shape appears under sign flips and reversals; collapse it
    seen = set()
    unique = []
    for row in rows:
        key = (row["bend"], row["pitch"], row["inflection"], row["closest"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    unique.sort(key=lambda row: (row["pitch"], row["size"], abs(row["bend"] - 2)))
    return unique[:wanted]


def random_search(trials=120000, limit=4, seed=7):
    rng = random.Random(seed)
    found = []
    for _ in range(trials):
        speeds = [rng.randint(-limit, limit) for _ in range(8)]
        if speeds[0] <= 0 or gcd_of(speeds) != 1:
            continue
        bend = fast_bend(speeds[:4], speeds[4:])
        if not (1.5 <= bend <= 6.0):
            continue
        found.append((max(abs(v) for v in speeds), abs(bend - 2), bend, speeds[:4], speeds[4:]))
    found.sort()
    return found[:400]




def panel_svg(record, width=480, height=250):
    """One sample curve as a standalone SVG panel, labelled inside."""
    speed_x, speed_y = record["speedX"], record["speedY"]
    points = []
    x = y = 0.0
    steps = 300
    for i in range(steps + 1):
        t = i / steps
        a = sum(c * t ** k for k, c in enumerate(speed_x))
        b = sum(c * t ** k for k, c in enumerate(speed_y))
        if i:
            t0 = (i - 1) / steps
            a0 = sum(c * t0 ** k for k, c in enumerate(speed_x))
            b0 = sum(c * t0 ** k for k, c in enumerate(speed_y))
            x += (a0 * a0 - b0 * b0) / steps + ((a * a - b * b) - (a0 * a0 - b0 * b0)) / (2 * steps)
            y += 2 * a0 * b0 / steps + (2 * a * b - 2 * a0 * b0) / (2 * steps)
        points.append((x, y))
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs); min_y, max_y = min(ys), max(ys)
    left, right, top, bottom = 16, 16, 44, 40
    scale = min((width - left - right) / max(1e-9, max_x - min_x),
                (height - top - bottom) / max(1e-9, max_y - min_y))
    ox = left + (width - left - right - (max_x - min_x) * scale) / 2
    oy = top + (height - top - bottom - (max_y - min_y) * scale) / 2
    fx = lambda v: ox + (v - min_x) * scale
    fy = lambda v: oy + (max_y - v) * scale
    path = "M" + " L".join(f"{fx(p[0]):.1f},{fy(p[1]):.1f}" for p in points)
    label = f"x={record['speedX']} y={record['speedY']}"
    metrics = (f"bend {record['bend']:.2f} | pitch {record['pitch']:,} | "
               f"inflection {record['inflection']:.2f}")
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="sample septic {label}">'
        f'<rect width="{width}" height="{height}" fill="#fbf7ec"/>'
        f'<text x="{left}" y="18" font-size="13" font-weight="600" fill="#2e2413">{label}</text>'
        f'<text x="{left}" y="34" font-size="12" fill="#7b6c4e">{metrics}</text>'
        f'<path d="{path}" fill="none" stroke="#2e2413" stroke-width="2"/>'
        f'</svg>'
    )


def main():
    candidates = search(2) + random_search()
    rows = interesting(candidates, wanted=40)
    document = {"title": "septic samples from small integer speeds",
                "searched": "speed coefficients in [-2, 2], first x coefficient positive, gcd 1",
                "curves": rows}
    OUT.write_text(json.dumps(document, indent=2) + "\n")
    print(f"{len(candidates)} candidates, {len(rows)} kept")
    for row in rows:
        print(f"  x={row['speedX']} y={row['speedY']}  bend {row['bend']:.2f} "
              f"pitch {row['pitch']} infl {row['inflection']:.2f}")


if __name__ == "__main__":
    main()
