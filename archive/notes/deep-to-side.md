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

## 2026-11-17 19:20 — numbers in documents are computed

`docs/CURVATURE-POWER-CURVES.md` had a correct formula and a wrong table: n = 4
read 0.535, the true value is 0.511, and the septic superellipse had its maximum
and minimum swapped. The fix is `scripts/curvature_power.py`; the page now
carries κ_max too. Rule: compute, cite the script, or write "unverified".

---

## 2026-11-17 19:10 — what was being built

The curve finder: properness (is a parametric curve a cover of a simpler one?)
and the curvature peak with its tangent angle. Engine `curve_lab/reduction.py`,
data `workbench/finder.json`, page `/finder`.

---

## 2026-11-17 19:45 — curve finder, first results

- Engine: `curve_lab/reduction.py`. A curve is proper when no other parameter
  lands on the same point; the test is the shared factor of the two divided
  differences. A monomial cover collapses (`(t²,t⁴)` → `(u,u²)`, cover ×2).
  A non-monomial cover is detected but the substitution is **not** built yet.
- Data: `workbench/finder.json` (12 curves). Page: `/finder`, also in the hub.
- Measured on y = x^n, t in [0,1]: the curvature peak sits at tangents of
  **24.1° (n=3), 28.1° (n=4), 30.0° (n=5), 31.8° (n=7), 32.7° (n=9)** — never
  45°. A 45° tangent occurs at x where n·x^(n−1) = 1, which is not the peak.
- So the 45° hunch is not confirmed on this family. Do not repeat it as fact.

---

## 2026-11-17 19:55 — where the files are

`docs/STRUCTURE.md` lists the top-level tree with file counts and the files that
matter. Read it before hunting. The short version: `curve_lab/` is the engine,
`scripts/` the generators and audits, `workbench/` the generated pages and their
JSON, `app/src/` the Astro site, `state/` the working memory, `docs/` the book.
Large and excluded: `.git`, `node_modules`, `.venv`, `vendor/`, `reference/`,
`out/`, `site/`, `dist/`.

---

## 2026-11-17 20:00 — absolute root

The repository root is the folder you cloned, not nested in another project.
Every path in `docs/STRUCTURE.md` is relative to that root; `$REPO` means that
directory.

---

## 2026-11-18 00:10 — the curve finder's current state

- Stored finds are PH: `u = 1 − 2t + 2t²`, `v` = `(t−p)(t−1+p)(t−½)^m` scaled to
  integers. `lace-1of8-3` matches `p = 1/8, m = 3` exactly.
- Properness ≠ no loops. A loop is a finite failure of injectivity; the reduction
  test only finds covers. Do not say "proper, so no crossings".
- The design family is `x = Q − P, y = Q + P` (P odd, Q even). Crossings are
  two linear equations; 45° tangent is `P' = 0`; the axis crossing is `P = 0`.
- `/finder` shows solved crossings and weighted-balance curves; stars save to
  `workbench/finder-stars.json` (backup kept). Curvature peaks on loop cards are
  **cusps**: the κ figure is unbounded and the page does not say so yet.

---

## 2026-11-18 02:10 — trig is a red flag

`cos`/`sin` of a general angle is irrational and leaves the integer grid for good.
Rational points of the circle are fine (`3-4-5`, `7-24-25`, or `t = tan(θ/2)`
with rational `t`, giving exact fractions like `(527/625, 336/625)`). Any figure
drawn by sampling real trig must be captioned **sampled** and must claim no
exactness. The rule and its reasoning are in `state/DESIGN-int.md`
§Trigonometry; it is also in `AGENTS.md` and `LTMemory-int.md`.

---

## 2026-11-19 02:10 — hand-off: the click-everything gate, on a scratch database

**Job.** Build the browser gate we are missing: open each of the 12 app pages,
press every control that is safe to press, and fail on any page error, any
duplicate card, any refused write. Then run it against a *copy* of the database,
so a click can never touch the record the operator is naming into.

**Files you own (create or edit only these).**

- `app/scripts/check-clicks.mjs` — the sweeper.
- `app/scripts/test-server.mjs` — starts a server with its own database, waits
  for health, runs the checks, stops the server, removes the copy.
If you find a bug in another file, **do not fix it**: report it here and leave
the file alone.

**Current facts, measured 2026-11-19.**

- Astro 7.4.13 on Node 24.22.3 at `~/node24`. Dev server on `:4321`, one daemon
  per project; a second `astro dev --port 4399` is refused ("already running").
- So a second instance is `npm --prefix app run build` then
  `node app/dist/server/entry.mjs` with `PORT` and `DATABASE_URL` set.
- Prisma reads `DATABASE_URL`; `app/prisma/dev.db` is the record and is
  gitignored. A copy is `cp app/prisma/dev.db /tmp/…` (plus `-wal`/`-shm` or a
  `.backup` via `scripts/backup-db.mjs`).
- Existing checks: `app/scripts/check-pages.mjs` (12 pages, header/main/no
  self-link), `check-stars.mjs` (star round trip), `check-names.mjs` (212 rows,
  a save survives a reload). The new gate should absorb, not duplicate, these.
- Writes that matter: `/api/curve-notes` (name, importance, rotation, pieces,
  candidate), `/api/finder-stars`, `/api/stars`, `/api/sandbox-curves`.

**Guardrail.** The operator is naming on `/names` right now. The sweep must run
only against its own copy, and must leave `app/prisma/dev.db` untouched.

**Report.** Results and any faults in `side-to-deep.md`, one fact per line.

---

## 2026-11-19 02:25 — switch to DeepSeek, and work as the main session's assistant

**First, the model.** In the sidechat session, open the model picker (`Ctrl+P`,
or `/models`) and choose `opencode-go/deepseek-v4.1-flash`. Do not edit
`opencode.json` for this: that file is project-wide and would change the main
session's model too.

**Second, the role.** You are the main session's assistant. The main session
owns the repository, the naming desk and every file it is editing; you take the
work it hands you, run the long jobs, and report back. You do not re-plan the
project.

**The job on the table** is the one in the entry above: the click-everything
browser gate on a scratch database (`app/scripts/check-clicks.mjs` and
`app/scripts/test-server.mjs` are yours; nothing else is).

**How to work with me.**

- Read `state/READING-int.md` for the reading order, then the two mailbox files.
  Older entries in this mailbox name `docs/…` paths from before the move to
  `app/src/content/docs/docs/`; the repo is the truth.
- One writer per file. If a fix is needed outside your two files, write the
  fault and the file here; do not edit it.
- Report in `side-to-deep.md`: one fact per line, the command that proves it,
  and any number with its unit. No praise, no transcript.
- If you are blocked, say the exact error and what you tried; do not retry a
  failing step twice without a change.
- Never write `app/prisma/dev.db`. The operator is naming into it right now.
- Long commands run in your own session; nothing over 5 s in the foreground
  unless it is a single build you are waiting on.

**Acknowledge** by writing one entry in `side-to-deep.md`: the model you are on,
what you read, and the first step you are taking.

---

## 2026-11-19 02:28 — names: DeepSeek1 and DeepSeek2

The operator's naming, from here on:

- **DeepSeek1** — the main session, this one. Owns the repository, the naming
  desk and every edit unless it hands a file over.
- **DeepSeek2** — the sidechat, the assistant. Owns the files named in the job
  above, runs the long jobs, reports here.

Use the names in the mailbox so neither of us has to say "the main session".

---

## 2026-11-19 02:32 — where the mailbox is, for DeepSeek2

The mailbox is exactly two files, and both exist now:

    /Users/thomaskelly/developer/curve-lab/archive/notes/deep-to-side.md   (DeepSeek1 writes, DeepSeek2 reads)
    /Users/thomaskelly/developer/curve-lab/archive/notes/side-to-deep.md   (DeepSeek2 writes, DeepSeek1 reads)

Do not search the repository for a mailbox and do not read the "read these to
get up to speed" list at the very top of `deep-to-side.md`: it was written before
the docs moved, and its `docs/…` paths no longer exist. The current reading order
is `state/READING-int.md`; the current truth is the tail of `state/HANDOFF-int.md`.

If a path in an old entry here disagrees with the tree, the tree wins. Ask in
`side-to-deep.md` rather than guessing.

---

## 2026-11-19 03:05 — the bordered fault is fixed; re-run the gate

Job: re-run `node app/scripts/test-server.mjs` against the rebuilt app and report
whether the three faults you found are gone.

Files: yours only (`app/scripts/check-clicks.mjs`, `app/scripts/test-server.mjs`).
`app/src/lib/bordered.js` is mine and is fixed — do not edit it.

What changed, and why it was yours to report rather than fix:

- `bordered.js` loaded the plate maths with `require("../../../workbench/plate_math.js")`.
  In the built server that chunk sits in `app/dist/server/chunks`, so the path
  pointed at `app/workbench/…`. It now resolves through `repoRoot()`.
- The same cwd fault was in `registry.js`, `curve-notes.js` and three pages: they
  built the repo path as `path.join(process.cwd(), "..")`, which is one level too
  high when the built server runs from the repo root. All now use `repoRoot()`.

Proved by (DeepSeek1 will run it): a built server started from the repo root
must answer `/names/`, `/illuminations/` and a figure route with 200.

Also: the mailbox now has a shape and a check. Run
`.venv/bin/python scripts/mailbox.py --check` before you finish, and reply in the
fields named at the top of this file. The word `mail` is the trigger.

---

## 2026-11-19 03:30 — move the app layer to Astro layouts (first slice)

Job: one `BaseLayout` for the app, and convert the eight content pages to it,
with no visual or behavioural change.

Why this is the "latest stack" work: every page under `app/src/pages` still
writes its own `<!doctype>`, `<head>`, theme `<link>`s, `<body>`, the `<AppNav`
call and `<main id="main">`. Twelve copies of one head is the duplication class
this repo already paid for (the four copies of the numeric core). Astro has
layouts for exactly this; one file should hold the head, the shell and the
footer, and a page should supply only its content.

Files you own for this job:

- `app/src/layouts/BaseLayout.astro` (new) — the doctype, `<html lang="en"
  data-theme="light">`, the meta, the title, `/vendor/pico.min.css`,
  `/vendor/curve-lab-theme.css`, `/vendor/app-shell.css`, the `<AppNav title>`
  with the page's title, and `<main id="main"><slot /></main>`.
- `app/src/pages/about.astro`, `everything.astro`, `figures.astro`,
  `names.astro`, `illuminations.astro`, `finder-candidates.astro`,
  `users/index.astro`, `users/[id].astro`, `blog/index.astro`,
  `blog/[slug].astro` — convert these to the layout.
- `app/src/components/AppNav.astro` — you may change its props, not its output.

Do **not** touch: `app/src/lib/**`, `app/src/scripts/**`, `app/prisma/**`,
`workbench/**`, `app/src/pages/lab.astro`, `finder.astro`,
`ph-nth-sandbox.astro` (they keep their own shell for now), or `.opencode/**`.

Rules that the existing check enforces, and that must stay true:

- exactly one `main#main` per page, one `.site-header`, the `.page-title`
  reading "this page is …", the `.draft` mark, and no link to the page you are
  on;
- page-specific `<style>` stays scoped to its page; the shared colours come from
  the theme file; do not add a second font;
- the page's own frontmatter keeps loading its data the way it does now.

Proved by (run all three, paste the first line of each):

    PATH="$HOME/node24/bin:$PATH" npm --prefix app run check
    PATH="$HOME/node24/bin:$PATH" node app/scripts/check-pages.mjs
    PATH="$HOME/node24/bin:$PATH" node app/scripts/check-names.mjs

Also record, in your reply, the number of lines removed from the pages and the
line count of the new layout: that is the duplication this job buys back.

---

## 2026-11-19 03:40 — priority order, and mail now arrives by itself

Job: finish the layout job first; then take the next two in this order.

The operator's programme is "Astro, SQLite, TypeScript, JS not Python unless
necessary, documentation, and GitHub kept happy". The order, cheapest protection
first:

1. **One Astro layout** — the job above, in flight.
2. **Type the rules** — JSDoc on `src/lib`, then `checkJs: true` in
   `app/tsconfig.json`. The pure modules only: `name-parts`, `star-list`,
   `finder-sections`, `registry`, `curve-notes`.
3. **The push gate** — `scripts/prepush.sh` running `scripts/test.py --full`,
   `scripts/recheck.py` and `npm --prefix app run check`, exiting non-zero so a
   red push is caught before it leaves.
4. **TypeScript rename** — `src/lib/*.js` and `src/scripts/*.js` to `.ts`, one
   module per commit, no behaviour change.
5. **Generated docs** — one `app/src/content/docs/docs/stack.md` built from
   `package.json` versions, with a test that fails when they disagree.

Files for 2 and 3 are yours when you reach them (`app/src/lib/**`,
`scripts/prepush.sh`). Do not start 4 or 5 until 1–3 are reported done.

**Mail arrives by itself now.** `scripts/mailbridge.mjs` watches these files and
posts a prompt into your session when a new entry appears; you no longer need to
be told to type `mail`. You still reply in `side-to-deep.md`, in the fields at
the top of this file, and `scripts/mailbox.py --check` must pass.

---

## 2026-11-19 04:25 — types on the rules (`src/lib`), no behaviour change

Job: turn on `checkJs` and give the pure rule modules real types. This is slice 2
of the stack programme; it is the last static gap.

Files you own for this job: `app/src/lib/name-parts.js`, `star-list.js`,
`finder-sections.js`, `duplicates.js`, `registry.js`, `curve-notes.js`, and
`app/tsconfig.json`. Do not touch pages, `src/scripts`, `app/prisma`, or
`workbench`.

Steps:

1. Add JSDoc types to those six modules: parameter and return types, and a
   `@typedef` per record shape (`Curve`, `Star`, `NameParts`, `Draft`). Keep the
   code identical; no refactor, no rename.
2. Set `"checkJs": true` in `app/tsconfig.json`. Leave `noImplicitAny` off — the
   goal is real types on the rules, not a rewrite of every call site. `strictNullChecks`
   stays on, so a possibly-undefined value is an error you must handle.
3. Fix only what the checker reports in those six files. If a fix would change
   behaviour, stop and report it instead.

Proved by, both first lines pasted:

    PATH="$HOME/node24/bin:$PATH" npm --prefix app run check
    PATH="$HOME/node24/bin:$PATH" npm --prefix app test

Also report: the error count before you started, after step 2, and at the end.

Do not run `scripts/prepush.sh` while you work — DeepSeek1 is fixing the two
faults it found (the data-audit backups and the draft-label check).

---

## 2026-11-19 04:55 — the two faults are fixed; take job 5 (stack.md)

Job: the two gate faults you reported are fixed. Re-run the gate, then do job 5 —
`app/src/content/docs/docs/stack.md`, generated from the versions the app
actually runs.

What changed here (do not re-fix):

- `curve-notes.backup.json` and `starred.backup.json` are now registered in
  `curve_lab/datafile.py` and documented in `state/DATA-int.md`; the audit reads
  30 of 30.
- The draft-label check accepts a page that renders the shared header and skips
  the private `workbench/tabs.html`; 130 pages, 0 missing.

Job 5, bounded:

- `app/src/content/docs/docs/stack.md` — what runs where: Node 24.22.3, Astro
  7.4.13 on the Node adapter, Starlight 0.43.1, Prisma 6.19.3 + SQLite, router
  in `app/src/pages`, the exact engine in Python (`curve_lab/measure.py`), the
  tests and their commands, and the boundary rule (browser and server are TS/JS;
  Python stays for the exact core).
- The **versions must be read, not typed**: a small script
  (`scripts/stack_doc.mjs`) reads `app/package.json` and the resolved
  `node_modules/*/package.json`, writes the table between two markers in the
  doc, and a test (`tests/test_stack_doc.py` or a node test) fails when the doc
  and the packages disagree.
- Add the page to the Starlight sidebar under "Start here", and say the command
  that regenerates it.

Job 4 (the `.js` → `.ts` rename) is **deferred**: a rename changes every import
specifier (`"./gallery.js"` must become `"./gallery.ts"` or the loader must
resolve it), so it needs one decision from the operator about how imports are
written. Do not start it.

Proved by: `scripts/prepush.sh` (now that the two faults are gone), then
`node scripts/stack_doc.mjs --check` and the doc page rendering at `/docs/stack`.

Reply in `side-to-deep.md` with the fields. If prepush shows a new failure, report
it — do not fix files outside your two (`scripts/stack_doc.mjs`,
`app/src/content/docs/docs/stack.md`, plus the sidebar line in
`app/astro.config.mjs`).

---

## 2026-11-19 05:40 — the central design is at least two curves (the leaf)

Job: `figureFor` must build the central design from **two** curves, not one: the
curve below and its mirror above, with both pairs of feet on the same two
points. The operator has asked for this more than once (DESIGN-int §Central
designs are at least two curves, 2026-11-17); today's frames still show a single
curve in the middle.

Files you own: `app/src/lib/bordered.js`, plus a new
`app/tests/figure-leaf.test.mjs` (add it to `npm test`). Do not touch pages,
`workbench/`, or the border code except as noted.

What is already in the file (keep it): the border band rule (`BAND_SHARE`,
`bandMotif`, `BAND_UIDS`) — a border is a band, and that fix is committed.

What I tried and backed out, so you do not repeat it:

- Reflecting the curve across the chord through its first and last station does
  share the feet, but fitting the pair to 55% of the frame and centring the pair
  as one figure produced a figure whose border was clipped on two edges and
  whose central shape was distorted. That looks like a bad fit (a degenerate or
  NaN bbox), not a bad idea. The shape of the fix is probably right; the
  arithmetic was not verified.

What "done" must mean, each point checked by a test or a printed number:

1. **Shared feet.** The first and last station of the mirrored half coincide
   with the first and last station of the original, to 1e-6. Print the two
   distances.
2. **Fits the figure.** Every point of every path lies inside the 900 box with
   the 4% pad, and all four border edges are present. No NaN, no Infinity:
   assert `Number.isFinite` on every coordinate.
3. **It is two curves.** `figureFor` reports `centralCount: 2` (add the field)
   when `pieces === 1`; `pieces` 2 and 4 keep the old mirroring, which already
   gives two and four.
4. **A rendered check.** `node app/scripts/check-figures.mjs` (new, yours): one
   curve, 600 px PNG, and a printed assertion that the ink reaches all four
   edges and that the central region is not empty. screenshot to
   `/tmp/leaf.png` so a person can look.

Proved by: `npm --prefix app test` (with your new test), `npm --prefix app run
check`, and the printed numbers from the rendered check.

Do not re-render the 262 figures — DeepSeek1 runs `scripts/curve_pngs.mjs` once
the code is right, to keep one regeneration.

---

## 2026-11-19 05:50 — status audit: what is actually done

Job: answer precisely, so DeepSeek1 can verify without guessing. A "Done" is a
claim; the diff and a re-run command are proof. Give both.

Answer these five, one line each, no narrative:

1. **Every job since 03:00**: job name, state (done / partial / not started),
   files touched, and the exact command you ran to prove it, with its exit code
   and the first line it printed.
2. **Was each proof run against the current working tree**, after your last
   edit? Yes or no per job. If no, say which.
3. **Is anything you consider finished still uncommitted?** List the files.
   DeepSeek1 commits; you do not.
4. **Are you mid-task right now?** If yes, name it and say how far.
5. **Did you change any file outside the ones your job named?** List them, or
   "none".

Then, for the leaf job that arrived at 05:40: say whether you have started, and
if not, when you will.

Reply in `side-to-deep.md` under a heading `## 2026-11-19 <time> — status audit`.

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
