#!/usr/bin/env python3
"""Is our quintic the same curve Blender draws? Ask Blender.

The extension claims that six control points, `order_u = 6` and
`use_endpoint_u` make one exact degree-5 Bézier span. This script checks the
claim with an independent evaluator: it hands the six points to Blender, asks
Blender for the curve's vertices, and compares them with the Bernstein sum
computed here.

    python scripts/check_blender_quintic.py
    python scripts/check_blender_quintic.py --points "0,0 24,36 48,54 72,54 96,36 120,0"

Exit 0 when Blender's curve and ours agree to `--tolerance` px (default 1e-4),
1 otherwise. Blender is 4.2.23 LTS at /Applications/Blender.app; override with
`--blender`.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inkscape import quintic_math as qm  # noqa: E402

BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
READER = ROOT / "scripts" / "blender_read_quintic.py"
DEFAULT = [(0, 0), (24, 36), (48, 54), (72, 54), (96, 36), (120, 0)]


def parse_points(text):
    points = []
    for pair in text.replace(";", " ").split():
        x, y = pair.split(",")
        points.append((float(x), float(y)))
    if len(points) != 6:
        raise SystemExit("a quintic needs six points, got %d" % len(points))
    return points


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--points", help="six 'x,y' pairs, space separated")
    parser.add_argument("--resolution", type=int, default=60,
                        help="Blender's resolution_u; the mesh has one vertex per step")
    parser.add_argument("--tolerance", type=float, default=1e-4,
                        help="largest allowed deviation, in px")
    parser.add_argument("--blender", default=BLENDER)
    args = parser.parse_args()

    control = parse_points(args.points) if args.points else DEFAULT
    if not Path(args.blender).exists():
        raise SystemExit("no Blender at %s" % args.blender)

    with tempfile.TemporaryDirectory() as tmp:
        points_path = Path(tmp) / "points.json"
        points_path.write_text(json.dumps({"points": [list(p) for p in control]}))
        command = [args.blender, "-b", "--factory-startup", "-P", str(READER),
                   "--", str(points_path), str(args.resolution)]
        done = subprocess.run(command, capture_output=True, text=True)
        if done.returncode != 0:
            print("Blender failed (%d):" % done.returncode)
            print(done.stderr[-2000:])
            return 1
        payload = None
        for line in done.stdout.splitlines():
            if line.startswith("QUINTIC_VERTICES "):
                payload = json.loads(line[len("QUINTIC_VERTICES "):])
    if payload is None:
        print("Blender printed no vertices; stderr tail:")
        print(done.stderr[-2000:])
        return 1

    vertices = payload["vertices"]
    # Blender's resolution_u is per curve edge, so the mesh carries
    # (points - 1) * resolution vertices across the single span. The parameter
    # runs 0..1 over the whole span either way, so compare like for like.
    count = len(vertices)
    ours = [qm.evaluate(control, k / (count - 1)) for k in range(count)]
    worst = max(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
                for a, b in zip(vertices, ours))
    mode = "vertex by vertex, t = k/%d" % (count - 1)

    print("control points: %s" % ", ".join("%g,%g" % p for p in control))
    print("Blender: %d vertices at resolution %d, %s"
          % (len(vertices), payload["resolution"], mode))
    print("largest deviation from the Bernstein sum: %.9f px" % worst)
    if worst <= args.tolerance:
        print("ok — Blender's order-6 clamped spline is our quintic")
        return 0
    print("FAIL — above the tolerance %.9f px" % args.tolerance)
    return 1


if __name__ == "__main__":
    sys.exit(main())
