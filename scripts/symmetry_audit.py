"""Every stored curve against every rational mirror axis, with numpy speed.

    .venv/bin/python scripts/symmetry_audit.py --all          # stored + finder
    .venv/bin/python scripts/symmetry_audit.py --finder       # finder only
    .venv/bin/python scripts/symmetry_audit.py --set found    # one stored set

Axes tested (as direction vectors, all rational): horizontal (1,0), vertical
(0,1), the two diagonals (1,1) and (1,-1), and the p-triple slopes (3,4), (4,3),
(5,12), (12,5), (7,24), (24,7), (2,1), (1,2), (3,1), (1,3). Plus the half turn.

A symmetry is reported when the largest gap between the curve and its mirror
image is at most 0.5% of the curve's size. The sandbox page tests only the
vertical axis, which is why the diagonal and x-axis cases were open.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

THRESHOLD = 0.005
SAMPLES = 140

AXES = {
    "horizontal (x axis)": (1, 0),
    "vertical (y axis)": (0, 1),
    "diagonal y=x": (1, 1),
    "anti-diagonal y=-x": (1, -1),
    "slope 3/4": (4, 3),
    "slope 4/3": (3, 4),
    "slope 5/12": (12, 5),
    "slope 12/5": (5, 12),
    "slope 7/24": (24, 7),
    "slope 24/7": (7, 24),
    "slope 1/2": (2, 1),
    "slope 2/1": (1, 2),
    "slope 1/3": (3, 1),
    "slope 3/1": (1, 3),
}


def gaps(points):
    """Hausdorff gap of the curve against each axis reflection, as a share of size."""
    p = np.asarray(points, dtype=float)
    centre = (p.min(axis=0) + p.max(axis=0)) / 2
    q = p - centre
    size = max(p.max(axis=0) - p.min(axis=0)) or 1.0
    out = {}
    spacing = float(np.mean(np.linalg.norm(np.diff(q, axis=0), axis=1))) / size if len(q) > 1 else 0.0
    tolerance = max(THRESHOLD, 2.5 * spacing)
    for name, (dx, dy) in AXES.items():
        d = np.array([dx, dy], dtype=float)
        reflected = 2 * np.outer(q @ d / (d @ d), d) - q
        a, b = q[:, None, :], reflected[None, :, :]
        distances = np.sqrt(((a - b) ** 2).sum(axis=2))
        gap = max(distances.min(axis=1).max(), distances.min(axis=0).max())
        out[name] = float(gap / size)
    # half turn
    a, b = q[:, None, :], (-q)[None, :, :]
    distances = np.sqrt(((a - b) ** 2).sum(axis=2))
    out["half turn"] = float(max(distances.min(axis=1).max(), distances.min(axis=0).max()) / size)
    return out


def spine_points(speeds, samples=SAMPLES):
    from ph_crossings import spine
    _, xs, ys = spine(speeds[0], speeds[1], samples=samples)
    return list(zip(xs, ys))


def finder_rows():
    data = json.loads((ROOT / "workbench" / "finder.json").read_text(encoding="utf-8"))
    for curve in data["curves"]:
        pts = curve.get("path") or []
        if len(pts) > 16:
            yield f'finder: {curve.get("family", "?")} · {curve["name"]}', pts


def stored_rows(which):
    if which == "found":
        data = json.loads((ROOT / "workbench" / "found-curves.json").read_text(encoding="utf-8"))
        rows = [(c["name"], c["terms"]) for c in data["curves"]]
    elif which == "moved":
        data = json.loads((ROOT / "workbench" / "moved-curves.json").read_text(encoding="utf-8"))
        rows = [(c["name"], c["terms"]) for c in data["curves"]]
    elif which == "curves":
        data = json.loads((ROOT / "workbench" / "real-curves.json").read_text(encoding="utf-8"))
        rows = [(c["name"], [{"power": i, "x": c["speedX"][i], "y": c["speedY"][i]}
                             for i in range(len(c["speedX"]))]) for c in data["curves"]]
    else:
        return
    for name, terms in rows:
        size = max(t["power"] for t in terms) + 1
        u = [0.0] * size; v = [0.0] * size
        for term in terms:
            u[term["power"]] = float(term["x"])
            v[term["power"]] = float(term["y"])
        yield f"{which}: {name}", spine_points((u, v))


def main(argv):
    rows = []
    if "--finder" in argv or "--all" in argv:
        rows += list(finder_rows())
    sets = [a.split("=")[1] for a in argv if a.startswith("--set=")]
    if "--all" in argv:
        sets = ["found", "moved", "curves"]
    for which in sets:
        rows += list(stored_rows(which))

    hits = {}
    totals = {}
    for name, points in rows:
        found = [axis for axis, gap in gaps(points).items() if gap <= THRESHOLD]
        for axis in found:
            totals[axis] = totals.get(axis, 0) + 1
        for axis in found:
            if axis not in ("vertical (y axis)",):
                hits.setdefault(axis, []).append(name)
    print(f"{len(rows)} curves tested against {len(AXES)} axes and the half turn")
    for axis, count in sorted(totals.items(), key=lambda kv: -kv[1]):
        print(f"  {axis:22} {count}")
    for axis, names in hits.items():
        if axis == "horizontal (x axis)":
            print(f"\n{axis}: {len(names)}")
            for name in names[:8]:
                print("   ", name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
