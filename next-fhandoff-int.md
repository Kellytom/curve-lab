```text
Read state/HANDOFF-int.md. Read app/src/content/docs/docs/handover.md only for durable detail.
You are closing the two ports the queue lists: run `tests/js/root-search.test.ts` and `tests/js/coupler-curves.test.ts` against the same fixtures the Python uses, then delete `scripts/root_search.py` (it has no Python consumer) and add a `state/PORT-int.md` row for each port — naming `tests/test_crossing_calibration.py` as `scripts/coupler_curves.py`'s last consumer instead of deleting a file that test imports.
Proves: both node tests green with their parity count printed; `scripts/root_search.py` gone; `state/PORT-int.md` has one row per port, each saying "retired" or naming the consumer that keeps it.
```

Source: state/HANDOFF-int.md, 2026-11-26 (the sidechat/buid block), commit 47939cad.
