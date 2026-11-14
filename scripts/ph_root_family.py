"""Find letter strokes by their roots, and check the gallery for waste.

    .venv/bin/python scripts/ph_root_family.py --family
    .venv/bin/python scripts/ph_root_family.py --clean

Why roots and not random numbers: the shape of one of these curves is set by the
ratio of the two rows, so the turning points are the roots of the y row. A random
search over coefficients spends almost all its time on curves nobody would draw.
Enumerating root positions and multiplicities visits only shapes that have a
name: one turn is a bowl or a v, two turns an m or a w, three a wave.

`--clean` reads the gallery seeds and reports their grid cost and any duplicate
rows, which is the other half of the question: which of the curves we already
have are worth keeping as they stand.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_metrics as metrics  # noqa: E402
from ph_crossings import pair_crossings, spine  # noqa: E402

POSITIONS = (Fraction(1, 5), Fraction(1, 4), Fraction(1, 3), Fraction(2, 5), Fraction(1, 2),
             Fraction(3, 5), Fraction(2, 3), Fraction(3, 4), Fraction(4, 5))


def row_from_roots(roots):
    """The coefficients of the product of (t - r), lowest power first."""
    coefficients = [Fraction(1)]
    for root in roots:
        wider = [Fraction(0)] * (len(coefficients) + 1)
        for power, value in enumerate(coefficients):
            wider[power] += -root * value
            wider[power + 1] += value
        coefficients = wider
    scale = 1
    for value in coefficients:
        scale = scale * value.denominator // math.gcd(scale, value.denominator)
    return [int(value * scale) for value in coefficients]


def turns_of(points):
    return sum(1 for i in range(1, len(points) - 1)
               if (points[i][1] - points[i - 1][1]) * (points[i + 1][1] - points[i][1]) < 0)


def measure(speed_x, speed_y):
    _, x, y = spine(speed_x, speed_y, 600)
    points = list(zip(x, y))
    width = max(x) - min(x)
    height = max(y) - min(y)
    flipped = [(-px, py) for px, py in points]
    measured = metrics.metrics(speed_x, speed_y)
    return {
        "turns": turns_of(points),
        "aspect": width / max(height, 1e-9),
        "bend": measured["bend"],
        "pitch": measured["pitch"],
        "inflections": measured["inflection_count"],
        "crossings": len(pair_crossings(points, flipped)),
    }


def family():
    """Every root pattern of one to three turns, with a plain or sloped x row."""
    found = {}
    x_rows = {"plain": [1], "sloped": [1, 1], "half": [1, Fraction(1, 2)]}
    for name, x_row in x_rows.items():
        for count in (1, 2, 3):
            for positions in _choose(POSITIONS, count):
                for multiplicity in _multiplicities(count):
                    roots = []
                    for position, times in zip(positions, multiplicity):
                        roots.extend([position] * times)
                    speed_y = row_from_roots(roots)
                    if len(speed_y) > 10:
                        continue
                    speed_x = _pad(x_row, len(speed_y))
                    try:
                        measured = measure(speed_x, speed_y)
                    except (ZeroDivisionError, ValueError):
                        continue
                    if measured["pitch"] > 5000 or measured["bend"] > 40:
                        continue
                    if not (0.4 < measured["aspect"] < 2.6):
                        continue
                    key = (measured["turns"], measured["pitch"])
                    entry = (name, speed_x, speed_y, measured)
                    if key not in found or found[key][3]["bend"] < measured["bend"]:
                        found[key] = entry
    return found


def _choose(items, count):
    if count == 1:
        return [(item,) for item in items]
    out = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if count == 2:
                out.append((items[i], items[j]))
            else:
                for k in range(j + 1, len(items)):
                    out.append((items[i], items[j], items[k]))
    return out


def _multiplicities(count):
    if count == 1:
        return [(1,), (2,), (3,)]
    if count == 2:
        return [(1, 1), (2, 2), (1, 2), (2, 1)]
    return [(1, 1, 1), (2, 2, 2)]


def _pad(row, length):
    out = [float(v) for v in row]
    return out + [0.0] * (length - len(out))


def seeds():
    """The gallery's own rows, read out of the panel script."""
    text = (ROOT / "scripts" / "ph_nth_panels.js").read_text()
    block = text[text.index("const SEED = ["):]
    block = block[:block.index("\n  ];")]
    out = []
    for match in re.finditer(r'\{ name: "([^"]+)",(.*?)\}', block, re.S):
        name, body = match.group(1), match.group(2)
        def row(key):
            found = re.search(key + r':\s*\[([^\]]*)\]', body)
            return [float(v) for v in found.group(1).split(",") if v.strip()] if found else []
        speed_x, speed_y = row("speedX"), row("speedY")
        if speed_x and speed_y:
            out.append((name, speed_x, speed_y))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", action="store_true")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    if not (args.family or args.clean):
        parser.print_help()
        return

    if args.family:
        found = family()
        for turns in sorted({key[0] for key in found}):
            label = {1: "one turn: a bowl or a v", 2: "two turns: an m or a w",
                     3: "three turns: a wave"}.get(turns, f"{turns} turns")
            print(f"\n{label}")
            rows = sorted((entry for key, entry in found.items() if key[0] == turns),
                          key=lambda entry: entry[3]["pitch"])[:6]
            for name, speed_x, speed_y, measured in rows:
                print(f"  {name:7s} x {_short(speed_x)}  y {_short(speed_y)}"
                      f"  pitch {measured['pitch']:>5}  bend {measured['bend']:6.2f}"
                      f"  aspect {measured['aspect']:4.2f}  inflections {measured['inflections']}")

    if args.clean:
        print("\nthe gallery, by grid cost")
        rows = []
        for name, speed_x, speed_y in seeds():
            measured = metrics.metrics(speed_x, speed_y)
            rows.append((measured["pitch"], name, speed_x, speed_y, measured))
        rows.sort()
        for pitch, name, speed_x, speed_y, measured in rows:
            print(f"  {pitch:>9,}  {name:12s} bend {measured['bend']:7.2f}"
                  f"  inflections {measured['inflection_count']}")
        seen = {}
        for pitch, name, speed_x, speed_y, measured in rows:
            key = (tuple(speed_x), tuple(speed_y))
            if key in seen:
                print(f"  duplicate rows: {seen[key]} and {name}")
            seen[key] = name


def _short(row):
    trimmed = list(row)
    while len(trimmed) > 2 and trimmed[-1] == 0:
        trimmed.pop()
    return "[" + ",".join(f"{v:g}" for v in trimmed) + "]"


if __name__ == "__main__":
    main()
