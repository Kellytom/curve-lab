```text
Read state/HANDOFF-int.md (tail only), then state/PORT-int.md, then tests/js/root-search.test.ts
and tests/js/coupler-curves.test.ts.
Close the two ports the queue lists: run the TypeScript twins against the Python on the same
fixtures, then retire `scripts/root_search.py` (it has no Python consumer) and add a
`state/PORT-int.md` row for each port — naming `tests/test_crossing_calibration.py` as
`scripts/coupler_curves.py`'s last consumer — instead of deleting a file that test imports.
Proves: `node --test tests/js/root-search.test.ts tests/js/coupler-curves.test.ts` green and
printing its parity count; `scripts/root_search.py` gone; `state/PORT-int.md` has one row per
port, each saying "retired" or naming the consumer that keeps it.
```

Source: state/HANDOFF-int.md, 2026-11-26 (the c-0022 block), and state/PLAN-int.md row 6.
Corrected 2026-11-26: both `.ts` twins already exist (2026-11-24, `scripts/root_search.ts`,
`scripts/coupler_curves.ts`, `app/src/lib/root-search.ts`, `app/src/lib/coupler-curves.ts`),
so the row is retirement and registration, not a first port.
