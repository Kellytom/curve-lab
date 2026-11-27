#!/usr/bin/env python3
"""Check a file against the shared quintic contract, from the extension's side.

The authority is `workbench/quintic.schema.json` (`curve-lab.quintic/1`), written
and owned by the curve-lab side. This script is the extension's reader-side
check: it answers "can my side read this, and did my writer produce it?" without
needing Node.

    python scripts/quintic_contract.py workbench/quintic-guides.json
    python scripts/quintic_contract.py /tmp/export/*-quintic.json
    python scripts/quintic_contract.py --extent-must-follow <file>

Exit 0 when every file obeys the contract, 1 with the first fault otherwise.
`state/QUINTIC-CONTRACT-int.md` says what the fields mean.
"""

import argparse
import json
import math
import sys
from pathlib import Path

DEGREE = 5
SPAN_POINTS = 6
GROUPS = ("math", "ornament")
CONTINUITY = ("G1", "G2", "G3")


class Fault(Exception):
    pass


def number(value, where):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Fault("%s is %r, not a number" % (where, value))
    if not math.isfinite(value):
        raise Fault("%s is not finite" % where)


def only(record, allowed, where):
    extra = set(record) - set(allowed)
    if extra:
        raise Fault("%s has %s, which the schema does not allow"
                    % (where, ", ".join(sorted(extra))))


def point(value, where):
    if not isinstance(value, list) or len(value) != 2:
        raise Fault("%s is not [x, y]" % where)
    number(value[0], where + "[0]")
    number(value[1], where + "[1]")


def end_of_span(value, where):
    if not isinstance(value, dict):
        raise Fault("%s is not an object" % where)
    only(value, ("p", "tangent", "kappa", "rate"), where)
    for key in ("p", "tangent", "kappa", "rate"):
        if key not in value:
            raise Fault("%s.%s is missing" % (where, key))
    point(value["p"], where + ".p")
    point(value["tangent"], where + ".tangent")
    for key in ("kappa", "rate"):
        if value[key] is not None:
            number(value[key], "%s.%s" % (where, key))


def span_of_curve(value, where):
    if not isinstance(value, dict):
        raise Fault("%s is not an object" % where)
    only(value, ("uid", "kind", "points", "weights", "frame"), where)
    for key in ("uid", "kind", "points", "weights", "frame"):
        if key not in value:
            raise Fault("%s.%s is missing" % (where, key))
    if value["kind"] != "quintic":
        raise Fault("%s.kind is %r, must be \"quintic\"" % (where, value["kind"]))
    points = value["points"]
    if not isinstance(points, list) or len(points) != SPAN_POINTS:
        raise Fault("%s.points must be %d points" % (where, SPAN_POINTS))
    for i, p in enumerate(points):
        point(p, "%s.points[%d]" % (where, i))
    weights = value["weights"]
    if weights is not None:
        if not isinstance(weights, list) or len(weights) != SPAN_POINTS:
            raise Fault("%s.weights must be null or %d numbers" % (where, SPAN_POINTS))
        for i, w in enumerate(weights):
            number(w, "%s.weights[%d]" % (where, i))
    frame = value["frame"]
    if not isinstance(frame, dict) or set(frame) != {"start", "end"}:
        raise Fault("%s.frame must be {start, end}" % where)
    end_of_span(frame["start"], where + ".frame.start")
    end_of_span(frame["end"], where + ".frame.end")


def join_of_curve(value, where):
    if not isinstance(value, dict):
        raise Fault("%s is not an object" % where)
    only(value, ("uid", "a", "b", "continuity", "residual"), where)
    for key in ("uid", "a", "b", "continuity", "residual"):
        if key not in value:
            raise Fault("%s.%s is missing" % (where, key))
    if value["continuity"] not in CONTINUITY:
        raise Fault("%s.continuity is %r" % (where, value["continuity"]))
    for side in ("a", "b"):
        ref = value[side]
        if not isinstance(ref, dict) or set(ref) != {"span", "end"}:
            raise Fault("%s.%s must be {span, end}" % (where, side))
        if ref["end"] not in ("start", "end"):
            raise Fault("%s.%s.end is %r" % (where, side, ref["end"]))
    residual = value["residual"]
    if not isinstance(residual, dict):
        raise Fault("%s.residual is not an object" % where)
    only(residual, ("position", "tangentDegrees", "kappa", "rate"), where + ".residual")
    for key in ("position", "tangentDegrees", "kappa", "rate"):
        if key not in residual:
            raise Fault("%s.residual.%s is missing" % (where, key))
        number(residual[key], "%s.residual.%s" % (where, key))
        if residual[key] < 0:
            raise Fault("%s.residual.%s is negative" % (where, key))


def curve(value, where):
    if not isinstance(value, dict):
        raise Fault("%s is not an object" % where)
    only(value, ("uid", "group", "family", "name", "note", "closed", "winding",
                 "fitError", "selfCrossings", "spans", "joins"), where)
    for key in ("uid", "group", "family", "name", "closed", "spans", "joins"):
        if key not in value:
            raise Fault("%s.%s is missing" % (where, key))
    if not isinstance(value["uid"], str) or len(value["uid"]) < 3:
        raise Fault("%s.uid must be a string of 3+ characters" % where)
    if value["group"] not in GROUPS:
        raise Fault("%s.group is %r, must be one of %s"
                    % (where, value["group"], ", ".join(GROUPS)))
    if not isinstance(value["closed"], bool):
        raise Fault("%s.closed is not a boolean" % where)
    if "winding" in value and value["winding"] not in ("ccw", "cw", None):
        raise Fault("%s.winding is %r" % (where, value["winding"]))
    if "fitError" in value:
        number(value["fitError"], where + ".fitError")
        if value["fitError"] < 0:
            raise Fault("%s.fitError is negative" % where)
    if "selfCrossings" in value:
        if not isinstance(value["selfCrossings"], int) or value["selfCrossings"] < 0:
            raise Fault("%s.selfCrossings is not a non-negative integer" % where)
    spans = value["spans"]
    if not isinstance(spans, list) or not spans:
        raise Fault("%s.spans is empty" % where)
    for i, span in enumerate(spans):
        span_of_curve(span, "%s.spans[%d]" % (where, i))
    joins = value["joins"]
    if not isinstance(joins, list):
        raise Fault("%s.joins is not a list" % where)
    for i, join in enumerate(joins):
        join_of_curve(join, "%s.joins[%d]" % (where, i))


def document(record, path, extent_must_follow):
    if not isinstance(record, dict):
        raise Fault("the file is not an object")
    only(record, ("format", "degree", "createdBy", "axes", "count", "curves"), "the file")
    for key in ("format", "degree", "axes", "count", "curves"):
        if key not in record:
            raise Fault("%s is missing" % key)
    if record["format"] != "curve-lab.quintic/1":
        raise Fault("format is %r, must be curve-lab.quintic/1" % record["format"])
    if record["degree"] != DEGREE:
        raise Fault("degree is %r, must be %d" % (record["degree"], DEGREE))
    axes = record["axes"]
    if not isinstance(axes, dict) or set(axes) != {"x", "y", "units", "extent"}:
        raise Fault("axes must be {x, y, units, extent}")
    if axes["x"] != "right" or axes["y"] != "up":
        raise Fault("axes must be x right, y up; got %r, %r" % (axes["x"], axes["y"]))
    extent = axes["extent"]
    if not isinstance(extent, list) or len(extent) != 4:
        raise Fault("axes.extent must be [xMin, xMax, yMin, yMax]")
    for i, v in enumerate(extent):
        number(v, "axes.extent[%d]" % i)
    if not isinstance(record["count"], int) or record["count"] < 1:
        raise Fault("count must be a positive integer")
    curves = record["curves"]
    if not isinstance(curves, list) or len(curves) != record["count"]:
        raise Fault("count is %r but there are %d curves"
                    % (record["count"], len(curves) if isinstance(curves, list) else -1))
    for i, value in enumerate(curves):
        curve(value, "curves[%d]" % i)

    xs, ys = [], []
    for value in curves:
        for span in value["spans"]:
            for x, y in span["points"]:
                xs.append(x)
                ys.append(y)
    actual = [min(xs), max(xs), min(ys), max(ys)]
    if extent_must_follow and any(abs(a - b) > 1e-6 for a, b in zip(actual, extent)):
        raise Fault("axes.extent %r does not cover the points %r" % (extent, actual))
    return "%s, %d curve%s, %d span%s" % (
        record["format"], len(curves), "" if len(curves) == 1 else "s",
        sum(len(c["spans"]) for c in curves),
        "" if sum(len(c["spans"]) for c in curves) == 1 else "s")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="JSON files, or folders of them")
    parser.add_argument("--extent-must-follow", action="store_true",
                        help="require axes.extent to equal the points' bounding box")
    args = parser.parse_args()

    targets = []
    for given in args.paths or ["workbench/quintic-guides.json"]:
        path = Path(given)
        if path.is_dir():
            targets.extend(sorted(path.glob("*.json")))
        else:
            targets.append(path)
    targets = [p for p in targets if not p.name.endswith("-report.json")]
    if not targets:
        print("nothing to check")
        return 1

    failures = 0
    for path in targets:
        try:
            record = json.loads(Path(path).read_text())
            summary = document(record, path, args.extent_must_follow)
            print("ok  %s  %s" % (path, summary))
        except (OSError, ValueError) as exc:
            print("FAIL %s  cannot read: %s" % (path, exc))
            failures += 1
        except Fault as fault:
            print("FAIL %s  %s" % (path, fault))
            failures += 1
    print()
    print("%d file%s checked, %d fault%s"
          % (len(targets), "" if len(targets) == 1 else "s",
             failures, "" if failures == 1 else "s"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
