"""Export the book plates: SVG, PNG, a plain gallery, and a manifest check.

    .venv/bin/python scripts/plate_export.py

Reads `book/plates.json`. For each plate: draws the spine and its two rails,
takes the bounding box of all three, and fills a canvas whose aspect is that
box, so the curve is as large as the image allows. White ground, dark ink, no
text on the image. Writes

    book/svg/<id>.svg       the plate, standalone
    book/plates/<id>.png    300 dpi, long side from the manifest
    book/render.html        the page the screenshots are taken from
    book/index.html         the plain gallery, no controls

The PNGs are rasterised by `scripts/plate_png.mjs` (Playwright, element
screenshot at the exact size), then stamped 300 dpi by `png_dpi.py`.

Naming: `<descriptor>-<variant>-t-exp-c-<serial>`. The serial is allocated once
in the manifest, so a re-export keeps the name and LibreOffice keeps the link.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import plate_curves  # noqa: E402
from png_dpi import read_dpi, set_dpi  # noqa: E402

BOOK = ROOT / "book"
SVG_DIR = BOOK / "svg"
PNG_DIR = BOOK / "plates"
NAME = re.compile(r"^([a-z][a-z0-9]*)-([0-9]+)-t-exp-c-([0-9]{4})$")
MARGIN_SHARE = 0.012
DPI = 300


def _manifest():
    path = BOOK / "plates.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    seen = set()
    for plate in data["plates"]:
        match = NAME.match(plate["id"])
        if not match:
            raise ValueError(f"{plate['id']}: name must be "
                             "<descriptor>-<variant>-t-exp-c-<4 digits>")
        descriptor, variant, serial = match.groups()
        if descriptor != plate["descriptor"] or int(variant) != int(plate["variant"]):
            raise ValueError(f"{plate['id']}: the name and the fields disagree")
        if serial in seen:
            raise ValueError(f"{plate['id']}: serial {serial} is used twice")
        seen.add(serial)
    return data


def _polyline(points, to_pixels, stroke) -> str:
    text = " ".join(f"{to_pixels(p)[0]:.1f},{to_pixels(p)[1]:.1f}"
                    for p in points)
    return (f'<polyline points="{text}" fill="none" stroke="#111111" '
            f'stroke-width="{stroke:.2f}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def draw(plate, long_side, stroke_share):
    """The SVG, its pixel size, and the numbers the table prints."""
    data = plate_curves.load(plate)
    x0, y0, x1, y1 = data["bbox"]
    width, height = x1 - x0, y1 - y0
    if width >= height:
        px_w, px_h = long_side, max(1, round(long_side * height / width))
    else:
        px_h, px_w = long_side, max(1, round(long_side * width / height))
    margin = round(MARGIN_SHARE * long_side)
    inner_w, inner_h = px_w - 2 * margin, px_h - 2 * margin
    scale = min(inner_w / width, inner_h / height)
    offset_x = (inner_w - width * scale) / 2
    offset_y = (inner_h - height * scale) / 2

    def to_pixels(point):
        x = margin + offset_x + (point[0] - x0) * scale
        y = px_h - (margin + offset_y + (point[1] - y0) * scale)   # +y up -> SVG y down
        return x, y

    stroke = max(1.0, stroke_share * long_side)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{px_w}" '
             f'height="{px_h}" viewBox="0 0 {px_w} {px_h}">',
             f'<rect width="{px_w}" height="{px_h}" fill="#ffffff"/>']
    parts.append(_polyline(data["spine"], to_pixels, stroke))
    for rail in data["rails"]:
        parts.append(_polyline(rail, to_pixels, stroke))
    parts.append("</svg>")
    return "".join(parts), px_w, px_h, data


def render_page(plates) -> str:
    body = "".join(
        f'<div class="plate" id="plate-{plate["id"]}" '
        f'style="width:{plate["pxW"]}px;height:{plate["pxH"]}px">{plate["svg"]}</div>'
        for plate in plates)
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<title>plate render</title><style>html,body{margin:0;padding:0;'
            'background:#fff}.plate{background:#fff;overflow:hidden;line-height:0}'
            '</style></head><body>' + body + '</body></html>')


def gallery(plates) -> str:
    cards = "".join(
        f'<figure><img src="plates/{plate["id"]}.png" width="{plate["pxW"]}" '
        f'height="{plate["pxH"]}" alt="{plate["id"]}">'
        f'<figcaption><b>{plate["id"]}</b><br>{plate["note"]}</figcaption></figure>'
        for plate in plates)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Book plates — temporary export</title>
<style>
body{{margin:0;background:#fff;color:#111;font:14px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:30px 22px 60px}}
h1{{font-size:22px;margin:0 0 4px}}
.lead{{color:#666;margin:0 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:26px}}
figure{{margin:0}}
img{{width:100%;height:auto;display:block;border:1px solid #eee}}
figcaption{{font:11px/1.5 ui-monospace,Menlo,monospace;color:#555;margin-top:6px}}
</style></head><body><main>
<h1>Book plates — temporary export</h1>
<p class="lead">{len(plates)} plates · white ground, no text on the image,
tight to the curve · labels outside the image, two columns · names are
<code>&lt;descriptor&gt;-&lt;variant&gt;-t-exp-c-&lt;serial&gt;</code></p>
<div class="grid">{cards}</div>
</main></body></html>
'''


def main() -> int:
    manifest = _manifest()
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    plates = []
    for spec in manifest["plates"]:
        svg, px_w, px_h, data = draw(spec, manifest["longSide"],
                                     manifest["strokeShare"])
        (SVG_DIR / f"{spec['id']}.svg").write_text(svg, encoding="utf-8")
        plates.append({"id": spec["id"], "svg": svg, "pxW": px_w, "pxH": px_h,
                       "note": spec["note"], "data": data, "kind": spec["kind"]})

    render = BOOK / "render.html"
    render.write_text(render_page(plates), encoding="utf-8")
    result = subprocess.run(["node", str(ROOT / "scripts" / "plate_png.mjs"),
                             str(render), str(PNG_DIR)],
                            cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout[-1200:])
        print(result.stderr[-1200:])
        return 1

    print(f"{'plate':26} {'kind':7} {'d':>8} {'|d.k|':>6} {'pixels':>11} {'dpi':>4} {'bytes':>8}")
    for plate in plates:
        path = PNG_DIR / f"{plate['id']}.png"
        if not path.exists():
            print(f"{plate['id']}: no PNG written")
            return 1
        set_dpi(path, DPI)
        data = plate["data"]
        print(f"{plate['id']:26} {plate['kind']:7} {data['distance']:8.4f} "
              f"{data['fold']:6.3f} {plate['pxW']:5}x{plate['pxH']:<5} "
              f"{read_dpi(path):4} {path.stat().st_size:8}")
    (BOOK / "index.html").write_text(gallery(plates), encoding="utf-8")
    print(BOOK / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
