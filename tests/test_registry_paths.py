"""The stored outlines keep the source's precision, so a graph is not a staircase.

The registry once copied a sampled path with `round(px, 2)`. On a curve of size 1–3 that
is coarser than the step between samples: the outline became a run of axis-aligned steps.
`c-0143` (y = x^2 as a t^2 cover) drew as a staircase, not a parabola — the operator's
"please fix underlying graph", 2026-11-21.

The registry may round to two decimals for identity; it must not round the drawing.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "workbench" / "curve-registry.json"
SOURCES = (ROOT / "workbench" / "finder.json", ROOT / "workbench" / "real-curves.json")


def shape(path):
    return tuple((round(float(x), 2), round(float(y), 2)) for x, y in path)


def source_paths():
    out = {}
    for file in SOURCES:
        if not file.exists():
            continue
        data = json.loads(file.read_text(encoding="utf-8"))
        for item in data.get("curves", []):
            path = item.get("path")
            if not path or item.get("speedX") or item.get("speedY"):
                continue
            out.setdefault(shape(path), path)
    return out


class RegistryPathTest(unittest.TestCase):
    def test_each_sampled_outline_keeps_the_source_precision(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        by_shape = source_paths()
        matched = 0
        for record in registry["curves"]:
            if record.get("kind") != "polyline" or not record.get("path"):
                continue
            source = by_shape.get(shape(record["path"]))
            if not source:
                continue
            matched += 1
            self.assertEqual(len(record["path"]), len(source), record["uid"])
            worst = max((max(abs(float(a[0]) - float(b[0])), abs(float(a[1]) - float(b[1])))
                         for a, b in zip(record["path"], source)), default=0.0)
            self.assertLess(worst, 1e-6,
                            f"{record['uid']} stored a rounded outline (worst miss {worst:.4f})")
        self.assertGreaterEqual(matched, 50,
                                "the source match must not be vacuous; the finder has 56")

    def test_the_y_x_2_cover_is_not_a_staircase(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        record = next(row for row in registry["curves"] if row["uid"] == "c-0143")
        path = record["path"]
        axis = sum(1 for a, b in zip(path, path[1:])
                   if abs(a[0] - b[0]) < 1e-9 or abs(a[1] - b[1]) < 1e-9)
        self.assertLess(axis, 0.1 * (len(path) - 1),
                        f"c-0143 has {axis} axis-aligned steps of {len(path) - 1}")


if __name__ == "__main__":
    unittest.main()
