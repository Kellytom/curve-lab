```text
Read state/SC-HANDOFF-int.md, then state/SCToDo-int.md, then tests/test_regressions.py.
You are porting the register (542 lines, 29 tests) to a TypeScript register. First list each
test's mechanism — subprocess to a Python module, subprocess to a Node check, a browser run, or
a file/data assertion — before moving one group. Port the registry shell with node:test and
child_process, one group at a time; the Python-only modules it calls stay Python until their own
ports. Keep the same test names and the same results.
Proves: node --test tests/test_regressions.ts runs the same test names and reports the same
failures (none beyond DeepSeek1's two), and scripts/test.py's register slot uses the TS file.
```

Source: state/SC-HANDOFF-int.md, 2026-11-24, after the coupler port.

This file is the sidechat's only next-action pointer. The main session's
`next-fhandoff-int.md`, `state/HANDOFF-int.md`, `state/PLAN-int.md` and
`state/SPRINT-int.md` belong to DeepSeek1 and are not read here.

Role: I am DeepSeek2 (the sidechat, `deep2`), the junior developer/designer. DeepSeek1, the
senior, sets direction; the operator is the top authority. I do exactly this row and stop; if it
turns out to need a design decision, I record the question in `state/SC-HANDOFF-int.md` and stop.
