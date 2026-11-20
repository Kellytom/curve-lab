#!/usr/bin/env python3
"""Score the hybrid candidates with the collection's own measures.

    .venv/bin/python scripts/hybrid_rank.py [top]

Reads workbench/hybrid-candidates.json (written by scripts/hybrid_candidates.mjs) and
prints the ranked list: crossing pairs, reversals, mirror gap, aspect. No drawing here;
the numbers decide, the figure justifies them.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import character_search as cs  # noqa: E402

CANDIDATES = ROOT / "workbench" / "hybrid-candidates.json"


def score(row):
    crossings = row["crossings"]
    s = 0.0
    if 2 <= crossings <= 16:
        s += min(crossings, 12) * 1.0
    elif crossings > 16:
        s += 12 - (crossings - 16) * 0.4
    s += 3.0 * max(0.0, 1 - row["mirror"] / 0.10)
    s += 2.0 * max(0.0, 1 - abs(row["aspect"] - 1.1) / 0.6)
    s += 1.0 * min(row["loops"], 8)
    if row["extent"] < 0.2:
        s -= 6
    return round(s, 2)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("top", nargs="?", type=int, default=12)
    args = parser.parse_args(argv)

    document = json.loads(CANDIDATES.read_text())
    rows = []
    for candidate in document["candidates"]:
        points = [(float(x), float(y)) for x, y in candidate["points"]]
        if len(points) < 3:
            continue
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        row = {
            "id": candidate["id"],
            "p": candidate["p"], "q": candidate["q"],
            "block": candidate["block"], "use": candidate["use"],
            "crossings": cs.crossings(points),
            "loops": min(cs.reversals(points), 24),
            "mirror": round(cs.mirror_gap(points), 4),
            "aspect": round(max(width, height) / (min(width, height) or 1), 3),
            "extent": round(max(width, height), 3),
        }
        row["score"] = score(row)
        rows.append(row)

    rows.sort(key=lambda row: -row["score"])
    print(f'{len(rows)} candidates, triple {document["triple"]}, {document["count"]} stations')
    print(f'{"score":>6} {"cross":>5} {"loops":>5} {"mirror":>7} {"aspect":>6}  id')
    for row in rows[: args.top]:
        print(f'{row["score"]:>6} {row["crossings"]:>5} {row["loops"]:>5} '
              f'{row["mirror"]:>7} {row["aspect"]:>6}  {row["id"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
