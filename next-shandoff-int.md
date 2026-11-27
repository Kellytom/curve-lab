```text
Read state/SC-HANDOFF-int.md, then state/SCToDo-int.md (the long-term track, §1), then
curve_lab/engine.py and state/PORT-int.md.
You are porting the clothoid engine: curve_lab/engine.py -> app/src/lib/engine.ts — Fresnel
evaluation, Placed/Chain, with parity fixtures taken from the Python chains — and adding the
row for it in state/PORT-int.md with the test in the npm list.
Proves: a parity script prints 0 mismatches against the Python chains on the fixture set, the
unit test passes, and state/PORT-int.md names the row.
```

Source: state/SC-HANDOFF-int.md, 2026-11-26, after row 2 (the variant through the save
endpoint) landed as `16ae84b7`.

Rows 3 (`print_plates.mjs` pngquant) and 6 (`gallery.test.mjs`) of
`state/SCToDo-int.md`'s Immediate queue are **waiting on DeepSeek1**: row 3 needs the hand-over,
row 6 is their in-flight files. Row 3's snap UI needs a live Inkscape session with the operator
present, so it is not an unattended row either.

Pushes are on hold until the operator says internet is back; commit locally and report the
hash.

This file is the sidechat's only next-action pointer. The main session's
`next-fhandoff-int.md`, `state/HANDOFF-int.md`, `state/PLAN-int.md` and
`state/SPRINT-int.md` belong to DeepSeek1 and are not read here.

Role: I am DeepSeek2 (the sidechat, `deep2`), the junior developer/designer. DeepSeek1, the
senior, sets direction; the operator is the top authority. I do exactly this row and stop; if it
turns out to need a design decision, I record the question in `state/SC-HANDOFF-int.md` and stop.
