"""One shape for a stored curve, and the only code that reads or writes it.

The old files stored a curve as two flat rows, `speedX` and `speedY`, in which
the position of a number meant its power. That is where the confusion came from:
a row written at step 1 and read at step 1/2 put the numbers in the wrong boxes,
and nothing in the file said which power a number belonged to.

This module owns one format, `curve-lab.curves/2`:

    {
      "format": "curve-lab.curves/2",
      "note": "...",
      "curves": [
        {
          "name": "lace-1of9-3",
          "terms": [{"power": 0, "x": 1, "y": -8}, {"power": 1, "x": 0, "y": 129}, ...],
          "measured": {"bend": 1.772, "grid": 22, "meetings": 16, "self": 8},
          "provenance": {"roots": "1/9, ...", "walk": "degree 5", "batch": "first"}
        }
      ]
    }

Rules, and why:

* **The power is on the term.** A number cannot land in the wrong box, because
  it carries the box it belongs to.
* **Only non-zero terms are stored.** A zero is the absence of a term, not data,
  so a curve cannot disagree with itself about how many powers it has.
* **The flat rows are not stored.** They are derived on demand from the terms,
  so there is one source of truth rather than two that can drift apart.
* **Measured numbers are labelled measured.** Bend and grid are re-derived in
  `validate()`; meetings and self-crossings come from the search and are facts
  about that run, not something a reader can recompute cheaply.
* **Provenance travels with the curve.** Which walk, which batch and which flat
  spots it came from, so a name can be checked against its construction.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

FORMAT = "curve-lab.curves/2"


# ---------------------------------------------------------------- constructors

def term(power, x, y):
    """One power with its two speeds."""
    return {"power": power, "x": float(x), "y": float(y)}


def record(name, terms, *, bend=None, grid=None, meetings=None, self_crossings=None,
           roots=None, walk=None, batch=None, truncation=None):
    """A record in the canonical shape, with only the facts that were measured."""
    cleaned = [term(t["power"], t["x"], t["y"]) for t in terms
               if float(t.get("x", 0)) or float(t.get("y", 0))]
    measured = {}
    if bend is not None:
        measured["bend"] = round(float(bend), 3)
    if grid is not None:
        measured["grid"] = int(grid)
    if meetings is not None:
        measured["meetings"] = int(meetings)
    if self_crossings is not None:
        measured["self"] = int(self_crossings)
    provenance = {key: value for key, value in
                  (("roots", roots), ("walk", walk), ("batch", batch)) if value}
    out = {key: value for key, value in
           (("name", name), ("terms", cleaned), ("measured", measured),
            ("provenance", provenance)) if value not in ({}, None, "")}
    if truncation:
        out["truncation"] = {
            end: {"t": float(truncation[end]["t"]),
                  "x": float(truncation[end]["x"]),
                  "y": float(truncation[end]["y"])}
            for end in ("from", "to") if end in truncation
        }
    return out


def rows_from_terms(terms):
    """The flat rows, for a reader that wants one number per power from 0 up."""
    if not terms:
        return [], []
    top = max(int(term["power"]) for term in terms)
    x = [0.0] * (top + 1)
    y = [0.0] * (top + 1)
    for item in terms:
        index = int(item["power"])
        x[index] = float(item["x"])
        y[index] = float(item["y"])
    return x, y


def rows_for_step(terms, step):
    """The rows a page needs at a given exponent step, or (rows, refusals).

    A power that does not land on a box is refused rather than rounded, because a
    rounded power is a different curve.
    """
    if step <= 0:
        raise ValueError("the exponent step must be positive")
    placed, refused = {}, []
    for item in terms:
        power = float(item["power"])
        index = power / step
        if abs(index - round(index)) > 1e-9:
            refused.append(f"power {power} is off the step {step}")
            continue
        placed[int(round(index))] = item
    if not placed:
        return ([], []), refused
    top = max(placed)
    x = [0.0] * (top + 1)
    y = [0.0] * (top + 1)
    for index, item in placed.items():
        x[index] = float(item["x"])
        y[index] = float(item["y"])
    return (x, y), refused


# ---------------------------------------------------------------------- reading

def read(path):
    """Read a document and upgrade it in memory. Raises ValueError if unusable."""
    document = json.loads(Path(path).read_text())
    return normalise(document)


def normalise(document):
    """Accept the current format or the old flat rows, and return the current one."""
    if not isinstance(document, dict):
        raise ValueError("a curve document must be an object")
    curves = document.get("curves")
    if not isinstance(curves, list):
        raise ValueError("a curve document needs a `curves` list")
    out = []
    for entry in curves:
        out.append(upgrade(entry))
    return {"format": FORMAT, "note": document.get("note", ""), "curves": out}


def upgrade(entry):
    """Turn one old or new entry into a canonical record, keeping what it measured."""
    if not isinstance(entry, dict):
        raise ValueError(f"a curve must be an object, not {type(entry).__name__}")
    name = entry.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("every curve needs a name")

    if isinstance(entry.get("terms"), list) and entry["terms"]:
        terms = entry["terms"]
    else:
        xs = entry.get("speedX") or []
        ys = entry.get("speedY") or []
        if not isinstance(xs, list) or not isinstance(ys, list):
            raise ValueError(f"{name}: speedX and speedY must be lists")
        length = max(len(xs), len(ys))
        terms = [{"power": k,
                  "x": xs[k] if k < len(xs) else 0,
                  "y": ys[k] if k < len(ys) else 0}
                 for k in range(length) if (k < len(xs) and xs[k]) or (k < len(ys) and ys[k])]

    measured = entry.get("measured") or {}
    provenance = entry.get("provenance") or {}
    # the old files spread these over the top level
    bend = measured.get("bend", entry.get("bend"))
    grid = measured.get("grid", entry.get("pitch"))
    meetings = measured.get("meetings", entry.get("meetings180"))
    self_crossings = measured.get("self", entry.get("self"))
    roots = provenance.get("roots", entry.get("roots"))
    return record(name, terms, bend=bend, grid=grid, meetings=meetings,
                  self_crossings=self_crossings, roots=roots,
                  walk=provenance.get("walk", entry.get("walk")),
                  batch=provenance.get("batch", entry.get("batch", "first")),
                  truncation=entry.get("truncation"))


# ---------------------------------------------------------------------- writing

def write(path, document):
    """Validate, then write the canonical shape. A bad document never reaches disk."""
    normalised = normalise(document)
    problems = validate(normalised)
    if problems:
        raise ValueError("refusing to write: " + "; ".join(problems[:5]))
    normalised["note"] = document.get("note", "")
    Path(path).write_text(json.dumps(normalised, indent=1) + "\n")
    return normalised


# ------------------------------------------------------------------- validation

def validate(document):
    """Every problem a reader could trip over, as plain sentences."""
    problems = []
    if document.get("format") != FORMAT:
        problems.append(f"format is {document.get('format')!r}, expected {FORMAT!r}")
    curves = document.get("curves")
    if not isinstance(curves, list):
        return problems + ["`curves` is not a list"]

    names = {}
    for index, curve in enumerate(curves):
        where = f"curve {index} ({curve.get('name', 'no name')})"
        name = curve.get("name")
        if not isinstance(name, str) or not name.strip():
            problems.append(f"{where}: no name")
        elif name in names:
            problems.append(f"{where}: the name is used twice")
        else:
            names[name] = index
        terms = curve.get("terms")
        if not isinstance(terms, list) or not terms:
            problems.append(f"{where}: no terms")
            continue
        powers = []
        for item in terms:
            if not isinstance(item, dict) or "power" not in item:
                problems.append(f"{where}: a term has no power")
                continue
            power = item["power"]
            if not isinstance(power, (int, float)) or isinstance(power, bool):
                problems.append(f"{where}: power {power!r} is not a number")
                continue
            if power < 0:
                problems.append(f"{where}: power {power} is below zero")
            powers.append(power)
            for axis in ("x", "y"):
                value = item.get(axis)
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    problems.append(f"{where}: {axis} at power {power} is not a number")
                elif not math.isfinite(value):
                    problems.append(f"{where}: {axis} at power {power} is not finite")
            if not item.get("x") and not item.get("y"):
                problems.append(f"{where}: power {power} is all zeros; it should not be stored")
        if len(set(powers)) != len(powers):
            problems.append(f"{where}: a power appears twice")
        if powers != sorted(powers):
            problems.append(f"{where}: the powers are not in order")
        truncation = curve.get("truncation")
        if truncation is not None:
            if not isinstance(truncation, dict):
                problems.append(f"{where}: truncation is not an object")
            else:
                for end in ("from", "to"):
                    point = truncation.get(end)
                    if not isinstance(point, dict):
                        problems.append(f"{where}: truncation has no {end} point")
                        continue
                    for key in ("t", "x", "y"):
                        value = point.get(key)
                        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                            problems.append(f"{where}: truncation {end} {key} is not a number")
                    if isinstance(point.get("t"), (int, float)) and not (0 <= point["t"] <= 1):
                        problems.append(f"{where}: truncation {end} t = {point['t']} is outside 0..1")
                if isinstance(truncation.get("from"), dict) and isinstance(truncation.get("to"), dict):
                    if truncation["from"].get("t", 0) >= truncation["to"].get("t", 0):
                        problems.append(f"{where}: truncation from is not before to")
        measured = curve.get("measured") or {}
        grid = measured.get("grid")
        if grid is not None and (not isinstance(grid, int) or grid < 1):
            problems.append(f"{where}: grid {grid!r} is not a positive whole number")
    return problems


def derived(document):
    """Re-derive what can be re-derived, so stored measurements can be checked."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import ph_quintic_metrics as metrics

    out = []
    for curve in document["curves"]:
        x, y = rows_from_terms(curve["terms"])
        measured = metrics.metrics(x, y)
        out.append({"name": curve["name"], "bend": measured["bend"],
                    "grid": int(measured["pitch"])})
    return out
