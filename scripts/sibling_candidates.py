#!/usr/bin/env python3
"""The sibling candidates: new curves at the ceiling from the sibling map.

    .venv/bin/python scripts/sibling_candidates.py            # the list
    .venv/bin/python scripts/sibling_candidates.py --post URL # save them

The operator's decision, 2026-11-23: keep every old curve; take the near
versions as NEW curves in their own right. So each recipe the map found —
same construction (u kept), v rebuilt from the same roots with a shorter ½
stack — in fact a new curve — becomes a sandbox candidate under its own
recipe-descriptive name, with its miss against its parent stated in curve
units.

The 18 recipes that already match a stored curve are named as existing — no
duplicate is created. The gates are verified on the stored rows (position
degree, rail degree, grid, bend), never assumed.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.measure import bend, grid, to_fraction  # noqa: E402
from inkscape.ph_actions import degree_of  # noqa: E402


def rows_for(record):
    return ([to_fraction(v) for v in record["speedX"]],
            [to_fraction(v) for v in record["speedY"]])


def build(entry, registry):
    parent = next(r for r in registry["curves"] if r["uid"] == entry["uid"])
    u, _ = rows_for(parent)
    v = [int(c) for c in entry["sibling_v"]]
    u_trim = [str(c) for c in u]
    while u_trim and u_trim[-1] == "0":
        u_trim.pop()
    degree = degree_of([to_fraction(c) for c in u_trim], [to_fraction(c) for c in v])
    rail = 2 * ((degree - 1) // 2) - 1 if degree > 1 else 0
    # the recipe-descriptive name: the family name with the sibling's roots
    stem = parent["name"].split("-")[0]
    curve_name = f"{stem}-{entry['sibling_roots']}"
    return {
        "name": f"{entry['uid']}-ceil",
        "curveName": curve_name,
        "base_uid": entry["uid"],
        "speedX": [int(c) for c in u_trim],
        "speedY": v,
        "kind": "rows",
        "variant": "sibling",
        "source": "sibling-map",
        "candidate": True,
        "origin": "sibling-map",
        "miss": entry["miss_units"],
        "note": (f"the same construction as {entry['uid']} with a shorter ½ stack · "
                 f"position degree {degree} · rails {rail} · grid {grid([to_fraction(c) for c in u_trim], [to_fraction(c) for c in v])} · "
                 f"bend {bend([to_fraction(c) for c in u_trim], [to_fraction(c) for c in v]):.3f} · "
                 f"miss {entry['miss_units']} units from its parent"),
    }


def post(payload, url):
    from urllib.request import Request, urlopen
    body = json.dumps({"curves": [payload]}).encode()
    request = Request(url, data=body, headers={"content-type": "application/json"})
    with urlopen(request, timeout=30) as response:
        return response.status, response.read().decode()


def main(argv):
    url = None
    if "--post" in argv:
        url = argv[argv.index("--post") + 1]
    registry = json.load(open(ROOT / "workbench" / "curve-registry.json"))
    data = json.load(open(ROOT / "workbench" / "sibling-map.json"))["curves"]
    found = [e for e in data if "miss_units" in e]
    existing = [e for e in found if e.get("in_catalogue")]
    # one record per DISTINCT new curve: several parents reduce to the same
    # recipe (wave-middle-6 and -7 both give wave-1of2-1of2-mid), and a new
    # curve is proposed once, with its nearest parents listed beside it
    by_rows = {}
    for entry in found:
        if entry.get("in_catalogue"):
            continue
        parent = next(r for r in registry["curves"] if r["uid"] == entry["uid"])
        u_trim = [int(c) for c in parent["speedX"]]
        while u_trim and u_trim[-1] == 0:
            u_trim.pop()
        key = (tuple(u_trim), tuple(int(c) for c in entry["sibling_v"]))
        if key not in by_rows:
            by_rows[key] = {**entry, "_near": []}
        by_rows[key]["_near"].append(entry["uid"])
        if entry["miss_units"] < by_rows[key]["miss_units"]:
            by_rows[key]["miss_units"] = entry["miss_units"]
            by_rows[key]["uid"] = entry["uid"]
            by_rows[key]["name"] = entry["name"]
    fresh = sorted(by_rows.values(), key=lambda e: e["miss_units"])
    # names must be unique in the sandbox (the endpoint refuses a clash with
    # 409): the same v-roots under a different u are different curves, so a
    # discriminator is appended — never a silent overwrite
    seen = {}
    for entry in fresh:
        stem = entry["name"].split("-")[0]
        base = f"{stem}-{entry['sibling_roots']}"
        count = seen.get(base, 0) + 1
        seen[base] = count
        entry["_curveName"] = base if count == 1 else f"{base}-{count}"
    print(f"{len(found)} recipes found · {len(existing)} already stored · "
          f"{len(fresh)} distinct new curves to propose")
    for entry in fresh:
        payload = build(entry, registry)
        payload["curveName"] = entry["_curveName"]
        line = (f"{entry['uid']} {entry['name'][:24]:24s} → {payload['curveName'][:34]:34s} "
                f"miss {entry['miss_units']:9.4f} units")
        if url:
            try:
                status, body = post(payload, url)
                line += f" · POST {status} {body}"
            except Exception as error:  # a 409 is the endpoint's uniqueness law
                line += f" · refused: {error}"
        print(line)
    if existing:
        print("\nalready in the catalogue (as themselves):")
        for entry in existing:
            print(f"  {entry['uid']} {entry['name'][:30]:30s} ↔ {entry['in_catalogue']}  (miss {entry['miss_units']:.4f} units)")


if __name__ == "__main__":
    main(sys.argv[1:])
