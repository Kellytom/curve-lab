```text
Read state/HANDOFF-int.md. Read app/src/content/docs/docs/handover.md only for durable detail.
Fix the band fill for a path curve, so the 185 path records can print rails.
Proves: node scripts/print_plates.mjs --only c-0273 draws both bands with no filled blob, the offset never crosses the spine, and tests/js/plate-path.test.mjs fails without the fix.
```

Source: state/HANDOFF-int.md, 2026-11-20 (commit ff1f1c98), "character rails reach the plate, the ground goes transparent".
