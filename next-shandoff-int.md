```text
Read state/SC-HANDOFF-int.md, then ~/developer/quintics/tools/curve_to_svg.py, then the
notes in §3 on Blender's order clamp and the missing knot vector.
You are finishing the quintic exporter and using it once by hand: write each spline's six
(x, y) control points into its SVG path as data-control="..." (plus data-degree="5"
data-endpoint="true"), then drag the six points of S_curve in
~/developer/quintics/quintic-kit.blend, re-export, and check the file round-trips.
Proves: a fresh curve.svg parses back to the same six control points that
spline.points[i].co reports, and the export log still prints control=6.
```

Source: state/SC-HANDOFF-int.md, 2026-11-26. The previous session was machine cleanup and
Blender tooling; no repository code changed, the tree is `841c40b9` plus this handoff.

Open in the background: the `coreaudiod` spin (~30%) waits on a reboot the operator has refused
for now; the Adobe paperwork (112 receipts, 12 MB shared folder, `com.adobe.*` plists) is offered
and not done.

Role: I am DeepSeek2 (the sidechat, `deep2`), the junior developer/designer. DeepSeek1, the
senior, sets direction; the operator is the top authority. I do exactly this row and stop; if it
turns out to need a design decision, I record the question in `state/SC-HANDOFF-int.md` and stop.

This file is the sidechat's only next-action pointer. `next-fhandoff-int.md`,
`state/HANDOFF-int.md`, `state/PLAN-int.md` and `state/SPRINT-int.md` belong to DeepSeek1.
