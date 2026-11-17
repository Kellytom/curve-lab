```text
Read state/HANDOFF-int.md. Read docs/HANDOVER.md only for durable detail.
You are starting the Bézier fitting step: fit wide-knot-x20 with cubic spans, print the maximum deviation as a share of the curve's size and the span count, and do the same for two more stored curves so the numbers are comparable.
Proves: scripts/bezier_fit.py prints, for each of three stored curves, the span count and the maximum deviation as a share of the curve size (fitted, not exact, and labelled so); every fitted curve is stated to be a drawing while the record's terms remain the curve; tests/test_bezier_fit.py passes and the printed deviation is under the tolerance the script states.
```

Source: state/HANDOFF-int.md, 2026-11-16, 5b12485.
