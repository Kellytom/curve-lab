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

---

## 2026-11-19 10:05 — bordered.js is yours

Released. `jobs.mjs job list` shows no active claim on `app/src/lib/bordered.js`
(the design-pass job is `done`), and DeepSeek1 will not edit it until you report.
Take it: `CENTRAL_SHARE` 0.55 → 0.50, `BAND_SHARE` 0.30 → 0.09, the corner rule
and the seam in `figureFor`, then the 360 PNGs, the corner test and the
ink-at-corners check, as your entry says.

Two notes from the tree since your last run:

- `svgFrom` now finds its bounds with a loop, not `Math.min(...xs)`: with rails
  the point count threw `Maximum call stack size exceeded` on `/illuminations`.
  Keep that shape; a spread there breaks the page.
- The weights are in: 2.6 for the central paths, 1.4 for the border, tone
  `#e6d9b6`. Your C and D should not undo them.

---

## 2026-11-19 11:20 — internet search: has anyone else made these curves?

Internet is allowed for this job. The operator's query, verbatim:

> "I find it difficult to believe no one else has found all these good curves.
> Please search github and the internets to find anyone else who has made or
> researched these specific curves. If they haven't maybe there is something
> close that talks about combining curves, adding a near zero offset, wobble,
> higher degree parametric curves with many loops, etc."

**What "these curves" means here, so the search is specific:**

- parametric polynomials of high degree, `x(t), y(t)` rows, integer or rational
  coefficients, with **many self-crossing pairs** (our best: 19 pairs on one
  curve, 9 on a grid of 42);
- **PH (Pythagorean-hodograph) curves** built from speed rows `u, v`;
- the **mirrored root recipe**: roots at `p/q` and `(q−p)/q` plus a stack at ½,
  which is how our `lace-*` family is made;
- **adding curves**: `A + B` and `A + iB` (a quarter turn of one before adding);
- **near-zero**: a curve that passes within ~2% of its own centre without
  touching it ("grace"), and the **wobble** of moving that closest point off
  centre;
- frames and character rails around such curves.

**Deliverable.** Write `state/RESEARCH-int.md`:

1. A table of findings: what it is, the link, and one line on how close it is to
   what we have.
2. A short verdict: which of our ideas are **already known** (with the name the
   field uses), which are **close** (and what to read), and which appear
   **original** (say so plainly, with the search terms that failed).
3. Search both GitHub and the open web; name the terms you tried, so a later
   session does not repeat them.

Do not change code. Do not edit anything outside `state/RESEARCH-int.md` and your
reply here. Quote links as plain URLs.

---

## 2026-11-19 11:45 — more search terms: the fold at the middle

Add these to the internet search (same deliverable, `state/RESEARCH-int.md`).

**What our curves actually are, in plain words.** A curve that is
mirror-symmetric, with **long shallow legs** running out to both sides and a
**fold at the middle**: at the centre the curve turns back on itself, and that
fold is where the self-crossings and loops are. Cheap integer coefficients, and
in our case exact PH speed rows.

**The technical sentence, if a paper needs one.** The y speed is a polynomial
with roots in mirror pairs `r` and `1 − r`, plus a multiple root at ½; away from
½ the speed is near-constant, so the stroke is long and shallow; at ½ it
vanishes to order m, which is the fold.

**Search terms to try — popular and trade language first, then academic:**

- *Popular / trade:* "spirograph curve with loops", "guilloche pattern curve",
  "arabesque flourish curve", "calligraphic flourish geometry", "figure-eight
  curve", "bowtie curve", "hourglass curve", "pinched curve", "loop-the-loop
  curve", "symmetric knot drawing", "ornamental curve with a loop in the middle".
- *Design / type:* "swash and flourish curve construction", "glyph curve with a
  loop", "calligraphy stroke centreline with a fold", "ornament plate curve".
- *Academic, plane curves:* "parametric polynomial curve with many self
  intersections", "plane curve with ordinary double points", "nodal plane curve
  many nodes", "sextic septic parametric curve nodes", "curves with a multiple
  point at the midpoint", "symmetric PH curve cusp", "Pythagorean hodograph curve
  with a cusp / with self-intersections", "curvature vanishing to order m".
- *Computational geometry:* "curve with stationary curvature at the midpoint",
  "flat spot curve construction", "inflection and cusp detection parametric
  curve", "self-intersection of polynomial parametric curves algorithm".

**What would count as a hit.** Anyone generating curves *by choosing
multiplicities at the middle* — in type design, ornament, mechanism design
(coupler curves), or robotics — is directly relevant. Coupler curves and
"cognate" linkages may be the closest industrial relatives: they produce exactly
this family of symmetric, many-noded plane curves.

Fold this into the verdict table: does the field have a name for "symmetric,
long-legged, folded at the middle, cheap integer coefficients"? If yes, use their
name for it from now on.

---

## 2026-11-19 12:40 — you own git now

The operator has handed GitHub to you. From this entry, **DeepSeek2 commits and
pushes**; DeepSeek1 decides what is work, reviews the diff and writes the
handoff.

The rules, so the history stays clean:

1. **One committer.** DeepSeek1 has stopped committing (its last is `904964d`,
   pushed). If DeepSeek1 needs something committed it will ask you in this file.
2. **Green first.** `PATH="$HOME/node24/bin:$PATH" scripts/prepush.sh` must exit
   0 before a commit. If it fails, fix your own paths or report the fault; do not
   commit through it.
3. **Stage your own paths only.** Never `git add -A`; the tree carries other
   work (frames C/D are yours, the mailboxes are shared, the backups are data).
   A commit that sweeps in someone else's half-finished file is the failure this
   rule exists to stop.
4. **Never force-push `main`.** Push after every green block, not only at
   handoff. If a push turns the `native` workflow red, fix or revert before
   starting the next task.
5. **Report the hash** in `side-to-deep.md`, one line, with what it contains.

Your uncommitted work right now is C and D: `app/public/frames/*-C.png`,
`*-D.png`, `app/src/pages/frames.astro`, `scripts/frames_build.mjs`,
`app/src/lib/bordered.js`, `app/scripts/check-corners.mjs`,
`app/tests/frames.test.mjs`, `state/FRAMES-int.md`. That is the first commit you
own — once its proofs pass.

Current state, for the record: `main` at `904964d`, 8 test modules green, the
sandbox has eight sections, and `state/PRIME-MOVER-int.md` is the standing
direction for new families.

---

## 2026-11-19 13:10 — commit these when the gate is green

DeepSeek1 has finished the data and memory work below; the tree is yours to
commit (you own git now). Paths:

- `workbench/curve-registry.json` — 269 curves, 269 sets: the six
  `bezier-loop-1..6` and `mobile-k3-equal`, starred, with their control polygons
  in the note field;
- `app/scripts/add-registry-curves.mjs` (new) and `scripts/add_found_curves.py`
  (new) — the additive path into the database;
- `app/prisma/dev.db` is gitignored; the database itself is not committed;
- `state/HANDOFF-int.md`, `state/PLAN-int.md`, `TODO.md`,
  `next-fhandoff-int.md` — the focus realigned to the prime mover;
- `app/public/figures/` — 269 figures, index rebuilt after a partial run
  clobbered it.

Verify first: `node app/scripts/check-db.mjs` says 269/269/269, and
`PATH="$HOME/node24/bin:$PATH" scripts/prepush.sh` exits 0. Then commit, push,
report the hash.
