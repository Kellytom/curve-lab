```text
Read state/SC-HANDOFF-int.md, then state/SCToDo-int.md (Immediate queue, row 2), then
inkscape/ph_variant.py and the app's own save endpoint that the tune desk posts to.
You are posting the variant payload that `inkscape/ph_variant.py` builds through the app's
save path — not into the registry directly — and making the tune page show the candidate it
produced.
Proves: a posted variant appears in `data/` with `base_uid` set and
workbench/curve-registry.json untouched, and the tune page shows that candidate.
```

Source: state/SC-HANDOFF-int.md, 2026-11-25, after the register port — the commit that added
`tests/test_regressions.ts` is `git log -1 --format=%h -- tests/test_regressions.ts`.

Rows 5 and 7 of `state/SCToDo-int.md`'s 2026-11-24 set are **waiting on DeepSeek1**: row 5
needs the declared loop shape before any code, and row 7 (retiring the Python twin of the
register) edits their Tier-0 docs and the `f` commands.

Pushes are on hold until the operator says internet is back; commit locally and report the hash.

This file is the sidechat's only next-action pointer. The main session's
`next-fhandoff-int.md`, `state/HANDOFF-int.md`, `state/PLAN-int.md` and
`state/SPRINT-int.md` belong to DeepSeek1 and are not read here.

Role: I am DeepSeek2 (the sidechat, `deep2`), the junior developer/designer. DeepSeek1, the
senior, sets direction; the operator is the top authority. I do exactly this row and stop; if it
turns out to need a design decision, I record the question in `state/SC-HANDOFF-int.md` and stop.
