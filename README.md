# clothoid-lab

Numerical clothoid chains, out as plain editable SVG.

A clothoid, or Euler spiral, is the curve whose curvature rises linearly with
arc length. It is the transition every road and railway uses, and the shape
under a French curve. This tool builds chains of them to stated tolerance,
offsets them into ribbons, and writes SVG that Inkscape opens as ordinary cubic
Bézier nodes.

The engine is Bertolazzi's Clothoids, compiled from the vendored source and
called through a small C surface. Everything around it is here: the chain
model, the cubic fit, the rails, and the writer.

## Install and run

```sh
bash scripts/build-native.sh          # compiles the engine, about a minute
python3 -m venv .venv                 # nothing to install: no runtime deps
.venv/bin/python -m clothoid_lab.cli --preset s-curve --width 6 --out out/s-curve.svg
```

The build needs a C++ compiler and nothing else. If the compiler is unavailable,
install the wheel and ask for it: `pip install -r requirements-dev.txt`, then add
`--backend pyclothoids` or `export CLOTHOID_BACKEND=pyclothoids`. The wheel carries
the same engine, which is why it works as a cross-check and not as the default.

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
`--width` for a two-rail ribbon, `--page WxH` to fix the page in mm, `--prec` for
decimals in the path data, `--split` for how many pieces a span is cut into,
`--backend` to choose the engine, `--design` to read a JSON design, `--json` to
write one, `--watch` to rebuild on save, `--quiet`.

`--page` matters in the two-window loop: with an automatic page every parameter
change resizes the document and the viewer re-fits, so the zoom moves under your
hand. A fixed page keeps the viewBox constant and the drawing moves inside it.

A rail that folds reverses inside a span, where the parabola arm runs away and
would place a control point tens of metres out. The arm is bounded at four times
the chord, and each clamped span is counted in the report rather than hidden.

Exit status is 0 when the fit is inside tolerance and every join is G2, 1 when
it is not. A fold in a rail is reported and does not fail the run.

## Two windows

Start the watcher, keep Inkscape open on the drawing, edit the design on the
other side, and save.

```sh
.venv/bin/python -m clothoid_lab.cli --watch \
    --design out/play.json --seed ogee --width 6 --out out/play.svg
```

```
seeded out/play.json from preset ogee
built     8 cubics  0.0050 mm  bertolazzi  ok
watching out/play.json -> out/play.svg   (ctrl-c to stop)
rebuilt   8 cubics  0.0031 mm  bertolazzi  ok
```

Inkscape notices the file changed and offers to reload. The write is atomic, so
it never opens a half-written file, and a design that does not parse leaves the
last good drawing untouched, because typing a number passes through states that
are not valid JSON.

This is generate-and-look, not a round trip: a rebuild replaces the file, so node
edits made in Inkscape are lost on the next save. The extension is what closes
that loop.

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
   tangents, chord over three cosine-squared halves. A span that misses the
   tolerance is redivided `--split` ways, two by default.
3. **Measure, never assume.** The error is the distance from the cubic to the
   curve, found by searching arc length, not the distance to sampled points. A
   sampled metric cannot report zero, so a straight line would look bent.
4. **Offset.** Rails are the library's exact parallel curve (`X_ISO`, `Y_ISO`),
   refitted to cubics. A rail folds where the offset reaches the centre of
   curvature, `|d * kappa| >= 1`; the fold is drawn and its arc-length range and
   margin are printed.
5. **Write.** Absolute `M` and `C` only, fixed-point numbers with no exponent,
   one user unit to one millimetre, `width` and `height` in mm with a matching
   viewBox, no transform. The design rides along in a `<desc>` so a round trip
   has something to recover.

## What is settled

- **The engine is compiled from source, BSD-2-Clause.** No wheel in the critical
  path, no copyleft: our code is MIT and can move between projects. The wheel is
  kept as a second opinion on the wrapper.
- **The fold is drawn, not clipped.** A fold is often the point of a ribbon. What
  must not happen is an unannounced one, so every rail carries its fold range in
  the report.
- **The 45 degree rule fails 0.02 mm.** Two spans over a 90 degree turn on a 40 mm
  segment is 0.024 mm off, by measurement, here. The tolerance decides, not the
  angle.
- **No path library.** Writing `M` and `C` is a formatting job, not a dependency.
- **The split factor is a dial, not a saving.** Measured on a 90 degree turn at
  0.02 mm: two-way splitting reaches tolerance in three spans per segment, a
  four-way split needs four. The default stays two.

## Files

- `clothoid_lab/model.py` holds the design, its JSON, and its validation.
- `clothoid_lab/engine.py` places the chain and addresses it by arc length.
- `clothoid_lab/bezier.py` holds the arm rule, the subdivision, and the error metric.
- `clothoid_lab/offsets.py` builds the rails, the fold ranges and the ribbon.
- `clothoid_lab/svg.py` writes the path data and reads the design back.
- `clothoid_lab/presets.py` holds the named starting designs, numbers derived.
- `clothoid_lab/backend/` holds the ctypes surface and the wheel adapter.
- `clothoid_lab/cli.py` runs one command and prints the report.
- `clothoid_lab/watch.py` holds the two-window loop and its safety rules.

## Tests

```sh
.venv/bin/python -m unittest discover tests
```

46 checks. The engine is held against an independent Simpson integral of the
Fresnel form, every preset against G2, the fitter against its own tolerance,
and the writer against the things that break Inkscape: exponent notation,
transforms, and coordinates that never touch the curve. The two backends are held
against each other, and the watcher is held against a broken edit, which must not
blank the drawing.

## Known roughness

- A rebuild replaces the whole file, so node edits made in Inkscape are lost.
- `--reopen` asks the macOS open handler for the file, which can hand Inkscape a
  second window and break a tiled layout. It is off unless you ask for it.
- The error is measured from the cubic to the curve, not the curve to the cubic,
  so a span that skipped a piece of curve would report small.

## Licence

MIT for this project. The vendored engine is BSD-2-Clause, Eigen is MPL-2.0, and
the optional wheel is MIT. See `LICENSE` and `ATTRIBUTION.md`.
