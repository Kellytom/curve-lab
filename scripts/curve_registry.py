"""One registry for every curve: a uid, one name, and its lists.

    .venv/bin/python scripts/curve_registry.py           # report only
    .venv/bin/python scripts/curve_registry.py --write   # write the registry

The sources (workbench/real-curves.json, finder.json, operator-list.json) are
read, not changed. Curves are grouped by shape: the rows normalised by their
common factor, plus the power step. One shape is one record.

A record keeps:

    uid         c-0001, assigned once in registry order, never reused
    name        the display name, unique, lower-case, hyphenated
    aliases     the other names the same curve travelled under
    speedX/Y    the rows
    step        the power step
    lists       found, finder, B (membership, not copies)
    family      the first token of the name, or the source's family
    source      where the rows came from

Names are chosen from the existing ones, preferring a structured name
(lace-1of8-3) over a sentence (45deg at t=1/2). The rest are slugged: spaces
and commas become hyphens, a fraction becomes "a of b", a plus becomes "plus".
A name still ugly after that goes to workbench/naming-todo.json for a human.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import sys
from datetime import datetime
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "curve-registry.json"
TODO = ROOT / "workbench" / "naming-todo.json"
SOURCES = (
    ("found", "workbench/real-curves.json", "curves"),
    ("finder", "workbench/finder.json", "curves"),
    ("B", "workbench/operator-list.json", "saved"),
)
FORMAT = "curve-lab.curve-registry/1"


def rows_of(item):
    x = [Fraction(str(v)).limit_denominator(1000) for v in item.get("speedX", []) or []]
    y = [Fraction(str(v)).limit_denominator(1000) for v in item.get("speedY", []) or []]
    return x, y


def shape_of(item):
    x, y = rows_of(item)
    if not x and not y:
        return None
    whole = x + y
    factor = 0
    for value in whole:
        factor = math.gcd(factor, abs(value.numerator))
    factor = factor or 1
    return (tuple(str(v / factor) for v in x), tuple(str(v / factor) for v in y),
            item.get("step", 1))


def slug(text: str) -> str:
    s = str(text or "").strip().lower()
    s = re.sub(r"(\d+)\s*/\s*(\d+)", r"\1of\2", s)     # 1/8 -> 1of8
    s = s.replace("+", " plus ").replace("−", " minus ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def name_score(name: str) -> tuple:
    """Lower is better: structured and short beats a sentence."""
    s = slug(name)
    return (s.count(" ") > 0, len(s), s)


def family_of(name: str, item: dict) -> str:
    if item.get("family"):
        return slug(item["family"])
    token = slug(name).split("-")[0]
    return token or "curve"


def main(argv: list[str]) -> int:
    write = "--write" in argv
    groups: dict[tuple, list[dict]] = {}
    order: list[tuple] = []
    for list_name, path, key in SOURCES:
        data = json.loads((ROOT / path).read_text(encoding="utf-8"))
        for item in data.get(key, []):
            shape = shape_of(item)
            if not shape:
                continue
            if shape not in groups:
                groups[shape] = []
                order.append(shape)
            groups[shape].append({"list": list_name, "item": item})

    records = []
    todo = []
    merged = 0
    for index, shape in enumerate(order, start=1):
        members = groups[shape]
        merged += len(members) - 1
        names = [member["item"].get("name") or "curve" for member in members]
        chosen = sorted(names, key=name_score)[0]
        # Naming is a later pass: the registry keeps the chosen name as it is.
        name = chosen
        aliases = sorted({n for n in names if n != name})
        item = members[0]["item"]
        x, y = rows_of(item)
        record = {
            "uid": f"c-{index:04d}",
            "name": name,
            "aliases": aliases,
            "speedX": [float(v) if v.denominator != 1 else int(v) for v in x],
            "speedY": [float(v) if v.denominator != 1 else int(v) for v in y],
            "step": item.get("step", 1),
            "lists": sorted({member["list"] for member in members}),
            "family": family_of(name, item),
            "source": members[0]["list"],
        }
        for extra in ("definition", "grid", "note"):
            if item.get(extra) is not None:
                record[extra] = item[extra]
        records.append(record)
        if len(name) > 40 or not re.search(r"[a-z]{3}", name):
            todo.append({"uid": record["uid"], "name": name, "current": chosen,
                         "why": "long" if len(name) > 40 else "not descriptive"})

    # names must be unique; a collision takes a numeric postfix, never a silent drop
    seen: dict[str, int] = {}
    for record in records:
        base = record["name"]
        if base in seen:
            seen[base] += 1
            record["name"] = f"{base}-{seen[base]}"
            if base not in record["aliases"]:
                record["aliases"].append(base)
        else:
            seen[base] = 1

    print(f"{len(records)} curves from {sum(len(v) for v in groups.values())} rows; "
          f"{merged} duplicate rows merged")
    print(f"{sum(1 for r in records if len(r['lists']) > 1)} curves in more than one list")
    print(f"{len(todo)} names want a human")
    for row in todo[:10]:
        print(f"  {row['uid']}  {row['name']}  ({row['why']})")

    if not write:
        print("report only: add --write to keep the registry")
        return 0

    backup = ROOT / "workbench" / "backups"
    backup.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        stamp = datetime.now().isoformat().replace(":", "-").replace(".", "-")
        shutil.copy2(OUT, backup / f"curve-registry-{stamp}.json")
    OUT.write_text(json.dumps({"format": FORMAT, "curves": records}, indent=1) + "\n",
                   encoding="utf-8")
    TODO.write_text(json.dumps({"format": "curve-lab.naming-todo/1", "curves": todo},
                               indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} and {TODO.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
