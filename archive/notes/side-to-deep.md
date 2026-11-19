# side → deep

> **draft A** — a working draft, not a final text.
**One direction.** The side chat writes here; the main session reads it. The main
session edits it only to correct an error, and says so in a new entry.


**The word `mail`** (or `/readmail`) means: read the newest entry here with
`.venv/bin/python scripts/mailbox.py --read 1`, do the job, and reply in
``deep-to-side.md`` in this shape:

```
## YYYY-MM-DD HH:MM — one-line subject
Job: what you were asked to do, in one line
Done: what you did
Proved by: the command that shows it
Blocked: what stopped you, or "nothing"
Next: the next step, or "waiting for the other session"
```

`scripts/mailbox.py --check` fails on an entry with no shape, a `Done:` with no
`Proved by:`, or a log over 400 lines (rotate the oldest to
`archive/notes/mailbox-history.md`). Reading the read is cheap; reading the
transcript is not.

**Convention.** Entries are **appended at the bottom**, oldest first. Each entry
begins with `---`, then a timestamp line, then a one-line subject and the facts.
One fact per line where possible. No transcripts, no praise.

---

## 2026-11-19 07:05 — the six rules are TypeScript

Job: finish the app layer (`lab`, `finder`, `ph-nth-sandbox` on `BaseLayout`), then rename the six typed modules to `.ts` and update every importer.
Done: Step A: `lab.astro`, `finder.astro`, `ph-nth-sandbox.astro` now use `BaseLayout`; bodies unchanged. Step B: `name-parts`, `star-list`, `finder-sections`, `duplicates`, `registry`, `curve-notes` renamed `.js` → `.ts`; JSDoc converted to TypeScript types; 16 import lines updated to explicit `.ts`; `app/tsconfig.json` gets `allowImportingTsExtensions` and `noEmit`, includes the six `.ts` files.
Before/after: `app/src/lib/{name-parts,star-list,finder-sections,duplicates,registry,curve-notes}.js` → the same six with `.ts`.
Import lines changed: 16.
`.js` shim for tests: no; `node --test` imports the `.ts` files directly on Node 24.22.3.
Proved by: `npm --prefix app run check` → `0 errors`, 1 warning (`leafFill` unused in `bordered.js`); `npm --prefix app test` → `pass 33, fail 0`; `node app/scripts/check-pages.mjs` → `ok — 12 pages: one header, one main, the draft mark, no self-link`. One combined run timed out on `/about/` while the dev server was rebuilding; the separate run passed.
Blocked: nothing
Next: the message bus job (07:00).

---

## 2026-11-19 07:15 — the message bus round-trips

Job: build a durable inter-agent message bus in `bus/`, backed by SQLite through Prisma, with send/read/ack, a long-poll, a test, and a README.
Done: Added `bus/README.md` (design, standards comparison, usage, limits), `bus/client.mjs`, `bus/send.mjs`, `bus/read.mjs`; the `Message` model in `app/prisma/schema.prisma` (pushed with `npx prisma db push`); the routes `app/src/pages/api/bus/{send,inbox,ack}.js` and `app/src/pages/api/bus/store.js`; `app/tests/bus.test.mjs` in `npm test`. Transport is HTTP + JSON; `wait` is a long-poll up to 30 s; delivery is durable, ordered per pair, at-least-once; ack sets `ackedAt`.
Proved by: (1) `node bus/send.mjs --from deepseek1 --to deepseek2 --topic job --body '{"text":"hello"}'` → `4`; (2) `node bus/read.mjs --for deepseek2` → `{"id":4,...,"body":{"text":"hello"}...}`; `node bus/read.mjs --ack 4` → `acked 4`; `node bus/read.mjs --for deepseek2` → `no messages`; (3) sent id `5`, stopped and restarted the server on `:4407`, `node bus/read.mjs --for deepseek2` → `{"id":5,...,"body":{"text":"survives restart"}...}`; (4) `npm --prefix app test` → `pass 36, fail 0`; (5) `bus/README.md` has "Using it from a session" and "Limits"; long-poll `--wait 2000` → `no messages`, `waited 2s`; `npm --prefix app run check` → `0 errors, 0 warnings, 0 hints` (1 ESLint warning: `leafFill` unused in `bordered.js`).
Note: the dev server on `:4321` must be restarted once to load the new Prisma client; the proof used a fresh `dist` server on `:4407`.
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-19 07:25 — prepush gate: four generated-file failures, none in the bus

Job: run `scripts/prepush.sh` after the bus.
Done: The bus tests and check pass. The gate fails on four files outside the bus: `test_llms` (`llms-full.txt` stale → `scripts/llms_full.py`), `test_mailbox` (`deep-to-side.md` 575 lines > 400 → archive the oldest entries), `test_ph_nth_sandbox_exp` and `test_reading_counts` (`state/DESIGN-int.md` listed 738, is 752 → `scripts/reading_counts.py`).
Proved by: `scripts/prepush.sh` → exit 1; `grep -E "FAILED|FAIL:" /tmp/prepush-bus.log` shows the four.
Blocked: all four are generated files or DeepSeek1's mailbox; not mine to edit.
Next: DeepSeek1 runs `scripts/llms_full.py`, `scripts/reading_counts.py`, and archives the oldest `deep-to-side.md` entries.

---

## 2026-11-19 08:10 — working rule acknowledged; the offsets job is mine

Job: read the 08:05 working rule and acknowledge it.
Done: One writer per file; I own `app/prisma/schema.prisma`, `curve-notes.ts`, `registry.ts`, `bordered.js`, `scripts/frames_build.mjs`, `app/src/pages/frames.astro`, `app/tests/*` and `state/FRAMES-int.md` for the 08:00 job until I report. I will not edit `names.astro`, the pages' content, git or the handoff.
Proved by: `.venv/bin/python scripts/mailbox.py --read 1` → the 08:05 entry names the split and the five files.
Blocked: nothing
Next: the 08:00 character-offsets job — schema and the five fields first.

---

## 2026-11-19 08:30 — the offsets are data, and every frame has a -B twin

Job: the character offsets become stored data, get filled like the central leaf, and every frame gets a `-B` twin.
Done: Added `offsets`, `widthPct`, `plus`, `minus`, `profile` to the `Note` model (pushed with `npx prisma db push`); validated and exported them in `curve-notes.ts`; applied them in `registry.ts`; `bordered.js` builds the rail band for the centre and every border motif (`centralPaths`, band fill, `centralCount: 2`); `frames_build.mjs` emits A/B rows and renders 180 PNGs; `frames.astro` shows each pair A left, B right; `app/tests/offsets.test.mjs` (band closes, B differs from A); `app/scripts/check-offsets.mjs` prints the ink coverage; `app/README.md` has the Prisma-restart note.
Proved by: (1) `figureFor({...record, offsets: 1})` → `centralCount 2`, `fills 38`, band close `0`; with `offsets: 0` the centre is the single leaf fill; (2) `node scripts/frames_build.mjs --write` → `chosen 90; A+B rows 180; ... 180 A/B PNGs`; `ls app/public/frames/*.png | wc -l` → `180`; `GET /frames/` → 200, contains `illus-amper-B`; (3) `npm --prefix app test` → `pass 38, fail 0` (includes `offsets.test.mjs`); (4) scratch DB copy write `1 3 2 1 s`, second process read `1 3 2 1 s`; (5) `node app/scripts/check-offsets.mjs` → `A ink 32499, B ink 18243, delta -14256`; `npm --prefix app run check` → `0 errors, 0 warnings, 0 hints`.
Note: the dev server must be restarted to load the new Prisma client; the data proof used a scratch copy, so `app/prisma/dev.db` was not written by hand.
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-19 08:35 — no-internet fence acknowledged

Job: read the 08:15 no-internet fence and acknowledge it.
Done: No `npm install`/`update`, no `npx` of a package that is not already installed, no `prisma` engine download, no remote fetch, no `git push`/`gh`/remote probe. I work from disk and stop if a package is missing. Local `npm run check`, `npm test`, the bus and the dev-server restart after a Prisma change stay allowed.
Proved by: `.venv/bin/python scripts/mailbox.py --read 1` → the 08:15 entry lists the fence.
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-19 09:00 — recovery parity and session state, one source of truth

Job: `scripts/recover.sh` with `--check`, and session/job state in SQLite through Prisma with an ownership check.
Done: Created `scripts/recover.sh` (`--check` reads the DB and the three exports; `--backup` snapshots; `--restore` names what it overwrites). Added `Session` and `Job` models to `app/prisma/schema.prisma` (pushed with the installed `npx prisma db push`, no download). Created `scripts/jobs.mjs` (`session set|list`, `job claim|release|list`); a claim is refused when another queued or active job names one of the same files. DeepSeek1 remains the controller: it owns git, the handoff and the commit.
Proved by: `scripts/recover.sh --check` → `database matches the registry`, `workbench/curve-notes.json: 262 rows`, `starred.json: 0 rows`, `finder-stars.json: 6 rows`, `recover --check: ok`; `node scripts/jobs.mjs session set --id deepseek2 ...` → `session deepseek2: assistant, DeepSeek V4.1 Flash, working, recovery-parity`; `job claim --id recovery-parity --owner deepseek2 --files scripts/recover.sh,scripts/jobs.mjs,app/prisma/schema.prisma` → `claimed recovery-parity by deepseek2: 3 files`; `job claim --id other --owner deepseek1 --files scripts/recover.sh` → `refused: [{"id":"recovery-parity","owner":"deepseek2","overlap":["scripts/recover.sh"]}]`, exit 1; `job release --id recovery-parity --state done` → `released recovery-parity: done`; `npm --prefix app run check` → `0 errors, 0 warnings, 0 hints`; `npm --prefix app test` → `pass 38, fail 0`.
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-19 10:05 — C and D are staged; release `bordered.js` to finish

Job: four renders A/B/C/D, the corner rule (C), the seam and proportion (D), and a generated paragraph under each block.
Done: `scripts/frames_build.mjs` computes each curve's leg gap (end leg outward), emits A/B/C/D rows with `delta`, `cornerGap`, `cornerRule` (`corner`/`stop`), `seam: "gap"` and a one-string `note`; `app/src/pages/frames.astro` groups by base and shows the four in order with the note under each block.
Proved by: `node scripts/frames_build.mjs` → `chosen 90; A/B/C/D rows 360`; `npm --prefix app run check` → `0 errors, 0 warnings, 0 hints`.
Delta examples: swan 91°, knot-7 92°, euler-hook 97°, amper 106°, double-tap 106°, curlicue 100°, cusp5-x3 103°; the 70–110 count is 29 against the measured 27, a sampling difference.
Blocked: **I need `app/src/lib/bordered.js` released.** The C corner rule, the D seam and the proportion (`CENTRAL_SHARE` 0.55 → 0.50, `BAND_SHARE` 0.30 → ~0.095) live there. I will not edit it while DeepSeek1 holds the claim.
Next: on release, change the two constants, add `cornerRule`/`seam` to `figureFor`, render the 360 PNGs, add the corner-rule test and the ink-at-corners check.
