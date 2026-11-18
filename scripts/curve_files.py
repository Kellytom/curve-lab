"""Write one folder per curve: the record, the notes, and (on request) the figure.

    .venv/bin/python scripts/curve_files.py --example
    .venv/bin/python scripts/curve_files.py --from workbench/family-census.json --top 3
    .venv/bin/python scripts/curve_files.py --record some.json --png

The layout, so a curve is readable without opening the page:

    curves/
      README.md                 the format, in plain English
      index.json                every curve's numbers, one row each
      <slug>/
        curve.json              the record the page saves, plus its figure spec
        notes.md                variables, formula, plain explanation, provenance
        figure.png              the loop view, drawn by the page itself

One folder per curve, because a curve is read as a whole: the numbers, the sentence
that says what it looks like, and the picture. `index.json` is the only aggregate, so
adding a curve never rewrites its neighbours.

Expressions come from `workbench/family-census.json`, which carries the measured
crossings, grid and exact arc for every symmetric flat-spot family. The census stores
the flat spots, not the rows, so the rows are rebuilt here with the same function the
page uses.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from fractions import Fraction as F
from math import gcd, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_root_search as R  # noqa: E402
from ph_crossings import self_crossings  # noqa: E402

CURVES = ROOT / "curves"


def rows_from_spots(text):
    """The speed rows for a list like "1/15, 1/12, 1/2, 1/2, 1/2, 11/12, 14/15"."""
    spots = [F(part.strip()) for part in text.split(",") if part.strip()]
    y = R.row_from_roots(spots)
    x = [1, 0, 0] + [0] * max(0, len(y) - 3)
    n = max(len(x), len(y))
    return (x + [0] * (n - len(x)))[:n], (y + [0] * (n - len(y)))[:n]


def slug_of(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "curve"


def polynomial_text(coefficients, symbol="t"):
    parts = []
    for power, value in enumerate(coefficients):
        if not value:
            continue
        size = "" if abs(value) == 1 and power else str(abs(int(value)))
        term = f"{size}{symbol}^{power}" if power else f"{size}"
        parts.append(f"{'-' if value < 0 else '+'} {term}")
    text = " ".join(parts).lstrip("+ ").strip()
    return text or "0"


def notes_for(entry):
    x, y = entry["speedX"], entry["speedY"]
    spots = entry.get("roots") or entry.get("spots") or ""
    loop = entry.get("loop") or {}
    loop_text = (f"t {loop['from']} to {loop['to']}" if loop else "the whole of t")
    arc_value = F(str(entry["arc"]))
    arc_text = f"{float(arc_value):.4f}"
    return f"""# {entry['name']}

**In one line.** A curve whose speed is the polynomial below; {entry['crossings']} self-crossings,
grid 1/{entry['grid']}, arc {arc_text}.

## The formula

The speed is a complex polynomial, and the curve is its square, integrated:

```
w(t) = p(t) + i q(t)
z(t) = integral of w(t)^2 dt = integral of (p^2 - q^2) + i(2 p q) dt
```

```
p(t) = {polynomial_text(x)}
q(t) = {polynomial_text(y)}
```

Nothing here is sampled or fitted: the numbers are whole, so the arc length is a
polynomial integral and is exact.

## The variables

| symbol | meaning | value |
|---|---|---|
| `t` | the parameter, 0 at the start and 1 at the end | 0 to 1 |
| flat spots | where the tangent is horizontal, `q(t) = 0` | {spots or "not recorded"} |
| `bend` | arc length over the straight distance between the ends | {entry.get('bend') if entry.get('bend') else 'no value: the two ends land on the same point'} |
| `grid` | the pitch the whole rows need: 1 over this number | 1/{entry['grid']} |
| self-crossings | how many times the stroke meets itself | {entry['crossings']} |
| loop | the part of `t` that holds the knot | {loop_text} |
| step | the power step of the rows: 1 is whole powers | {entry.get('step', 1)} |

## How it was found

{entry.get('source', 'From the symmetric flat-spot census, scripts/family_census.py.')}

## The figure

`figure.png` is drawn by the page itself (`scripts/curve_png.mjs`), in the view
recorded in `curve.json`. Where a large row collapses to a flat line,
`figure-exact.png` holds the factored drawing. If the picture and the numbers
ever disagree, the numbers are right and the figure is stale — regenerate it
rather than trust it.
"""


def write_curve(entry, png, png_width):
    slug = slug_of(entry["name"])
    folder = CURVES / slug
    folder.mkdir(parents=True, exist_ok=True)
    record = {key: entry[key] for key in
              ("name", "speedX", "speedY", "step", "roots", "loop", "bend", "grid",
               "crossings", "arc", "source") if key in entry}
    record["format"] = "curve-lab.curve/1"
    record["figure"] = {"file": "figure.png", "view": "loop, focus the knot",
                        "width": png_width, "made_by": "scripts/curve_png.mjs"}
    (folder / "curve.json").write_text(json.dumps(record, indent=1) + "\n")
    (folder / "notes.md").write_text(notes_for(entry))
    if png:
        subprocess.run(["node", str(ROOT / "scripts" / "curve_png.mjs"),
                        str(folder / "curve.json"), str(folder / "figure.png"), str(png_width)],
                       check=True)
    return slug, record


def rebuild_index():
    rows = []
    for record_path in sorted(CURVES.glob("*/curve.json")):
        record = json.loads(record_path.read_text())
        rows.append({
            "slug": record_path.parent.name,
            "name": record.get("name"),
            "crossings": record.get("crossings"),
            "grid": record.get("grid"),
            "arc": record.get("arc"),
            "notes": f"{record_path.parent.name}/notes.md",
            "figure": f"{record_path.parent.name}/figure.png"
            if (record_path.parent / "figure.png").exists() else None,
        })
    rows.sort(key=lambda row: (-(row["crossings"] or 0), row["grid"] or 0))
    (CURVES / "index.json").write_text(json.dumps({"format": "curve-lab.index/1",
                                                    "curves": rows}, indent=1) + "\n")
    return rows


EXAMPLE = ("cheap-knot-9", "1/8, 1/11, 1/2, 10/11, 7/8", 9, 42, "1.4437",
           "the cheapest nine-crossing family in the census")
CHEAP = ("cheap-knot-6", "1/12, 1/13, 1/15, 1/2, 1/2, 1/2, 1/2, 1/2, 14/15, 12/13, 11/12",
         6, 6, "1.1493", "six crossings on grid 1/6, the cheapest knotty family found")


def from_census(names=None, top=0):
    census = json.loads((ROOT / "workbench" / "family-census.json").read_text())
    curves = census["curves"]
    if names:
        want = set(names)
        curves = [curve for curve in curves if curve["spots"] in want]
    curves = sorted(curves, key=lambda c: (-c["crossings"], c["grid"]))
    return curves[:top] if top else curves


def measure(x, y):
    """The loop window and the bend, measured the way the page measures them."""
    hits = self_crossings(x, y, samples=1024)
    if hits:
        low = min(min(hit["t1"], hit["t2"]) for hit in hits)
        high = max(max(hit["t1"], hit["t2"]) for hit in hits)
        loop = {"from": round(max(0.0, low - 0.02), 4), "to": round(min(1.0, high + 0.02), 4)}
    else:
        loop = None
    # the endpoint is the integral of w^2, exact
    n = max(len(x), len(y))
    xs = [F(str(value)) for value in x] + [F(0)] * (n - len(x))
    ys = [F(str(value)) for value in y] + [F(0)] * (n - len(y))
    end_x = sum(F(sum(xs[i] * xs[m - i] for i in range(n) if 0 <= m - i < n)
                  - sum(ys[i] * ys[m - i] for i in range(n) if 0 <= m - i < n), m + 1)
                for m in range(2 * n - 1))
    end_y = sum(F(2 * sum(xs[i] * ys[m - i] for i in range(n) if 0 <= m - i < n), m + 1)
                for m in range(2 * n - 1))
    chord = float((end_x ** 2 + end_y ** 2) ** F(1, 2)) if hasattr(end_x ** 2, "numerator") else 0.0
    arc = float(F(str(_arc(x, y))))
    return loop, (round(arc / chord, 3) if chord else None)


def _arc(x, y):
    n = max(len(x), len(y))
    xs = [F(str(value)) for value in x] + [F(0)] * (n - len(x))
    ys = [F(str(value)) for value in y] + [F(0)] * (n - len(y))
    total = F(0)
    for m in range(2 * n - 1):
        total += F(sum(xs[i] * xs[m - i] for i in range(n) if 0 <= m - i < n)
                   + sum(ys[i] * ys[m - i] for i in range(n) if 0 <= m - i < n), m + 1)
    return total


def name_from_spots(text):
    """A readable name: the outer denominators and the copies at 1/2.

    "1/3, 1/5, 1/11, 1/2, 1/2, 1/2, 10/11, 4/5, 2/3" -> "loop-3-5-11-mid-3".
    """
    parts = [F(piece.strip()) for piece in text.split(",") if piece.strip()]
    outer = sorted({part.denominator for part in parts if part != F(1, 2)})
    middle = sum(1 for part in parts if part == F(1, 2))
    return "loop-" + "-".join(str(value) for value in outer) + f"-mid-{middle}"


def entry_from_census(curve):
    x, y = rows_from_spots(curve["spots"])
    loop, bend = measure(x, y)
    return {"name": name_from_spots(curve["spots"]),
            "loop": loop, "bend": bend,
            "speedX": x, "speedY": y, "step": 1, "roots": curve["spots"],
            "bend": None, "grid": curve["grid"], "crossings": curve["crossings"],
            "arc": curve["arc"],
            "source": "family-census.json; see scripts/family_census.py for the box"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="source")
    parser.add_argument("--top", type=int, default=0)
    parser.add_argument("--record")
    parser.add_argument("--png", type=int, default=0, help="render at this width")
    parser.add_argument("--cheap", type=int, default=0,
                        help="also write this many curves with grid <= 100 and 5+ crossings")
    args = parser.parse_args()

    CURVES.mkdir(exist_ok=True)
    written = []
    if args.record:
        entry = json.loads(Path(args.record).read_text())
        written.append(write_curve(entry, args.png, args.png or 900))
    else:
        source = args.source or str(ROOT / "workbench" / "family-census.json")
        census = json.loads(Path(source).read_text())
        curves = sorted(census["curves"], key=lambda c: (-c["crossings"], c["grid"]))
        chosen = list(curves[:args.top or 3])
        if args.cheap:
            cheap = [c for c in curves if c["grid"] <= 100 and c["crossings"] >= 5]
            cheap.sort(key=lambda c: (-c["crossings"], c["grid"]))
            seen = {c["spots"] for c in chosen}
            chosen += [c for c in cheap if c["spots"] not in seen][:args.cheap]
        for curve in chosen:
            written.append(write_curve(entry_from_census(curve), args.png, args.png or 900))
    for slug, record in written:
        print(f"curves/{slug}/  crossings {record.get('crossings')}  grid 1/{record.get('grid')}")
    rows = rebuild_index()
    print(f"curves/index.json  {len(rows)} curves")


if __name__ == "__main__":
    main()
