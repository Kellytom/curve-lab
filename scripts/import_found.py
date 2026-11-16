"""Import named curves from the found file into `curves/`, with a factored figure.

    .venv/bin/python scripts/import_found.py wide-knot-x20 lace-1of8-1of3-3 ...

The gallery's thumbnails frame on the knot and draw from the speed row, so a curve with
long legs and a small knot comes out as a smudge. A folder here gets a figure drawn from
the flat spots, with the loop window recorded and the vertical stretch stated, so the
shape is legible. The record keeps the row; the figure is a drawing of it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import curve_files  # noqa: E402

FOUND = ROOT / "workbench" / "found-curves.json"


def entry_for(curve):
    rows = {}
    for term in curve["terms"]:
        rows[int(term["power"])] = [term["x"], term["y"]]
    top = max(rows) if rows else 0
    speed_x = [rows.get(power, [0, 0])[0] for power in range(top + 1)]
    speed_y = [rows.get(power, [0, 0])[1] for power in range(top + 1)]
    roots = curve.get("provenance", {}).get("roots", "")
    if any(not part.strip().split("/")[0].isdigit() for part in roots.split(",")):
        roots = ""            # a prose provenance cannot go on a ruler
    loop, bend = curve_files.measure(speed_x, speed_y)
    measured = curve.get("measured", {})
    return {"name": curve["name"], "speedX": speed_x, "speedY": speed_y, "step": 1,
            "roots": roots, "loop": loop, "bend": bend,
            "grid": measured.get("grid"), "crossings": measured.get("self"),
            "arc": str(curve_files._arc(speed_x, speed_y)),
            "source": f"workbench/found-curves.json; {curve.get('provenance', {}).get('batch', '')} batch"}


def main():
    names = sys.argv[1:]
    if not names:
        print("name one or more curves from workbench/found-curves.json")
        return
    document = json.loads(FOUND.read_text())
    for name in names:
        curve = next((item for item in document["curves"] if item["name"] == name), None)
        if curve is None:
            print(f"{name}: not in the found file")
            continue
        entry = entry_for(curve)
        entry["figure"] = {"file": "figure.png", "view": "factored",
                           "aspect": "auto", "balance": None,
                           "drawn_by": "scripts/curve_svg.py + scripts/svg_png.mjs"}
        slug, record = curve_files.write_curve(entry, 0, 900)
        folder = ROOT / "curves" / slug
        # the figure spec must be in the record BEFORE the drawing: the stretch is read
        # from it, and write_curve's default spec has none
        record = json.loads((folder / "curve.json").read_text())
        record["figure"] = {"file": "figure.png", "view": "factored", "aspect": "auto",
                            "balance": None,
                            "drawn_by": "scripts/curve_svg.py + scripts/svg_png.mjs"}
        (folder / "curve.json").write_text(json.dumps(record, indent=1) + "\n")
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "scripts" / "curve_svg.py"),
                        str(folder / "curve.json"), str(folder / "figure-exact.svg")], check=True,
                       capture_output=True)
        subprocess.run(["node", str(ROOT / "scripts" / "svg_png.mjs"),
                        str(folder / "figure-exact.svg"), str(folder / "figure.png"), "900"],
                       check=True, capture_output=True)
        print(f"curves/{slug}/  crossings {entry['crossings']}  grid 1/{entry['grid']}")


if __name__ == "__main__":
    main()
