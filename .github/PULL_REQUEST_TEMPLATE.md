## What this changes

One or two sentences. Which page, module or number?

## Why

The fault or the need. If it is a fixed fault, name the test and the register
row.

## Checks

- [ ] `.venv/bin/python scripts/test.py --full` passes.
- [ ] A new test covers the change, or I say why one cannot.
- [ ] A generated page was rebuilt from its generator, not edited by hand.
- [ ] Outward pages still say `draft A` (`scripts/stamp_draft.py --check`).
- [ ] No token, key or personal path is in the diff.
