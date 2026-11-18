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

import hashlib
import hmac
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
NOTES = ROOT / "workbench" / "curve-notes.json"
STARS = ROOT / "workbench" / "finder-stars.json"
TODO = ROOT / "workbench" / "naming-todo.json"
SOURCES = (
    ("found", "workbench/real-curves.json", "curves"),
    ("finder", "workbench/finder.json", "curves"),
    ("B", "workbench/operator-list.json", "saved"),
)
FORMAT = "curve-lab.curve-registry/1"
PPOI = ROOT / "ppoi.json"


def owner_secret():
    """The ownership key lives outside the repository (ppoi.json, gitignored).

    A record carries only an HMAC of its uid, so a pull request cannot forge the
    mark without the key, and the key never appears in the public tree.
    """
    if not PPOI.exists():
        return None
    data = json.loads(PPOI.read_text(encoding="utf-8"))
    secret = data.get("ownership", {}).get("secret")
    if secret:
        return secret
    import secrets as _secrets
    secret = _secrets.token_hex(32)
    data.setdefault("ownership", {})["secret"] = secret
    PPOI.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return secret


def owner_mark(secret, uid):
    if not secret:
        return None
    return hmac.new(secret.encode(), uid.encode(), hashlib.sha256).hexdigest()[:16]


FILLER = {"loadable", "the", "at", "of", "septic", "septic-curves"}
FAMILY_WORDS = (
    ("rose", "rose"), ("loop", "loop"), ("cross", "cross"),
    ("45deg", "bend45"), ("line", "line"), ("ph", "ph"),
    ("lace", "lace"), ("wave", "wave"),
)
PREFIX = {"45deg": "bend45", "a": "term", "c": "term", "e": "term"}


def tidy(text: str) -> str:
    parts = [part for part in text.split("-") if part and part not in FILLER]
    out = "-".join(parts)
    out = re.sub(r"^45deg-", "", out)
    out = re.sub(r"^plus-", "", out)
    out = out.replace("-t-", "-t")
    out = re.sub(r"-q-(\d)", r"-q\1", out)
    out = re.sub(r"^t-(\d)", r"t\1", out)
    out = re.sub(r"^(plus|minus)-(\d)", r"\1\2", out)
    return out


def variant_of(name, family):
    s = slug(name)
    if s == family:
        return "plain"
    if s.startswith(f"{family}-"):
        return tidy(s[len(family) + 1:]) or "plain"
    return tidy(s)


def rows_of(item):
    x = [Fraction(str(v)).limit_denominator(1000) for v in item.get("speedX", []) or []]
    y = [Fraction(str(v)).limit_denominator(1000) for v in item.get("speedY", []) or []]
    return x, y


def shape_of(item):
    x, y = rows_of(item)
    if not x and not y:
        path = item.get("path")
        if path:
            # A drawing without rows: identity is its outline, rounded. Two
            # paths merge only when every sampled point agrees.
            return ("path", tuple((round(px, 2), round(py, 2)) for px, py in path))
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
    s = re.sub(r"=\s*-(\d+)", r"=minus\1", s)            # b=-1 -> b=minus1
    s = re.sub(r"(?<=\s)-(\d)", r" minus\1", s)          # slope -3 -> slope minus3
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

    stars = set()
    if STARS.exists():
        for star in json.loads(STARS.read_text(encoding="utf-8")).get("curves", []):
            if star.get("name"):
                stars.add(star["name"])
    notes = {}
    if NOTES.exists():
        for note in json.loads(NOTES.read_text(encoding="utf-8")).get("curves", []):
            if note.get("uid"):
                notes[note["uid"]] = note

    secret = owner_secret()
    records = []
    todo = []
    merged = 0
    for index, shape in enumerate(order, start=1):
        members = groups[shape]
        merged += len(members) - 1
        names = [member["item"].get("name") or "curve" for member in members]
        chosen = sorted(names, key=name_score)[0]
        # A sentence becomes a name; the sentence is kept as an alias. A name
        # that was already structured is left exactly as it is.
        name = slug(chosen) or chosen
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
        note = notes.get(record["uid"], {})
        if note.get("name"):
            if note["name"] != record["name"] and record["name"] not in record["aliases"]:
                record["aliases"].append(record["name"])
            record["name"] = note["name"]
        record["auto_named"] = slug(chosen) != chosen
        record["family_id"] = PREFIX.get(slug(record["family"]), slug(record["family"]))
        record["variant"] = variant_of(record["name"], slug(record["family"]))
        if record["auto_named"]:
            raw = slug(chosen)
            prefix = next((pref for word, pref in FAMILY_WORDS if raw.startswith(word)),
                          record["family_id"])
            if re.match(r"^[a-e](-|$)", raw) or "mixed" in raw:
                prefix = "term"
            core = tidy(raw[len(prefix):] if raw.startswith(prefix) else raw)
            record["family_id"] = prefix
            record["variant"] = core or "plain"
            record["name"] = prefix if not core else f"{prefix}-{core}"
        record["owner"] = owner_mark(secret, record["uid"])
        record["kind"] = record.get("kind", "rows")
        record["starred"] = any(n in stars for n in [record["name"], *record["aliases"]])
        # A curve that exists only in the finder, was never starred and was never
        # rated is a candidate, not a pick. It stays in the registry, out of the
        # naming desk and out of the chosen sets.
        record["candidate"] = (record["lists"] == ["finder"]
                               and not record["starred"]
                               and int(record.get("importance") or 0) == 0)
        record["importance"] = int(note.get("importance",
                                          10 if record["starred"] else 0))
        for key in ("rotation", "pieces", "border_uid"):
            if note.get(key) is not None:
                record[key] = note[key]
        if not x and not y and item.get("path"):
            record["path"] = [[round(px, 2), round(py, 2)] for px, py in item["path"]]
            record.pop("speedX", None)
            record.pop("speedY", None)
            record["kind"] = "polyline"
        for extra in ("definition", "grid", "note"):
            if item.get(extra) is not None:
                record[extra] = item[extra]
        records.append(record)
        if len(name) > 40 or not re.search(r"[a-z]{3}", name):
            todo.append({"uid": record["uid"], "name": name, "current": chosen,
                         "why": "long" if len(name) > 40 else "not descriptive"})

    # a family's base is the plain member, else its shortest variant
    families: dict[str, list[dict]] = {}
    for record in records:
        families.setdefault(record["family_id"], []).append(record)
    for members in families.values():
        base = min(members, key=lambda r: (r["variant"] != "plain", len(r["variant"])))
        for record in members:
            record["base_uid"] = None if record is base else base["uid"]

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
    # A set is the composite: the inner curve, the border curve, the turn, the
    # number of pieces and the border's copies per side. One default set per
    # curve; more can sit beside it later.
    sets = []
    for index, record in enumerate(records, start=1):
        sets.append({
            "uid": f"s-{index:04d}",
            "name": f"{record['name']}-set",
            "inner_uid": record["uid"],
            "border_uid": record.get("border_uid") or record["uid"],
            "rotation": int(record.get("rotation", 0) or 0),
            "pieces": int(record.get("pieces", 1) or 1),
            "per_side": 5 if record["uid"] in {"c-0007", "c-0002"} else 9,
            "importance": int(record.get("importance", 0) or 0),
        })

    OUT.write_text(json.dumps({"format": FORMAT, "curves": records, "sets": sets}, indent=1) + "\n",
                   encoding="utf-8")
    TODO.write_text(json.dumps({"format": "curve-lab.naming-todo/1", "curves": todo},
                               indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} and {TODO.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
