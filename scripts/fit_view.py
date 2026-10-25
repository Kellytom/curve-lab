"""Set the saved Inkscape view so a drawing opens fitted, not at 100%.

Inkscape stores the view in `sodipodi:namedview` as `inkscape:zoom` (a factor,
1.0 = 100%), `inkscape:cx` and `inkscape:cy` (the view centre in user units).
It does not store pixels per millimetre.

So the fit factor is:

    zoom = min((window_w - pad) / (page_w * PX_PER_MM),
               (window_h - chrome - pad) / (page_h * PX_PER_MM))

with PX_PER_MM = 96 / 25.4. The window frame comes from Inkscape's preferences.

    python scripts/fit_view.py out/play.svg
    python scripts/fit_view.py out/play.svg --zoom 0.75
"""

from __future__ import annotations

import argparse
import os
import re
import sys

PX_PER_MM = 96.0 / 25.4
PREFS = os.path.expanduser(
    "~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/preferences.xml")


def page_size(svg: str) -> tuple[float, float]:
    def value(name: str) -> float:
        match = re.search(rf'{name}="([0-9.]+)mm"', svg)
        if not match:
            raise SystemExit(f"the SVG has no {name} in mm; cannot compute a fit")
        return float(match.group(1))
    return value("width"), value("height")


def window_size() -> tuple[float, float]:
    try:
        text = open(PREFS, "r", encoding="utf-8").read()
    except OSError:
        return 720.0, 800.0
    block = re.search(r'<group\b[^>]*id="geometry"[^>]*/>', text, re.S)
    if not block:
        return 720.0, 800.0
    attrs = block.group(0)
    width = re.search(r'width="([0-9.]+)"', attrs)
    height = re.search(r'height="([0-9.]+)"', attrs)
    return (float(width.group(1)) if width else 720.0,
            float(height.group(1)) if height else 800.0)


def fit_zoom(page: tuple[float, float], window: tuple[float, float],
             pad: float = 24.0, chrome: float = 80.0) -> float:
    width_px, height_px = window
    zoom_w = (width_px - pad) / (page[0] * PX_PER_MM)
    zoom_h = (height_px - chrome - pad) / (page[1] * PX_PER_MM)
    return max(0.05, min(zoom_w, zoom_h))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("svg")
    ap.add_argument("--zoom", type=float, default=None,
                    help="override the computed factor")
    ap.add_argument("--pad", type=float, default=24.0, help="pixels of margin")
    ap.add_argument("--chrome", type=float, default=80.0,
                    help="window pixels taken by title bar, menu and status bar")
    args = ap.parse_args(argv)

    with open(args.svg, "r", encoding="utf-8") as fh:
        text = fh.read()
    page = page_size(text)
    window = window_size()
    zoom = args.zoom if args.zoom is not None else fit_zoom(page, window,
                                                           args.pad, args.chrome)
    cx, cy = page[0] / 2.0, page[1] / 2.0

    if "<sodipodi:namedview" not in text:
        raise SystemExit("no sodipodi:namedview in the file to update")
    text = re.sub(r'inkscape:zoom="[^"]*"', f'inkscape:zoom="{zoom:.6g}"', text)
    text = re.sub(r'inkscape:cx="[^"]*"', f'inkscape:cx="{cx:g}"', text)
    text = re.sub(r'inkscape:cy="[^"]*"', f'inkscape:cy="{cy:g}"', text)
    with open(args.svg, "w", encoding="utf-8") as fh:
        fh.write(text)

    print(f"page {page[0]:g} x {page[1]:g} mm, window {window[0]:g} x {window[1]:g}")
    print(f"zoom {zoom:.4f} ({zoom * 100:.0f}%), centre ({cx:g}, {cy:g})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
