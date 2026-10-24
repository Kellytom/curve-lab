# Spec

What this tool is for, what it refuses to do, and the numbers that decide
whether it has done the job. The original brief is preserved in the lineage of
this file; what follows is the version the code is held to.

## Purpose

Generate clothoid chains with numerical control, offset them into ribbons, and
write SVG that Inkscape opens as ordinary cubic Bézier nodes for a human to
edit.

## Goals

- Chains of clothoids with stated start curvature, curvature rate and arc
  length, joined G2 unless the design says otherwise.
- Parallel rails at signed distances, for ribbons and thickness.
- A measured fit. Every cubic says how far it sits from the true curve.
- Plain absolute-cubic SVG, millimetre units, no transform, no exponent
  notation, four decimals by default.
- A JSON design that survives the round trip, carried inside the SVG.
- Light enough to run on an eight gigabyte machine beside Inkscape.

## Non-goals

- Replacing Inkscape as the path editor.
- Real-time freehand drawing.
- A Bézier handle editor of our own.
- A polished multi-platform package, for now.

## Decisions taken

1. **Engine: Bertolazzi's Clothoids, GPL-3.** It carries the offsets, trimming
   and fitting that would otherwise be ours to write and get wrong. The cost is
   the licence: this repository is GPL-3 and stays a standalone tool.
2. **Offsets are emitted, not clipped.** Where a rail folds, `|d * kappa| >= 1`,
   the fold is drawn and its arc-length range and margin are printed. A fold is
   often the point of the shape; an unannounced one never is.
3. **No path library.** `M` and `C` are string formatting. A library here earns
   nothing and costs a dependency.
4. **No GUI yet.** The engine, the fit and the writer come first. The parameter
   window is the last piece, not the first.
5. **The tolerance decides the node count.** Not an angle rule, not a fixed
   count.

## Acceptance numbers

These are the promises, and each has a test.

- **Accuracy.** The fit error is measured as the distance from the cubic to the
  curve, minimised along arc length. It is reported per run and must not exceed
  `--tol`, default 0.02 mm. On failure the exit status is 1.
- **Continuity.** A join is G2 when the curvature jump is below 1e-9 per mm.
  Any jump is printed. Presets must be G2.
- **Engine fidelity.** The engine matches an independent Simpson integration of
  the clothoid's defining integral to 1e-9 mm.
- **Rails.** A rail holds its distance from the spine and reports its worst
  deviation. A zero-distance rail reproduces the spine inside tolerance.
- **Path data.** No exponent notation, no transform, no coordinate more precise
  than the stated decimals, and no non-finite number.
- **Round trip.** The design JSON recovered from a written SVG equals the design
  it was written from.
- **The 45 degree rule is not assumed.** Measured: two spans over a 90 degree
  turn on a 40 mm segment deviates 0.024 mm, over the default tolerance. Three
  spans give 0.0036 mm; four give 0.0009 mm. The fitter measures rather than
  counts degrees.

## The model

A design is an anchor `{x, y, angle}` and a list of segments.

```json
{"kd": 0.0019635, "length": 40.0, "kappa0": null}
```

`kd` is curvature rate in 1/mm², `length` is arc length in mm, and `kappa0` is
the curvature the segment starts from, with `null` meaning "continue from the
previous end" and therefore G2. A number is honoured as given and the mismatch
against the previous end is printed.

Rails are `offsets`, a list of signed distances in mm, or `--width`, which adds
two at half width.

## Roadmap

1. Seed the span count from the turn (about 30 degrees), then refine by error.
   Bisection from one span costs up to twice the nodes an even split needs.
2. Terminals: tapered and round ends. The ribbon outline still closes with a
   straight join.
3. The Inkscape extension: an `.inx` menu entry and a Python entry point calling
   this module, so the tool is integrated rather than exported to.
4. The PySide6 parameter window with JSON open and save, per the original brief.
5. Re-import: read a path back, replace a section with a fitted clothoid, and
   report the approximation error rather than implying a perfect inverse.
