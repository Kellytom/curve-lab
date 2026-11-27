"""Check the shared quintic contract from Python — the side the extension lives on.

    .venv/bin/python scripts/check_quintic_contract.py
    .venv/bin/python scripts/check_quintic_contract.py workbench/quintic-closed.json

The Inkscape extension is Python, so the contract has to be checkable from Python
and not only from the TypeScript test that the generator's author runs. This reads
the same files and asserts the same four facts:

  1. `points` are six numbers per span; on this data they are integers.
  2. `frame.start.tangent` is P1 - P0 and `frame.end.tangent` is P5 - P4, both
     pointing forward;
  3. `closed: true` means the last span ends where the first starts, with a winding;
  4. every join carries a measured residual.

Exit 1 on the first violation, with the path and the reason. Nothing is written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = [
    ROOT / "workbench" / "quintic-guides.json",
    ROOT / "workbench" / "quintic-closed.json",
    ROOT / "workbench" / "quintic-chain.json",
]


def fail(where: str, why: str) -> None:
    raise SystemExit(f"FAIL {where}: {why}")


def check_shape(where: str, curve: dict) -> None:
    if not curve.get("uid"):
        fail(where, "curve has no uid")
    if curve.get("closed") not in (True, False):
        fail(where, "closed is not a boolean")
    spans = curve.get("spans")
    if not isinstance(spans, list) or not spans:
        fail(where, "curve has no spans")
    joins = curve.get("joins")
    if not isinstance(joins, list):
        fail(where, "curve has no joins list")

    for span in spans:
        if span.get("kind") != "quintic":
            fail(where, f"span {span.get('uid')} is not a quintic")
        points = span.get("points")
        if not isinstance(points, list) or len(points) != 6:
            fail(where, f"span {span.get('uid')} does not have six points")
        for p in points:
            if not (isinstance(p, list) and len(p) == 2):
                fail(where, f"span {span.get('uid')} has a malformed point {p!r}")
        if span.get("weights") is not None:
            fail(where, f"span {span.get('uid')} carries weights the contract has not opened")

        frame = span.get("frame") or {}
        start, end = frame.get("start"), frame.get("end")
        if not isinstance(start, dict) or not isinstance(end, dict):
            fail(where, f"span {span.get('uid')} has no frame")
        if [start["p"][0], start["p"][1]] != list(points[0]):
            fail(where, f"span {span.get('uid')} frame.start.p is not P0")
        if [end["p"][0], end["p"][1]] != list(points[5]):
            fail(where, f"span {span.get('uid')} frame.end.p is not P5")
        want_start = [points[1][0] - points[0][0], points[1][1] - points[0][1]]
        want_end = [points[5][0] - points[4][0], points[5][1] - points[4][1]]
        if list(start["tangent"]) != want_start:
            fail(where, f"span {span.get('uid')} start tangent is not P1 - P0 (forward)")
        if list(end["tangent"]) != want_end:
            fail(where, f"span {span.get('uid')} end tangent is not P5 - P4 (forward)")

    if curve["closed"]:
        first = spans[0]["points"][0]
        last = spans[-1]["points"][5]
        if list(first) != list(last):
            fail(where, f"closed curve {curve['uid']} does not meet itself")
        if curve.get("winding") not in ("ccw", "cw"):
            fail(where, f"closed curve {curve['uid']} has no winding")

    for join in joins:
        residual = join.get("residual") or {}
        for key in ("position", "tangentDegrees", "kappa", "rate"):
            if key not in residual:
                fail(where, f"join {join.get('uid')} has no {key} residual")
        if join.get("continuity") not in ("G1", "G2", "G3"):
            fail(where, f"join {join.get('uid')} has an unknown continuity")


def check_chain(path: Path, data: dict) -> tuple[int, int]:
    """`curve-lab.chain/1` is a report, not a curve collection: spans and joins only."""
    chain = data.get("chain")
    joins = data.get("joins")
    if not isinstance(chain, list) or not chain:
        fail(str(path), "chain has no spans")
    if not isinstance(joins, list) or len(joins) != len(chain) - 1:
        fail(str(path), "a chain of n spans needs n-1 joins")
    for span in chain:
        if not span.get("uid") or len(span.get("points") or []) != 6:
            fail(str(path), f"span {span.get('uid')} does not have six points")
    for join in joins:
        residual = join.get("residual") or {}
        if "position" not in residual or "tangentDegrees" not in residual:
            fail(str(path), f"join {join.get('uid')} has no measured residual")
        if join.get("continuity") not in ("G1", "G2", "G3"):
            fail(str(path), f"join {join.get('uid')} has an unknown continuity")
    return len(chain), len(joins)


def check_file(path: Path) -> tuple[int, int]:
    if not path.exists():
        fail(str(path), "missing")
    data = json.loads(path.read_text())
    if data.get("format") == "curve-lab.chain/1":
        return check_chain(path, data)
    if data.get("format") != "curve-lab.quintic/1":
        fail(str(path), f"format is {data.get('format')!r}, not curve-lab.quintic/1")
    if data.get("degree") != 5:
        fail(str(path), "degree is not 5")
    axes = data.get("axes") or {}
    if axes.get("x") != "right" or axes.get("y") != "up":
        fail(str(path), "axes are not x-right, y-up (the house rule)")

    curves = data.get("curves")
    if not isinstance(curves, list) or not curves:
        fail(str(path), "no curves")
    if data.get("count") != len(curves):
        fail(str(path), f"count {data.get('count')} does not match {len(curves)} curves")

    seen: set[str] = set()
    spans = 0
    for curve in curves:
        where = f"{path.name}:{curve.get('uid')}"
        check_shape(where, curve)
        if curve["uid"] in seen:
            fail(where, "duplicate uid")
        seen.add(curve["uid"])
        spans += len(curve["spans"])
    return len(curves), spans


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv[1:]] or DEFAULT
    for path in paths:
        data = json.loads(path.read_text())
        count, spans = check_file(path)
        if data.get("format") == "curve-lab.chain/1":
            print(f"ok {path.name}: {count} spans, {spans} joins")
        else:
            closed = sum(1 for c in data["curves"] if c["closed"])
            print(f"ok {path.name}: {count} curves, {spans} spans, {closed} closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
