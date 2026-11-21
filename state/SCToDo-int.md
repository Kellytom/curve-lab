# SCToDo-int — the sidechat's own todo list

One list, one owner (me). Each item carries a `Proves:` line so it can be judged
done without re-reading anything. Work the top row; commit per item when the
gate is green; report the hash. Long items go to the background, never waited on.

---

## My long-term track — decided 2026-11-21

**My strongest ground, honestly assessed as GLM flash:** fast, disciplined work
with a clear spec and a test to guard it — ports, contracts, calibration,
measurement, documentation. Weaker ground: inventing new geometry from scratch;
that is DeepSeek1's lead and I am the measurement and search support around it.

So the order is:

### 1 · Python → TypeScript conversion (the long-term project I lead)

The site eventually runs free or low-cost on Netlify / Cloudflare Pages +
Durable Objects; no GitHub Actions runners (no monthly cost). The pattern is
already proven three times in this repo: `app/src/lib/stars.js`,
`curve-notes.ts`, and my `formula.js` + `data-export.js` — each ported with a
numeric check, not a hope.

- ~~First row: `curve_lab/measure.py` → TypeScript~~ **LANDED 2026-11-21**:
  `app/src/lib/measure.ts`, parity on 212 stored curves with **0 mismatches**
  (`app/scripts/parity-measure.mjs`), smoke test `app/tests/measure.test.mjs`
  pinned to the Python reference numbers. Three port faults caught by parity
  are recorded in `state/SC-NOTES-measure-port.md`.
- Next row: `clearance.py` → `app/src/lib/clearance.ts`, same harness.
  `Proves:` the parity script prints zero mismatches for its curves.
- Then `piece.py`, `junction.py`, `svg.py`, each with its own parity check.
- `state/PORT-int.md` is the boundary record — update it per row.
- `Proves:` per row: the parity script plus `npm --prefix app test`.

### 2 · Starlight documentation finishing (the parallel, smaller track)

The 39 doc pages are in place; what is missing is the finishing pass: draft-A
lines retired page by page as text finalises, the glossary pulled into one
place, `state/` knowledge (DATA-int, PRIME-MOVER, EXACT-NUMBERS) folded into
reader pages. Suited to me because it is style-disciplined plain English.
`Proves:` a docs build with zero "draft A" pages and `npm --prefix app run
check` green — but only when the operator says a page is final.

### 3 · Math & geometry analysis (support role, not lead)

I am strongest at the *measurement and search* side: calibrated counters, the
family sweeps, the literature map (`RESEARCH-int.md`, the sin-cos note), and
the "what is named / what is ours" verdicts. The new-curve invention itself is
DeepSeek1's to lead; I run the sweeps, pin the numbers, and code what is
decided. `Proves:` a sweep with calibrated counters only.

### 4 · The foundations track (fits between rows)

- a `--check` (dry-run) mode for every script that writes files (TODO senior-dev
  item 4; two page breakages came from scripts writing without one);
- a smoke test per generator, one known number each (item 2);
- the "exact" wording audit against DESIGN-int §Trigonometry (item 3);
- the 77 empty cells of crossings × inflections, searched with calibrated
  counters only.

---

## Immediate queue (top first)

1. **`print_plates.mjs` gains the pngquant step** (`--quality 90-99 --speed 1`)
   so the next export lands compressed — flagged to DeepSeek1; mine if handed
   over. `Proves:` a regenerated plate is within 2% of the swapped-in set's
   size for the same uid.
2. **Post-reset check-in:** read `state/SC-READING-int.md` tier 0, confirm the
   mailbox paths, run the gate. `Proves:` `scripts/mailbox.py --check --quiet`
   → ok, and the gate green.
3. **`gallery.test.mjs` red on the dirty tree** — DeepSeek1's in-flight work;
   mine to fix only if they hand the files over. `Proves:` the test green.
4. **`workbench/ph-nth-sandbox*.html` twins** — dirty and unowned; ask, then
   commit or restore. `Proves:` a clean `git status` for those two paths.

## Parked (decided, not started)

- The comparison page's floor rungs stay marked BROKEN unless the operator
  reopens the floor; the 3-colour set survives in git history (`44c2ae9b`).
- `state/PNG-COMPRESSION-int.md` carries the final numbers; no more passes
  unless the set is re-exported.

## Done this cycle (context, not a list to repeat)

Counters calibrated; the visible record (`data/`) built and guarded; the
compression studied end to end and the 90-99 set printed, swapped, committed;
the audit written (plain-English twin included); the reset files
(`SC-READING-int.md`, `SCmemory-int.md`) placed; five test guards in git.
