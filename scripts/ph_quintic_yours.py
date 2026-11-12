"""Clean up curves saved from the gallery: exact fractions and integers.

    .venv/bin/python scripts/ph_quintic_yours.py

Writes workbench/ph-quintic-yours.json and workbench/ph-quintic-yours.svg.

A saved curve arrives as decimals from the sliders.  Rounding to the slider
step gives an exact fraction, and scaling by the lcm of the denominators
gives an integer recipe - the same curve, with a pitch that can be read.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction as F
from pathlib import Path

import ph_quintic_lattice as Q
import ph_quintic_presets as P

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "workbench" / "ph-quintic-yours.json"
SVG_PATH = ROOT / "workbench" / "ph-quintic-yours.svg"

# label, saved at, u, v - exactly as the gallery saved them
RAW = [
    ("saved 1", "2026-11-12T18:58:48Z", (1.65, -5.5, 5.4), (1.825, -11.65, 11.8)),
    ("saved 2", "2026-11-12T19:03:18Z", (2.625, -8.65, 7.8), (1.775, -11.45, 11.6)),
    ("saved 3", "2026-11-12T19:03:54Z", (2.725, -8.65, 7.8), (1.75, -11.4, 11.6)),
    ("saved 4", "2026-11-12T19:04:57Z", (-0.8825, 6.33, -6.33), (1.415, -5.66, 5.66)),
    ("saved 5", "2026-11-12T19:05:44Z", (0.3625, 2.35, -3.35), (1.15, -4.6, 4.6)),
    ("saved 6", "2026-11-12T19:07:04Z", (0.1375, 2.45, -3.45), (1.5, -4.6, 4.6)),
    ("saved 7", "2026-11-12T19:09:40Z", (-0.425, 5.4, -7.1), (1.925, -4.55, 4.6)),
    ("saved 8", "2026-11-12T19:17:03Z", (-0.3, 4.9, -6.6), (0.5125, 1.1, -1.05)),
    ("saved 9", "2026-11-12T19:18:41Z", (-1.775, 7.2, -7.5), (0.0375, 1.8, -0.55)),
    ("saved 10", "2026-11-12T19:22:22Z", (-1.6, 6.35, -7.3), (-0.0125, 5, -6.75)),
]


def exact(values):
    """The slider value as an exact fraction (the sliders step by 0.05)."""
    return tuple(F(value).limit_denominator(1000) for value in values)


def integer_form(u, v):
    """The smallest integer recipe with the same shape, and the scale used."""
    scale = 1
    for coefficient in u + v:
        scale = math.lcm(scale, coefficient.denominator)
    scaled_u = tuple(int(coefficient * scale) for coefficient in u)
    scaled_v = tuple(int(coefficient * scale) for coefficient in v)
    divisor = 0
    for value in scaled_u + scaled_v:
        divisor = math.gcd(divisor, abs(value))
    divisor = divisor or 1
    return (tuple(value // divisor for value in scaled_u),
            tuple(value // divisor for value in scaled_v),
            scale // divisor)


def record(label, saved_at, u_decimal, v_decimal):
    u, v = exact(u_decimal), exact(v_decimal)
    integer_u, integer_v, scale = integer_form(u, v)
    inflection, pitch, end, _swing = Q.s_info(u, v)
    integer_inflection, integer_pitch, integer_end, _ = Q.s_info(integer_u, integer_v)
    return {
        "label": label,
        "saved": saved_at,
        "u_decimal": [str(value) for value in u_decimal],
        "v_decimal": [str(value) for value in v_decimal],
        "u": [str(coefficient) for coefficient in integer_u],
        "v": [str(coefficient) for coefficient in integer_v],
        "scale": scale,
        "bend": round(P.bend_ratio(u, v), 2),
        "pitch_decimal": pitch,
        "pitch": integer_pitch,
        "inflection": round(inflection, 2),
        "closest_approach": round(P.closest_approach(u, v), 2),
        "endpoint": [str(end[0]), str(end[1])],
        "endpoint_at_pitch": [str(integer_end[0] * integer_pitch),
                              str(integer_end[1] * integer_pitch)],
    }


def build_records():
    return [record(*case) for case in RAW]


def build_document(records):
    return {
        "title": "curves saved from the ph-quintic gallery, cleaned",
        "generator": "scripts/ph_quintic_yours.py",
        "note": (
            "u_decimal and v_decimal are what the sliders held; u and v are the same curve "
            "as integers, scaled by the lcm of the denominators. The pitch is read from the "
            "integer form - the decimal form's pitch is meaningless because the decimals are "
            "binary approximations."
        ),
        "curves": records,
    }


def main():
    records = build_records()
    JSON_PATH.write_text(json.dumps(build_document(records), indent=2) + "\n")
    sheet = []
    for item in records:
        sheet.append({
            "label": item["label"],
            "bend": item["bend"],
            "pitch": item["pitch"],
            "u": item["u"],
            "v": item["v"],
        })
    SVG_PATH.write_text(P.build_svg(sheet, title="Curves saved from the gallery, cleaned"))
    print(f"{JSON_PATH.relative_to(ROOT)}  {len(records)} curves")
    print(f"{SVG_PATH.relative_to(ROOT)}  {SVG_PATH.stat().st_size} bytes")


if __name__ == "__main__":
    main()
