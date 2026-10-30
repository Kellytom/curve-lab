# Status

What works today, and what does not. The dated detail is in `HANDOFF.md`.

## Works

- **The app, on this Mac** at `127.0.0.1:8000`: presets, cap shapes, the design
  editor, the report, SVG and JSON download, and the clearance check.
- **The deployed copy**: it asks for the shared password and answers 401 without
  it, 200 with it; every page except `/health` is gated, and drawing is limited
  per visitor.
- **The engine**: 36 cap shapes, seven kinds of end, junctions and rounded
  corners, slices across a line, boxes of lines, and the clearance report.
- **The spine layer**: exact plans, loops that close, true right angles, joins
  and mirrors, width, placement on the sheet, large drawings in ordinary
  decimals, and the 150 recovered ends with their attachment points.
- **The spine import**: a chain becomes a `Piece`/`Trace` through
  `clothoid_lab/spine.py`, drawing on the 200 × 250 mm sheet with a declared
  contact that passes clearance (gates 1–3, `3f7a603`).
- **The caps transfer**: all 36 caps re-drawn on the spine layer, with a middle
  error of 0.44 per cent of their length and a worst case of 10 per cent.

## Not connected yet

- **Gate 4 is open: no W03 study is drawn from chains.** Exact chains cannot
  reproduce P01's node table (15 units of drift at 1° steps, not falling with
  finer steps); the conformance rule is the decision. See `SESSIONS.md`.
- **The recovered ends have attachment points, but nothing uses them yet,**
  apart from the extractor and the transfer study.
- **Ends that turn past 120°** and a **smoother corner blend** are not built.
- **Some cloud-study pictures are missing here** because they contain
  photographs that are not published.

## Checks

226 engine tests, 139 spine tests, the layout check green, and parity as its own
check. Dates and carried values are in `HANDOFF.md`.
