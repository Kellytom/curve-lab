# Quintic guides — the test sheet

Drop Inkscape `.svg` files here. Each one needs at least one path to be the
guide; the extension uses the **first path in the selection**, so run the batch
tool with the file's path selected by id:

```sh
.venv/bin/python scripts/quintic_report.py --sheet workbench/quintic-guides --spans 3
```

That runs the **installed** extension over every `.svg` here and prints, per
file: the point mode, alpha, cubic count, the drawn→quintic max and RMS miss, and
whether the curve left its own six points.

Guidelines for a useful guide file:

- a freehand-looking stroke is best — five or six cubics with uneven spacing,
  like a trackball or pencil line, not a pair of arcs;
- one path per file, with an `id` so it can be selected;
- leave the stroke pale and dotted, as the working practice does;
- keep the drawing at a sensible document scale (a few hundred px), because the
  tolerance and the miss are both in px.

`--mode` switches the reduction: `even` (six points on the stroke, default),
`lsq` (best fit), `cage-nodes`, `cage-samples`. `--spans N` splits each stroke
into N quintics, each with its own six points.
