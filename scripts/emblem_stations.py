#!/usr/bin/env python3
"""Emblem stations from the registry's own speed rows — exact, no conics.

The operator's direction (2026-11-23): "closely read llm.txt and ltmemory and
try again. that means no simple circles ellipses, or conic sections." So this
desk uses only the collection's own exact curves: speed rows from
`workbench/curve-registry.json`, turned into position polynomials by the one
exact core (`curve_lab/ph_offset.py`: u²−v², 2uv, integrated in Fraction).
The emblems are compositions of those curves by mirror and exact quarter
turns — no circle, ellipse or conic section appears anywhere.

Output: `workbench/emblem-stations.json`, read by
`app/src/pages/figure-desk.astro` (the same pattern as prime-mover's
circle-plots.json). Floats are for plotting only; each panel also carries one
exact sample, `x(1/2) = …`, printed on the page as proof.

`--sheet` writes the candidate contact sheet instead (workbench/
emblem-contact-sheet.svg).
"""

import json
import sys
from fractions import Fraction

sys.path.insert(0, ".")
from curve_lab import ph_offset  # noqa: E402

REGISTRY = "workbench/curve-registry.json"
OUT = "workbench/emblem-stations.json"
N = 40  # stations per curve


def load_curve(curves, uid):
    rec = next(c for c in curves if c["uid"] == uid)
    assert rec.get("kind") == "rows", f"{uid} is not a speed-row curve"
    u = [Fraction(str(c)) for c in rec["speedX"]]
    v = [Fraction(str(c)) for c in rec["speedY"]]
    return u, v, rec


def exact_stations(u, v, n=N):
    """Exact stations of the speed rows' curve, in Fraction."""
    x_poly, y_poly = ph_offset.curve(u, v)
    return [(ph_offset.evaluate(x_poly, Fraction(i, n)),
             ph_offset.evaluate(y_poly, Fraction(i, n))) for i in range(n + 1)]


def floats(sts):
    return [[float(x), float(y)] for x, y in sts]


def mirror_x(sts):
    return [[-x, y] for x, y in sts]


def quarter_turn(sts):
    """Rotate 90° exactly: (x, y) -> (−y, x). No trigonometry."""
    return [[-y, x] for x, y in sts]


def bbox(panel_sts):
    all_pts = [p for sts in panel_sts for p in sts]
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    return [min(xs), max(xs), min(ys), max(ys)]


def sample_string(sts):
    x, y = sts[len(sts) // 2]
    return f"x(1/2) = {x}, y(1/2) = {y}"


def panel(key, title, parts, samples):
    flat = [p for part in parts for p in part]
    return {
        "key": key, "title": title,
        "legend": ["stations — exact rational points of the registry's speed rows"],
        "stations": floats(flat),
        "bounds": [float(value) for value in bbox(parts)],
        "samples": samples,
    }


def main(sheet_mode=False):
    reg = json.load(open(REGISTRY))
    curves = reg["curves"] if isinstance(reg, dict) else reg

    if sheet_mode:
        candidates = ["c-0003", "c-0005", "c-0006", "c-0007", "c-0013",
                      "c-0014", "c-0031", "c-0032", "c-0033", "c-0034", "c-0036"]
        sheet = {}
        for uid in candidates:
            u, v, rec = load_curve(curves, uid)
            sheet[uid] = (rec.get("name", uid), rec.get("family"),
                          floats(exact_stations(u, v)))
        contact_sheet(sheet)
        return

    # --- the panels -----------------------------------------------------
    panels = []

    # 1. the fish: one wave curve over its mirror, nose to nose
    u, v, rec = load_curve(curves, "c-0014")
    wave = exact_stations(u, v)
    panels.append(panel(
        "fish", f"Fig. F — the fish: {rec['name']} (c-0014) over its mirror",
        [wave, mirror_x(wave)],
        [f"c-0014: {sample_string(wave)}"]))

    # 2. the sprig: one grass stroke and its mirror — two blades from one curve
    u, v, rec = load_curve(curves, "c-0007")
    grass = exact_stations(u, v)
    panels.append(panel(
        "sprig", f"Fig. G — the sprig: {rec['name']} (c-0007) and its mirror",
        [grass, mirror_x(grass)],
        [f"c-0007: {sample_string(grass)}"]))

    # 3. the rosette: one swan stroke walked around by exact quarter turns
    u, v, rec = load_curve(curves, "c-0003")
    swan = exact_stations(u, v)
    arms = [swan]
    for _ in range(3):
        arms.append(quarter_turn(arms[-1]))
    panels.append(panel(
        "rosette", f"Fig. R — the rosette: {rec['name']} (c-0003) turned by "
        "three exact quarter turns",
        arms, [f"c-0003: {sample_string(swan)}"]))

    # 4. the band: wave-middle-5 over its mirror — an ornament border
    u, v, rec = load_curve(curves, "c-0033")
    band = exact_stations(u, v)
    panels.append(panel(
        "band", f"Fig. B — the band: {rec['name']} (c-0033) over its mirror",
        [band, mirror_x(band)],
        [f"c-0033: {sample_string(band)}"]))

    # 5. the fish row: the same composition, three waves from the family
    for k, uid in enumerate(["c-0014", "c-0031", "c-0032"]):
        u, v, rec = load_curve(curves, uid)
        w = exact_stations(u, v)
        panels.append(panel(
            f"fish-row-{k}", f"flare family · {rec['name']} ({uid}) over its mirror",
            [w, mirror_x(w)], [f"{uid}: {sample_string(w)}"]))

    out = {"format": "curve-lab.emblem-stations/1", "stations_per_curve": N,
           "no_conics": "every panel is a speed-row curve of the registry, "
                        "mirrored or quarter-turned; no circle, ellipse or "
                        "conic section is plotted",
           "panels": panels}
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {OUT}: {len(panels)} panels, "
          f"{sum(len(p['stations']) for p in panels)} plotted stations")
    for p in panels:
        print(f"  {p['key']}: {len(p['stations'])} dots  |  {p['samples'][0]}")


def contact_sheet(sheet):
    cols, cell = 5, 150
    keys = list(sheet)
    rows = (len(keys) + cols - 1) // cols
    w, h = cols * cell, rows * cell
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}" font-family="Helvetica" font-size="9">']
    svg.append(f'<rect width="{w}" height="{h}" fill="white"/>')
    for i, uid in enumerate(keys):
        name, fam, pts = sheet[uid]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        s = min((cell - 24) / (max(xs) - min(xs) or 1),
                (cell - 24) / (max(ys) - min(ys) or 1))
        cx0 = (i % cols) * cell + 12
        cy0 = (i // cols) * cell + 12
        dots = " ".join(
            f'{cx0 + (x - min(xs)) * s:.1f},{cy0 + (max(ys) - y) * s:.1f}'
            for x, y in pts)
        svg.append(f'<polyline points="{dots}" fill="none" stroke="#ccc" '
                   f'stroke-width="0.6"/>')
        svg.append('<g fill="#c9761f">' + "".join(
            f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="1.4"/>'
            for p in dots.split()) + "</g>")
        svg.append(f'<text x="{cx0}" y="{cy0 + cell - 4}" fill="#333">'
                   f'{name} ({uid})</text>')
    svg.append("</svg>")
    with open("workbench/emblem-contact-sheet.svg", "w") as f:
        f.write("".join(svg))
    print("contact sheet: workbench/emblem-contact-sheet.svg")
    for uid, (name, fam, _) in sheet.items():
        print(f"  {uid}: {name} ({fam})")


if __name__ == "__main__":
    main(sheet_mode="--sheet" in sys.argv)
