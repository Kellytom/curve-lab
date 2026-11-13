"""The named curves found in the septic sandbox, with their exact metrics.

    .venv/bin/python scripts/septic_curves.py

Writes workbench/septic-curves.json, which the sandbox injects as the seed
for its saved-curves row.  A curve is the eight speed numbers; everything
else - bend, pitch, inflection, closest, degree - is computed here.
"""

from __future__ import annotations

import json
from pathlib import Path

import ph_quintic_metrics as M

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "septic-curves.json"

# name, speed x (four), speed y (four)
CURVES = [
    ("half-heart", (1.95, 4.85, 6.45, -16), (2.0, -4.95, 5.05, 5.25)),
    ("flourish-a", (1.95, 4.4, 6.45, -16), (2.0, -8.0, 4.95, 5.2)),
    ("flourish-b", (2.05, 4.4, 5.75, -16), (1.75, -7.85, 5.15, 8.5)),
]


def record(name, speed_x, speed_y):
    metrics = M.metrics(speed_x, speed_y)
    x, y = M.curve_polynomials(speed_x, speed_y)
    degree_x = max((k for k, c in enumerate(x) if c), default=0)
    degree_y = max((k for k, c in enumerate(y) if c), default=0)
    return {
        "name": name,
        "speedX": list(speed_x),
        "speedY": list(speed_y),
        "bend": round(metrics["bend"], 3),
        "pitch": metrics["pitch"],
        "inflection": None if metrics["inflection"] is None else round(metrics["inflection"], 3),
        "closest": round(metrics["closest"], 3),
        "degree": [degree_x, degree_y],
    }


def build():
    return {"title": "named curves from the septic sandbox",
            "curves": [record(*curve) for curve in CURVES]}


def main():
    document = build()
    OUT.write_text(json.dumps(document, indent=2) + "\n")
    for curve in document["curves"]:
        print(f"{curve['name']:12s} bend {curve['bend']:.3f}  pitch {curve['pitch']:,}  "
              f"degree {curve['degree']}")


if __name__ == "__main__":
    main()
