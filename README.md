# clothoid-lab

Numerical clothoid chains, out as plain editable SVG.

A clothoid, or Euler spiral, is the curve whose curvature rises linearly with
arc length. It is the transition every road and railway uses, and the shape
under a French curve. This tool builds chains of them to stated tolerance,
offsets them into ribbons, and writes SVG that Inkscape opens as ordinary cubic
Bézier nodes.

The engine is Bertolazzi's Clothoids through `pyclothoids`. Everything around
it is here: the chain model, the cubic fit, the rails, and the writer.

## Install and run

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

.venv/bin/python -m clothoid_lab.cli --preset s-curve --width 6 --out out/s-curve.svg
```

```
segments      2   length 80.000 mm
joins         G2   worst curvature jump 0.000e+00 1/mm
tightest      radius 12.732 mm at s=40.00
cubics        6  per segment [3, 3]
fit           0.0032 mm worst, 0.0032 mm spacing  (tol 0.02 mm)
rail +3.000  clear  7 cubics  error 0.0167 mm  margin 9.732 mm
rail -3.000  clear  7 cubics  error 0.0136 mm  margin 9.732 mm
verdict       inside tolerance
wrote         out/s-curve.svg
```

Presets: `s-curve`, `ogee`, `bracket`, `petal`. Options: `--tol` in mm,
`--width` for a two-rail ribbon, `--prec` for decimals in the path data,
`--design` to read a JSON design, `--json` to write one, `--quiet`.

Exit status is 0 when the fit is inside tolerance and every join is G2, 1 when
it is not. A fold in a rail is reported and does not fail the run.

## A design is data

```json
{
  "name": "s-curve 90 deg",
  "anchor": {"x": 0.0, "y": 0.0, "angle": 0.0},
  "segments": [
    {"kd": 0.0019635, "length": 40.0, "kappa0": null},
    {"kd": -0.0019635, "length": 40.0, "kappa0": null}
  ],
  "offsets": [],
  "stroke": 0.8
}
```

`kd` is curvature rate in 1/mm², `length` is arc length in mm, and `kappa0` is
the curvature the segment starts from. `null` means "continue from the previous
segment's end", which is what makes the join G2. Set a number and the jump
against the previous end is measured and printed.

## How the drawing is made

1. **Place the chain.** Each segment starts where the last ended, facing the
   direction the last ended in. Position, tangent and curvature carry across,
   so continuity is structural rather than hoped for.
2. **Cut it into cubics.** Each span takes the parabola rule's arm along its end
   tangents, chord over three cosine-squared halves. A span is bisected while
   its measured deviation from the true clothoid exceeds the tolerance.
3. **Measure, never assume.** The error is the distance from the cubic to the
   curve, found by searching arc length, not the distance to sampled points. A
   sampled metric cannot report zero, so a straight line would look bent.
4. **Offset.** Rails step along the normal and refit. A rail folds where the
   offset reaches the centre of curvature, `|d * kappa| >= 1`; the fold is drawn
   and its arc-length range and margin are printed.
5. **Write.** Absolute `M` and `C` only, fixed-point numbers with no exponent,
   one user unit to one millimetre, `width` and `height` in mm with a matching
   viewBox, no transform. The design rides along in a `<desc>` so a round trip
   has something to recover.

## What is settled

- **Bertolazzi's Clothoids, GPL-3.** The repo is GPL-3 with it, and nothing here
  can move into an unencumbered project later.
- **The fold is drawn, not clipped.** A fold is often the point of a ribbon. What
  must not happen is an unannounced one, so every rail carries its fold range in
  the report.
- **The 45 degree rule fails 0.02 mm.** Two spans over a 90 degree turn on a 40 mm
  segment is 0.024 mm off, by measurement, here. The tolerance decides, not the
  angle.
- **No path library.** Writing `M` and `C` is a formatting job, not a dependency.

## Files

- `clothoid_lab/model.py` holds the design, its JSON, and its validation.
- `clothoid_lab/engine.py` places the chain and addresses it by arc length.
- `clothoid_lab/bezier.py` holds the arm rule, the subdivision, and the error metric.
- `clothoid_lab/offsets.py` builds the rails, the fold ranges and the ribbon.
- `clothoid_lab/svg.py` writes the path data and reads the design back.
- `clothoid_lab/presets.py` holds the named starting designs, numbers derived.
- `clothoid_lab/cli.py` runs one command and prints the report.

## Tests

```sh
.venv/bin/python -m unittest discover tests
```

34 checks. The engine is held against an independent Simpson integral of the
Fresnel form, every preset against G2, the fitter against its own tolerance,
and the writer against the things that break Inkscape: exponent notation,
transforms, and coordinates that never touch the curve.

## Licence

GPL-3.0-or-later. See `LICENSE` and `ATTRIBUTION.md`.
