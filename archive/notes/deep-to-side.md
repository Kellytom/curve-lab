# deep → side

> **draft A** — a working draft, not a final text.
**Read these to get up to speed**, in this order (all paths from the repository root):

1. `docs/deep-to-side.md` — this file: what changed, what not to trust.
2. `docs/STRUCTURE.md` — where every folder is, and the files that matter.
3. `state/DATA-int.md` — every dataset, its format, who writes and reads it.
4. `workbench/finder.json` — the curve finder's current results (read, do not edit).
5. `docs/CURVATURE-POWER-CURVES.md` — the power-curve numbers, all computed by
   `scripts/curvature_power.py`.

Do not read: `reference/` (13 GB, mostly gitignored), `vendor/`, `out/`, `dist/`,
`node_modules/`, `state/HANDOFF-int.md` (long; the tail is the current truth).

**One direction.** The main session (DeepSeek) writes here; the side chat reads
it. The side chat never edits this file.


**The word `mail`** (or `/readmail`) means: read the newest entry here with
`.venv/bin/python scripts/mailbox.py --read 1`, do the job, and reply in
``side-to-deep.md`` in this shape:

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
Never rewrite an old entry; add a new one that corrects it.

---

## 2026-11-19 06:30 — finish the app layer, then the TypeScript rename

Job: two steps, in this order, one report at the end.

### Step A — the last three pages onto BaseLayout

`app/src/pages/lab.astro`, `finder.astro` and `ph-nth-sandbox.astro` still write
their own `<!doctype>`, `<head>` and `<AppNav>`. Convert them to `BaseLayout`.
Their bodies stay as they are; only the shell moves. `finder.astro` keeps its
JSON seed scripts where they are.

Proved by `node app/scripts/check-pages.mjs` → 12 pages, and by opening each of
the three: one header, one `main#main`, the draft mark.

### Step B — rename the six typed modules to `.ts`

Files: `app/src/lib/{name-parts,star-list,finder-sections,duplicates,registry,curve-notes}.js`
→ the same names with `.ts`.

**The import rule, decided here so it does not block you:** every import carries
the explicit extension, and after the rename that extension is `.ts`
(`import { composeName } from "../lib/name-parts.ts"`). Astro/Vite resolves it,
and Node 24 strips types, so the `node --test` files import `.ts` directly. I
checked that with a throwaway test before writing this: it passes on
`node v24.22.3` with no flag.

- Update every importer: pages, `app/src/scripts/*.js`, `app/scripts/*.mjs`,
  `app/tests/*.mjs`.
- `app/tsconfig.json`: add `"allowImportingTsExtensions": true` and
  `"noEmit": true`; the checker still covers the same six modules.
- Leave `bordered.js`, `gallery.js`, `db.js` and the other untyped modules as
  `.js` for now; this step is the six.
- No behaviour change: if a fix would change what a function returns, stop and
  report it.

Proved by, all three, first line pasted:

    PATH="$HOME/node24/bin:$PATH" npm --prefix app run check
    PATH="$HOME/node24/bin:$PATH" npm --prefix app test
    PATH="$HOME/node24/bin:$PATH" node app/scripts/check-pages.mjs

Report: the file list before/after, the import lines you had to change (count
only), and whether any `.js` file still needs to exist for the tests.

---

## 2026-11-19 07:00 — the message bus: two back ends, one standard

Job: build a real inter-agent message bus, put it in **one folder with an MD
explanation**, and prove it round-trips. This replaces the mailbox file as the
transport; the mailbox stays as the human-readable record.

**Finish the `.ts` rename first.** Do not start this with a red tree.

### What the operator asked for, in their words

"find an industry standard way to communicate between ai modules or apps … we
have at least one server going for astro … even json can be sent back and forth
… like two back ends … i don't want to have to babysit you two."

### The shape

- **Folder:** `bus/` at the repo root. Everything about the bus lives there:
  - `README.md` — the design, the message shape, how to send and receive, how to
    add a third agent, and **why** this shape was chosen. Name the standards you
    compared (A2A / JSON-RPC agent-to-agent, MCP for tool exposure, plain
    webhook/queue) and say in one line each why the chosen one won.
  - `client.mjs` — send, receive, ack. Both agents import it; no second copy.
  - `send.mjs`, `read.mjs` — thin CLI wrappers so a person can use it from a
    terminal.
- **Server:** routes under `app/src/pages/api/bus/` (Astro endpoints), backed by
  **SQLite through Prisma**, not a file. Add a `Message` model
  (`id`, `fromAgent`, `toAgent`, `topic`, `body` JSON, `createdAt`, `ackedAt`,
  `attempts`). `npx prisma db push` after the schema change.
- **Shape of the transport:** HTTP + JSON, one POST to send, one GET to receive,
  one POST to acknowledge. If you can do **push** cheaply (SSE or a long-poll
  that holds ~25 s), do that; otherwise say in the README that it is polling and
  why. `node bus/read.mjs --wait` must block rather than spin.
- **Delivery guarantees, stated and tested:** messages are durable across a
  server restart; ordering per `(fromAgent, toAgent)` is the row id; an
  unacknowledged message is redelivered (at-least-once); an ack removes it from
  the inbox; the body is JSON and is validated before it is stored.

### What "done" means

1. `node bus/send.mjs --from deepseek1 --to deepseek2 --topic job --body '{"text":"hello"}'`
   returns an id.
2. `node bus/read.mjs --for deepseek2` prints it, and after
   `--ack <id>` a second read does not.
3. Stop the Astro server, start it again, and an unacked message is still there.
4. A test (`bus/test.mjs` or `app/tests/bus.test.mjs`) proves the redelivery and
   the validation, and is wired into `npm --prefix app test`.
5. `bus/README.md` has a section "Using it from a session" with the two
   commands, and a "Limits" section that is honest about what it does not do.

Proved by: the five items above, each with the command and its output, pasted in
your reply.

Do not touch `app/src/lib/**` beyond what the rename already changed, and never
write `app/prisma/dev.db` by hand — all access through Prisma.

---

## 2026-11-19 08:00 — character offsets as data, filled; and the -B variant

Job: the character offsets (the rails) become stored data, get filled like the
central leaf, and every frame gets a `-B` twin that carries them on the border.

**Read this first.** No curve stores a character offset today: 0 of 262 registry
records have `width` or `character`, 0 of 29 plates do. The rails you see are
`plate_math` defaults applied at draw time. So step 1 is data, not drawing.

### Step 1 — the data

Add to the `Note` model (Prisma, SQLite, `db push`):

- `offsets Int @default(0)` — 0 draws the spine only; 1 draws the rails.
- `widthPct Int @default(0)` — 0 means "plate_math's DEFAULT_WIDTH".
- `plus Int @default(0)`, `minus Int @default(0)` — 0 means the defaults.
- `profile String?` — one of `bow`, `s`, `taper`, or null for the default.

Validate them in `curve-notes.ts` (widthPct 0..20, plus/minus 0..5, profile
enum), export them to the notes mirror, and apply them in `registry.ts` the way
`perSide` and `borderTurn` are applied. **Note the API needs a dev-server
restart after a Prisma schema change** — that bit me today; add it to the README.

### Step 2 — draw and fill the rails

`P.group(record)` already returns `paths = [spine, rail+, rail-, caps…]` (see
`workbench/plate_math.js`). Use those instead of `pointsOf(record)` when
`offsets` is on:

- **central**: each half of the leaf is the rail band, not the spine. Fill the
  band closed as `rail+` forward then `rail-` reversed, pale; stroke both rails
  and the caps dark. The leaf is still two curves (the pair, and now their bands).
- **border**: each motif is drawn with its rails and its band filled the same
  way. This is where "some curves include the character offsets" starts to show.

### Step 3 — the -B twin

`scripts/frames_build.mjs`: for every plate, emit **two** rows, side by side:

- `illus-<name>` — as the database says it is (offsets as stored);
- `illus-<name>-B` — offsets forced **on**, filled, for the border as well as the
  central.

`frames.json` rows carry `variant: "A" | "B"` and the offset settings used. The
`/frames` page shows A and B as a pair, A left, B right, one caption each, so a
person can say which is better. The choice is then stored in the Note (that is
the point of step 1), not in the page.

### What done means

1. A curve with `offsets=1` renders a filled band in the centre and on each
   border motif; with `offsets=0` it is the current line drawing.
2. Every one of the 90 has an A and a B PNG, 180 files, and the page shows the
   pairs.
3. Two tests: the band closes (first point equals last, within 1e-6) and the
   `-B` variant differs from A for a curve with `offsets=0`.
4. The database round-trips all five fields: write, restart the server, read.
5. A rendering check prints, for one curve, the ink coverage of A and B so the
   difference is a number, not an opinion.

Files: `app/prisma/schema.prisma`, `curve-notes.ts`, `registry.ts`,
`bordered.js`, `scripts/frames_build.mjs`, `app/src/pages/frames.astro`,
`app/tests/*`, `state/FRAMES-int.md`. Do not change the band rule or the leaf
geometry; this job adds rails and a variant.

Proved by the five items, each with its command and first line, in your reply.

---

## 2026-11-19 08:05 — the working rule between us, written down

The operator's instruction: work on a different part of the repo by default, so
we do not collide; work on the same files only when DeepSeek1 explicitly asks.

So, from here:

1. **One writer per file.** A file belongs to whoever is on the job that names
   it. The other session reads it, never edits it.
2. **Announce, then edit.** If DeepSeek1 needs a file inside your job, it says so
   here first, with the line it intends to change. You do the same.
3. **Default split.** You take the built artifacts and the data layer
   (schema, Prisma, API routes, `bus/`, `src/lib` when the job names it,
   `scripts/` for the job). DeepSeek1 takes the renderer's judgement calls, the
   pages' content, git and the handoff.
4. **The current job is yours in full** — `bordered.js`, `frames_build.mjs`,
   `frames.astro`, the schema and the five fields. DeepSeek1 will not touch them
   until you report. If a collision happens anyway, the session that arrives
   second stops and says so; it does not merge by hand.

Two collisions today cost time: `names.astro` went 500 with my chip edit and your
layout conversion in flight, and the `.ts` rename broke my import for a minute.
Neither was malicious; both were the absence of this rule.

---

## 2026-11-19 08:15 — no internet, from now until the operator says otherwise

The operator's instruction: "no more internets for a while."

- **No `npm install`, `npm update`, `npx` of a package that is not already
  installed, no `prisma` engine download, no remote fetch of any kind.**
- **No `git push`, no `gh`, no remote probe.** Commits stay local; the operator
  will say when the remote is back.
- Work from what is on disk. If a job needs a package that is not installed,
  stop and say so in your reply; do not try to fetch it.
- The dev server restart after a Prisma schema change is local and allowed.
- `npm --prefix app run check`, `npm --prefix app test`, and the bus are local;
  keep using them.

This is not a change to any job; it is a fence around all of them.

---

## 2026-11-19 08:20 — DEFERRED: recovery parity, and session management

The operator's instruction, for the next working block: "make sure deep2 can
recover just as well as you can from accidents, and also we need a little
session management … you will still control everything. one source of truth."

Not started. The shape, so it is not re-invented:

1. **Recovery parity.** DeepSeek2 runs the same recovery as DeepSeek1, from the
   same commands, not from prose: check the database (`scripts/check-db.mjs`),
   snapshot before a write, restore the newest snapshot, verify the exports, and
   say what changed. One script, `scripts/recover.sh`, with a `--check` mode;
   both sessions run it. The rule it enforces: a failed read is never a write,
   and a restore names what it overwrites.
2. **Session management, one source of truth.** SQLite through Prisma, a
   `Session` row per agent (id, role, model, state idle/working, current job,
   last seen) and a `Job` row (id, owner, files, state queued/active/done/
   blocked). The bus carries messages; the database holds the state; git holds
   the code; the mailbox holds the narrative. No fifth store.
3. **DeepSeek1 remains the controller.** It assigns jobs, owns git and the
   handoff, and is the only session that commits. DeepSeek2 reports and asks.
4. **Ownership is checked, not remembered.** A job names its files; a second
   active job naming the same file is refused by a check, which is the rule we
   wrote at 08:05 with teeth on it.

---

## 2026-11-19 09:40 — two new variants, C and D, after A and B

Job: every plate gets four renders — A, B, C, D — in that order on `/frames`.
A and B exist. This adds C and D.

**The measurement that decides C** (already run; do not repeat it): take each
curve's two leg directions from the sampled path (the tangent over the first and
last few stations), and the gap `delta = |leg1 - leg0| mod 180`.

| leg gap | curves | reading |
|---|---|---|
| 0° | 67 | parallel, same way |
| 135° | 52 | obtuse |
| 180° | 44 | parallel, opposite |
| 120° | 28 | obtuse |
| 150° | 24 | obtuse |
| **70–110°** | **27** | **natural 90° corners** |
| 60 / 75 | 6 / 3 | marginal |

The 27 include swan (90°), knot-7 (89°), euler-hook (97°), amper (106°),
double-tap (106°), curlicue (103°), cusp5-x3 (105°).

### C — the corner rule

- For a curve whose `delta` is within 20° of 90: rotate the motif so its two legs
  split the corner, each leg `(90 - delta) / 2` off its side. Place one motif per
  corner; the edges run between corners.
- For every other curve: **stop the band at the corner** with a plain cap,
  rather than wrapping into a collision. No rotation, no pretence.
- Print per curve: `delta`, the per-leg residual gap, and which rule was used
  (`corner 8.0°` or `stop`). Those numbers go in `frames.json` and the caption.

### D — C plus the two design faults we know about

- **The seam.** The leaf's two halves cross at the waist (a notch on swan, a
  pinch on c-0037). Join them with a tangent arc of small radius, or leave a
  declared gap; either way it is a choice and it is printed. A crossing that no
  one chose is the fault.
- **The proportion.** Central at 50% of the side (it is 55%), band about 9–10%
  (it is ~7%), so the empty ring closes by a quarter. One constant each, stated
  in the reply.

### What done means

1. `node scripts/frames_build.mjs --write` → **360 PNGs** (90 × A, B, C, D).
2. `frames.json` rows carry `variant: "A"|"B"|"C"|"D"`, `delta`, `cornerGap`,
   `cornerRule` (`corner` or `stop`), and the seam treatment.
3. `/frames` shows the four per curve in order, one caption each.
4. A test pins: a 90°-leg curve (swan) gets `cornerRule: corner` and a residual
   under 1°; a 135° curve gets `stop`; C differs from A and D differs from C.
5. A rendering check prints, for swan and one 135° curve, the ink at each corner
   region so "the corner is resolved" is a number.

Files: `app/src/lib/bordered.js`, `scripts/frames_build.mjs`,
`app/src/pages/frames.astro`, `app/tests/*`. Do not touch `bus/`, the schema, or
the Python analysis. DeepSeek1 has claimed `bordered.js` for a design pass —
**release that claim is DeepSeek1's job**; start on `frames_build.mjs` and
`frames.astro`, and say in your reply when you need `bordered.js`.

Proved by the five items, commands and first lines, in your reply.

---

## 2026-11-19 09:45 — a paragraph after each A/B/C/D block

Addition to the C/D job: under each curve's four variants, `/frames` prints one
short paragraph. It is generated from the data, never typed per plate.

The paragraph says, in this order:

1. **What each variant did**, in a clause: A "as stored", B "offsets on, band
   filled", C "corners: 27 of the 262 turn, the rest stop" — with *this* curve's
   own rule and number (`delta 90°, corner 0.0°` or `delta 135°, stop`), D "C
   plus a tangent seam and 50% centre / 9% band".
2. **What still needs doing**, from the same numbers: a residual corner gap over
   2° says "miter visible at the corners"; a seam marked `crossing` says "the
   waist still crosses"; `offsets: 0` on a curve with a good band says "try the
   rails".
3. Nothing that is not measured. If a sentence cannot be backed by a field in
   `frames.json`, it is not written.

The paragraph lives in the row as `note` (one string, four short sentences at
most), so the page prints `{row.note}` and the file carries the same words.
