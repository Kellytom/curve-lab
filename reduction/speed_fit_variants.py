#!/usr/bin/env python3
"""The fit-family candidates: the re-fit's served curves as sandbox records.

    .venv/bin/python reduction/speed_fit_variants.py            # the list
    .venv/bin/python reduction/speed_fit_variants.py --post URL # save them

For each curve the census serves (miss under one per cent of size), re-fit at
speed 5 and store the rows at the registry's own precision (six decimals).
The miss printed is recomputed ON THE STORED ROWS — the record's number, not
the search's (the six-decimal re-quantization changes the curve, so it must
change the number too). The save goes through POST /api/sandbox-curves: the
sandbox table is the funnel; the registry is never written directly.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.measure import curve_polynomials, to_fraction
from reduction import speed_fit


def served_curves():
    census = json.load(open(ROOT / "workbench" / "speed-fit-census.json"))
    return [r for r in census["curves"]
            if r["size"] and r["miss_share"] is not None and r["miss_share"] < 0.01]


def cell(value):
    """A row coefficient as the registry stores it: a plain decimal with the
    shortest exact text at six places or fewer."""
    short = f"{float(value):.10f}".rstrip("0").rstrip(".")
    if "." in short:
        decimals = len(short.split(".")[1])
        if decimals > 6:
            short = f"{float(value):.6f}"
    return float(short)


def build(record):
    uid, name = record["uid"], record["name"]
    parent = next(r for r in json.load(open(ROOT / "workbench" / "curve-registry.json"))["curves"]
                  if r["uid"] == uid)
    u = [to_fraction(v) for v in parent["speedX"]]
    v = [to_fraction(v) for v in parent["speedY"]]
    x, y = curve_polynomials(u, v)
    fu, fv, _ = speed_fit.reffit(x, y, 5, start=(u, v))
    # the stored rows: six decimals, the registry's precision
    su = [cell(c) for c in fu]
    sv = [cell(c) for c in fv]
    # the record's own verdict, recomputed on the stored rows
    from fractions import Fraction
    exact_u = [Fraction(f"{c:.6f}") for c in su]
    exact_v = [Fraction(f"{c:.6f}") for c in sv]
    px, py = speed_fit.position_of_rows(exact_u, exact_v)
    miss = speed_fit.station_miss(x, y, px, py)
    return {
        "name": f"{uid}-s5",
        "curveName": f"{name}-speed5",
        "base_uid": uid,
        "speedX": su,
        "speedY": sv,
        "kind": "rows",
        "variant": "speed-fit",
        "source": "reduction-speed-fit",
        "candidate": True,
        "origin": "speed-fit",
        "miss": round(miss, 6),
        "note": f"speed-space re-fit at degree 5 · miss {miss:.6f} curve units "
                f"on size {record['size']} · position degree 11, rails 9",
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
    for record in served_curves():
        payload = build(record)
        line = (f"{record['uid']} {record['name'][:24]:24s} → {payload['curveName'][:28]:28s} "
                f"miss {payload['miss']:.6f} units of {record['size']}")
        if url:
            status, body = post(payload, url)
            line += f" · POST {status} {body}"
        print(line)


if __name__ == "__main__":
    main(sys.argv[1:])
