#!/usr/bin/env python3
"""Image → equations: a reference figure traced into cubic spans.

    .venv/bin/python deep2/trace.py refs/sacred-heart-statue-02.jpg

The pipeline, each step visible:
  1. mask the FIGURE from the background (the background here is green and
     out of focus; the figure is warm — colour separates them cleanly);
  2. keep the largest component and fill it (the figure, not the bokeh);
  3. potrace the mask into cubic Béziers (potrace is the standard bitmap →
     outline tool, and it speaks SVG);
  4. read those cubics back into our span dicts (p0, c1, c2, p3), y flipped
     to the project's y-up and scaled to the millimetre sheet later — for now
     normalised to the figure's own bounding box;
  5. write the spans as JSON and an SVG drawn from THEM (not from potrace),
     so what we see is the data we would use.

The output is the figure as equations — the first step toward the canonical
construction. It is a TRACE, not a construction: the spans are approximate
between stations, and the report says so.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent


def lithograph_mask(image: Image.Image) -> np.ndarray:
    """Figure vs cream paper, by flood-filling the paper from the borders.

    For a lithograph/holy card the paper is a warm cream; the figure is
    anything the cream fill cannot reach. Robust to the printed border and
    the rays, which are inside the paper region but part of the drawing."""
    from scipy import ndimage as ndi
    rgb = np.asarray(image.convert("RGB"), dtype=np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    paper = (r > 195) & (g > 180) & (b > 140) & (r >= b + 15)
    seeds = np.zeros_like(paper)
    seeds[0, :] = seeds[-1, :] = seeds[:, 0] = seeds[:, -1] = True
    # the printed frame line blocks the flood, so seed inside it as well:
    # the lithograph's own cream background sits just inside the frame
    h, w = paper.shape
    for fy in (0.06, 0.94):
        for fx in (0.06, 0.94):
            seeds[int(fy * h), int(fx * w)] = True
    reached = ndi.binary_propagation(seeds & paper, mask=paper, structure=np.ones((3, 3)))
    # the figure is ENCLOSED by paper, so no hole-filling here (fill_holes
    # swallowed the whole figure on the first run); it is simply what the
    # paper flood cannot reach
    mask = ~reached
    mask = ndi.binary_opening(mask, iterations=2)
    mask = ndi.binary_closing(mask, iterations=2)
    return mask


def otsu(values: np.ndarray) -> float:
    """Otsu's threshold: the cut that separates two brightness populations."""
    hist, edges = np.histogram(values, bins=256, range=(0, 255))
    hist = hist.astype(float)
    total = hist.sum()
    if total == 0:
        return 128.0
    p = hist / total
    centres = (edges[:-1] + edges[1:]) / 2
    omega = np.cumsum(p)
    mu = np.cumsum(p * centres)
    mu_t = mu[-1]
    denom = omega * (1 - omega)
    denom[denom == 0] = 1e-12
    sigma_b = (mu_t * omega - mu) ** 2 / denom
    return float(centres[int(np.argmax(sigma_b))])


def silhouette_mask(image: Image.Image) -> np.ndarray:
    """Dark figure against a bright sky, cut by Otsu on luminance — the case
    that needs no colour reasoning at all."""
    from scipy import ndimage as ndi
    gray = np.asarray(image.convert("L"), dtype=np.float64)
    cut = otsu(gray)
    mask = gray < cut
    mask = ndi.binary_opening(mask, iterations=1)
    mask = ndi.binary_closing(mask, iterations=1)
    labels, count = ndi.label(mask)
    if count == 0:
        raise SystemExit("no silhouette found")
    sizes = ndi.sum(mask, labels, range(1, count + 1))
    return labels == (int(np.argmax(sizes)) + 1)


def figure_mask(image: Image.Image) -> np.ndarray:
    """True where the figure is: not the green, bright-focus background."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green = (g - np.maximum(r, b)) > 8           # the foliage is green-dominant
    # the bokeh is foliage-lit white (g >= r); the pale statue is pink-beige
    # (r > g by ten levels). Brightness alone cannot separate them — the first
    # runs masked the statue as background.
    bokeh = (rgb.sum(axis=2) > 330) & (g >= r - 2)
    background = green | bokeh
    mask = ~background
    # close small holes and drop specks, then keep the biggest component
    from scipy import ndimage as ndi
    mask = ndi.binary_closing(mask, iterations=3)
    mask = ndi.binary_opening(mask, iterations=1)
    labels, count = ndi.label(mask)
    if count == 0:
        raise SystemExit("no figure found")
    sizes = ndi.sum(mask, labels, range(1, count + 1))
    keep = int(np.argmax(sizes)) + 1
    mask = labels == keep
    mask = ndi.binary_fill_holes(mask)
    return mask


def write_pbm(mask: np.ndarray, path: Path) -> None:
    """P4 bitmap; potrace treats BLACK (1) as the shape to trace, so the
    figure's True pixels are written as 1 — not inverted (the first run
    traced the background by getting this backwards)."""
    h, w = mask.shape
    rows = [np.packbits(mask[y].astype(np.uint8), bitorder="big").tobytes()
            for y in range(h)]
    header = f"P4\n{w} {h}\n".encode()
    path.write_bytes(header + b"".join(rows))


def parse_svg_cubics(svg_text: str):
    """Cubic spans out of potrace's SVG path data, in pixels.

    potrace writes both absolute (M, L, C) and RELATIVE (l, c, v, h) commands,
    with repeated coordinate sets implying a repeat of the last command — a
    real token walk, not a grep for 'C'."""
    import re
    d = re.search(r'<path[^>]*\sd="([^"]+)"', svg_text)
    if not d:
        raise SystemExit("no path in the potrace SVG")
    raw = re.findall(r"[MmLlHhVvCcZz]|-?\d*\.?\d+", d.group(1))
    spans = []
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    cmd = None
    i = 0
    while i < len(raw):
        tok = raw[i]
        if tok.isalpha():
            cmd = tok
            i += 1
            continue
        if cmd in ("M", "L", "m", "l"):
            rel = cmd.islower()
            x, y = float(raw[i]), float(raw[i + 1])
            nxt = (cur[0] + x, cur[1] + y) if rel else (x, y)
            if cmd in ("M", "m"):
                start = nxt
                cmd = "l" if rel else "L"  # an implicit lineto after a moveto
            cur, i = nxt, i + 2
        elif cmd in ("v", "V"):
            y = float(raw[i])
            cur = (cur[0], cur[1] + y) if cmd == "v" else (cur[0], y)
            i += 1
        elif cmd in ("h", "H"):
            x = float(raw[i])
            cur = (cur[0] + x, cur[1]) if cmd == "h" else (x, cur[1])
            i += 1
        elif cmd in ("c", "C"):
            rel = cmd.islower()
            vals = [float(v) for v in raw[i:i + 6]]
            if rel:
                c1 = (cur[0] + vals[0], cur[1] + vals[1])
                c2 = (cur[0] + vals[2], cur[1] + vals[3])
                p3 = (cur[0] + vals[4], cur[1] + vals[5])
            else:
                c1, c2, p3 = (vals[0], vals[1]), (vals[2], vals[3]), (vals[4], vals[5])
            spans.append({"p0": cur, "c1": c1, "c2": c2, "p3": p3})
            cur, i = p3, i + 6
        elif cmd in ("z", "Z"):
            cur = start
            i += 1
        else:
            i += 1
    return spans


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    ref = (HERE / argv[0]).resolve() if not Path(argv[0]).is_absolute() else Path(argv[0])
    image = Image.open(ref)
    # work at a print-plate scale: 900 px on the long side
    scale = 900 / max(image.size)
    image = image.resize((round(image.width * scale), round(image.height * scale)))
    mode = "photo"
    if "--lithograph" in argv:
        mode = "lithograph"
    if "--silhouette" in argv:
        mode = "silhouette"
    if "--crop" in argv:
        box = [int(v) for v in argv[argv.index("--crop") + 1].split(",")]
        image = image.crop(tuple(box))
    if "--outname" in argv:
        stem_override = argv[argv.index("--outname") + 1]
    mask = (lithograph_mask(image) if mode == "lithograph"
            else silhouette_mask(image) if mode == "silhouette"
            else figure_mask(image))

    stem = locals().get("stem_override") or ref.stem
    (HERE / "out").mkdir(exist_ok=True)
    pbm = HERE / "out" / f"{stem}.pbm"
    write_pbm(mask, pbm)

    svg_path = HERE / "out" / f"{stem}-potrace.svg"
    subprocess.run(
        ["/usr/local/bin/potrace", "-s", "-o", str(svg_path),
         "--turdsize", "40", "--alphamax", "1.0", str(pbm)],
        check=True, capture_output=True,
    )
    spans_px = parse_svg_cubics(svg_path.read_text())

    # normalise: y up, unit scale on the figure's bounding box
    xs = [v for s in spans_px for v in (s["p0"][0], s["c1"][0], s["c2"][0], s["p3"][0])]
    ys = [v for s in spans_px for v in (s["p0"][1], s["c1"][1], s["c2"][1], s["p3"][1])]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    height = y1 - y0 or 1

    def norm(p):
        return [round((p[0] - x0) / height, 5), round((y1 - p[1]) / height, 5)]

    spans = [{"p0": norm(s["p0"]), "c1": norm(s["c1"]),
              "c2": norm(s["c2"]), "p3": norm(s["p3"])} for s in spans_px]

    payload = {
        "reference": ref.name,
        "source": "wikimedia commons, modified by tracing (deep2)",
        "method": "colour mask → potrace cubics → spans; approximate between endpoints",
        "spans": len(spans),
        "bbox": [x0, y0, x1, y1],
        "curves": spans,
    }
    out_json = HERE / "spans" / f"{stem}.json"
    out_json.write_text(json.dumps(payload, indent=1))

    # draw OUR spans, not potrace's file — one path, M + C per span
    def f(v):
        return f"{min(1.0, max(0.0, v)):.4f}"

    parts = [f"M {f(spans[0]['p0'][0])} {f(spans[0]['p0'][1])}"] if spans else []
    for s in spans:
        parts.append(f"C {f(s['c1'][0])} {f(s['c1'][1])} {f(s['c2'][0])} {f(s['c2'][1])} "
                     f"{f(s['p3'][0])} {f(s['p3'][1])}")
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -0.05 1 1.1" '
           'width="600" height="660">'
           '<rect x="0" y="-0.05" width="1" height="1.1" fill="#fffef9"/>'
           f'<path d="{" ".join(parts)}" fill="none" stroke="#3b2d1c" stroke-width="0.004"/>'
           '</svg>')
    out_svg = HERE / "out" / f"{stem}-spans.svg"
    out_svg.write_text(svg)

    print(f"{ref.name}: {len(spans)} cubic spans · bbox {x0:.0f},{y0:.0f} → {x1:.0f},{y1:.0f}")
    print(f"  spans  {out_json.relative_to(HERE)}")
    print(f"  drawn  {out_svg.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
