# deep2 — DeepSeek2's sandbox for images → equations

*The operator, 2026-11-23: "make a folder just for you deep2, and make a
sandbox and whatever you need to save images (dont worry about licenses
because we will be modifying them) and work on them to convert to
equations."*

This folder is the working area for turning reference images into the
project's curve language. Images are saved here modified by tracing; each
file's source is recorded in `refs/`. The house rules still hold: y up, cubic
spans, exact stations, numbers with their scripts.

## The pipeline (working, measured)

```
refs/<image>  --trace.py-->  spans/<name>.json  --measure_spans.py-->  out/*.svg
```

- **`trace.py`** — image → cubic spans. Three mask modes:
  - `--silhouette`: dark figure on a bright sky, Otsu cut (the reliable one);
  - `--lithograph`: cream paper flood-filled from the borders (holy cards);
  - default `photo`: colour rules for a green/white background.
  Optional `--crop x0,y0,x1,y1` and `--outname name`. potrace does the
  bitmap → Bézier step; the script reads potrace's cubics back into our span
  dicts (y flipped, normalised to the figure's height) and draws the result
  from the data, not from potrace's file.
- **`measure_spans.py`** — the numbers: span count, join continuity (kink
  angles), and the snap cost to a 1/1000 grid; writes a snapped SVG.

## What is already converted

| reference | source | spans | state |
|---|---|---|---|
| `corcovado-silhouette.jpg` → **redeemer** | Wikimedia, sunset silhouette (cropped) | **35** | traced, snapped at 1/1000 (largest move 0.0005 of height), joins max 7.70° — a smooth outline |

The first human figure in equations: the Christ the Redeemer, open arms —
the pose the centre of an ornament wants.

## What this is not yet

- It is a **trace**, not a construction: no canon proportions, no G3 gates,
  no PH equations. The face is not in it (a silhouette has no face).
- The next steps, in order: (1) the figure's canon overlay (Byzantine
  proportions) so the trace can be judged against landmarks; (2) per-part
  spans (face by engraved tone — Ostromoukhov's rule — not by outline);
  (3) the silhouette re-built as exact rational spans, not quantised floats.

## Files

- `refs/` — the saved images (statue photo, Pantocrator icon, Currier & Ives
  lithographs, the Corcovado silhouette). Wikimedia Commons; modified by
  tracing in this folder.
- `spans/` — the span JSONs (source of truth for each conversion).
- `out/` — masks, potrace SVGs, drawings from our spans, previews.
- `notes/` — free notes.
