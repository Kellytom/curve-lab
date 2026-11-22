```text
Read state/HANDOFF-int.md (the 2026-11-22 section) and docs/SIDE-CURVES.md.
You are balancing the side offsets by moving the starting point of the curves.
For each curve, when the offset curves' start and end gaps differ by (dx, dy), move the
curve's starting point by (dx/2, dy/2) so the start and end gaps match. Keep the two sides at
one strength (the average of the saved plus/minus) and the profile zero at the ends.
Proves: the offset gaps are equal on both sides and equal at the start and end; a curve whose
gaps differ before the shift has equal gaps after; `tests/js/plate-offset.test.mjs` covers the
shift; regenerate the plate set once with the finished law, not in a loop.
```

Source: state/HANDOFF-int.md, 2026-11-22, commit 3ceba869.
