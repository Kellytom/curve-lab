notes Oct 24.md

It wasn't integrated. The C surface had one unused primitive, cl_push_G1 (continue the chain to a point), bound in Python and called by nothing. There was no two-point fit, no spline through points, and no CLI path. Now there is.
What I added
- csrc/clothoid_api.cpp — three functions over the vendored library:
- cl_g1_fit — Bertolazzi and Frego's buildClothoid: one clothoid through two points with a direction at each, returning k, dk, L.
- cl_build_g1 — the spline through n points, directions estimated or supplied.
- cl_segment — reads each fitted piece back as x0, y0, theta0, kappa0, dk, L.
- clothoid_lab/backend/bertolazzi.py — g1_fit() and g1_spline() through ctypes.
- clothoid_lab/interpolate.py — fit(), from_points(), parse(), load(); turns the fit into an ordinary Design of segments with explicit curvature, so the existing fitter, rails, SVG writer and report all work unchanged.
- CLI: --points FILE (JSON or x, y per line, # comments), and --watch --points FILE to refit on save.
- model.py: a g1: true flag, because curvature jumps at the points are the fit, not a defect — the report says so and the run exits 0 instead of failing.
- tests/test_interpolate.py: interpolation, directions, G1 joins, round trip, parsing, CLI. 68 tests pass (was 46).
- Rebuilt build/libclothoidlab.dylib; README and SPEC updated.
Use
.venv/bin/python -m clothoid_lab.cli --points out/route.txt --width 4 --out out/route.svg
segments      4   length 55.461 mm
joins         G1   G1 spline through the points: curvature jumps are the fit
fit           0.0100 mm worst  (tol 0.02 mm)
verdict       inside tolerance, G1 spline by construction
Measured: every supplied point hit within 1.3e-14 mm, directions within 1e-9 rad, joins tangent-continuous. Directions can be pinned per point with "thetas" in the JSON; otherwise they're estimated.
Two honest limits: it's G1, not G2 (curvature jumps at the points), and it needs the compiled backend — the pyclothoids wheel has no G1 API, so that path now gives a clear error instead of a wrong answer. No new dependency: the algorithm is already in the vendored BSD-2 library.






- Page now 120 × 200 mm portrait, design rotated 90°, ribbon 4 mm, stroke 0.5 (draws at ~1.2 mm after frame scaling).
- Verified: G2, 0 crossings, no rail folds, 12 cubics, 0.0094 mm.
- Watcher restarted with --width 4 --frame 120x200 (pid 3815, log /private/tmp/play-watch.log).
- Cmd+Option+R is now File → Revert. Installed in Inkscape's user keymap via scripts/bind_shortcut.py; Inkscape was restarted so it's live.
- The "top left" view was a stale saved view (zoom 3.5 aimed at the old landscape page) that the watcher faithfully preserved. I reset it to zoom 3.6 centred on (60,100), so it opens fitted. If it ever drifts, 5 is Inkscape's built-in "fit page in window" — one key, no panning.
What's actually needed for splicing and terminals — not Rust, not JS, not libraries

The hard geometry is already compiled C++ (Bertolazzi). Python is doing the cheap part. More languages would add toolchains and no capability. The gaps are design-layer:

1. Splice model — pieces with their own local frame and name, assembled head-to-tail with tangent + curvature checks. ~150 lines on top of model.py.

2. Terminals as geometry — today rails just stop with a straight cut. Clothoid terminals need a width envelope (half-width varying with s) for tapers and looped ends. That's the one real algorithmic addition.

3. Outline assembly + a real --check — stitch rails to terminals, then test the closed outline for self-intersection, clearance, folds and aspect. I did that test by hand today; it belongs in the CLI.

4. Design files that carry the sheet — move page, frame, width, stroke into the JSON so a design is one file and the watcher command never changes.

5. Exploration tooling — the contact sheet I built ad hoc, plus seeded sweeps. That's how you make a lot of designs quickly.



***

how CAD layout engines (like Grasshopper/Rhino) natively approximate these transitions for vector profiles? [1] (https://www.youtube.com/watch?v=EMeGqOE2QQ4), [2] (https://www.youtube.com/watch?v=s9LWqewG8EY&t=476)
