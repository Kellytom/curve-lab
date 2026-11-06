"""Put a design grid, and its intersections, behind any rendered SVG.

Some figures are built in page space by their own writer, with no model
coordinates left to hang a lattice on. This pass works on the finished SVG:
read the viewBox, lay a round grid of ~10 lines over it, then walk every path's
points and mark the crossing with each grid line. One implementation, so a
figure drawn by any script reads the same.

    python scripts/overlay_lattice.py workbench/stage-two.html

The grid is in page units (y down, as SVG has it); the marks are the points
where the ink meets a rule, which is the hit count this project cares about.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

RULE = "#e8dfc9"
MARK = "#c9a441"
MAX_MARKS = 24


def _step(span: float, target: int = 10) -> float:
    if span <= 0:
        return 1.0
    raw = span / target
    p = 10.0 ** math.floor(math.log10(raw))
    for k in (1.0, 2.0, 2.5, 5.0, 10.0):
        if raw <= k * p:
            return k * p
    return 10.0 * p


def _points(d: str) -> list[tuple[float, float]]:
    nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
    return list(zip(nums[0::2], nums[1::2]))


def _sub_paths(d: str) -> list[list[tuple[float, float]]]:
    out = []
    for part in re.split(r"(?=[Mm])", d):
        pts = _points(part)
        if len(pts) > 1:
            out.append(pts)
    return out


def decorate(svg: str) -> str:
    """Return `svg` with a grid and its intersections, or unchanged."""
    if svg.count("<line") >= 2 or "<path" not in svg:
        return svg
    m = re.search(r'viewBox="([-\d.\s]+)"', svg)
    if not m:
        return svg
    x0, y0, vw, vh = (float(v) for v in m.group(1).split())
    ds = re.findall(r'<path[^>]*\sd="([^"]+)"', svg)
    curves = [p for d in ds for p in _sub_paths(d)]
    if not curves:
        return svg
    step = _step(max(vw, vh))
    body = []
    gx = math.ceil(x0 / step) * step
    while gx <= x0 + vw + 1e-9:
        body.append(f'<line x1="{gx:.1f}" y1="{y0:.1f}" x2="{gx:.1f}" '
                    f'y2="{y0 + vh:.1f}" stroke="{RULE}"/>')
        gx += step
    gy = math.ceil(y0 / step) * step
    while gy <= y0 + vh + 1e-9:
        body.append(f'<line x1="{x0:.1f}" y1="{gy:.1f}" x2="{x0 + vw:.1f}" '
                    f'y2="{gy:.1f}" stroke="{RULE}"/>')
        gy += step
    marks, seen = [], set()
    for pts in curves:
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if bx != ax:
                g = math.ceil(min(ax, bx) / step) * step
                while g <= max(ax, bx) + 1e-9:
                    t = (g - ax) / (bx - ax)
                    if 0.0 <= t <= 1.0:
                        key = (round(g, 3), round((ay + t * (by - ay)) / step))
                        if key not in seen:
                            seen.add(key)
                            marks.append((g, ay + t * (by - ay)))
                    g += step
            if by != ay:
                g = math.ceil(min(ay, by) / step) * step
                while g <= max(ay, by) + 1e-9:
                    t = (g - ay) / (by - ay)
                    if 0.0 <= t <= 1.0:
                        key = (round((ax + t * (bx - ax)) / step), round(g, 3))
                        if key not in seen:
                            seen.add(key)
                            marks.append((ax + t * (bx - ax), g))
                    g += step
    if len(marks) > MAX_MARKS:
        stride = len(marks) / MAX_MARKS
        marks = [marks[int(i * stride)] for i in range(MAX_MARKS)]
    for mx, my in marks:
        body.append(f'<circle class="lattice" cx="{mx:.1f}" cy="{my:.1f}" '
                    f'r="2.0" fill="{MARK}"/>')
    insert = "".join(body)
    # draw behind the ink: after the background rect, else just inside <svg>
    out, n = re.subn(r'(<rect[^>]*/>)', r"\1" + insert, svg, count=1)
    if not n:
        out, n = re.subn(r'(<svg[^>]*>)', r"\1" + insert, svg, count=1)
    return out


def overlay_html(text: str) -> str:
    return re.sub(r"<svg.*?</svg>", lambda m: decorate(m.group(0)), text,
                  flags=re.S)


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv[1:]]
    if not files:
        files = sorted(Path("workbench").glob("*.html"))
    for path in files:
        raw = path.read_text(encoding="utf-8")
        new = overlay_html(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
