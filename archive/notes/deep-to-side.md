# deep → side

> **draft A** — a working draft, not a final text.
**Read these to get up to speed**, in this order (all paths from the repository root):

1. `docs/deep-to-side.md` — this file: what changed, what not to trust.
2. `docs/STRUCTURE.md` — where every folder is, and the files that matter.
3. `state/DATA-int.md` — every dataset, its format, who writes and reads it.
4. `state/RESPONSIBILITIES-int.md` — who owns what, and the rule that overlap
   is allowed: do not refuse a job because a file looks busy.
5. `workbench/finder.json` — the curve finder's current results (read, do not edit).
6. `docs/CURVATURE-POWER-CURVES.md` — the power-curve numbers, all computed by
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

---

## 2026-11-19 13:40 — rename: no "imaginary" in code or prose

The operator dislikes "imaginary number" and "imaginary transform"; the numbers
are not hypothetical and the word is a historical accident. The naming decision
is in `state/DESIGN-int.md` §Naming. **Do not use "Euler transform"** — it is a
series transform in combinatorics and Euler angles are a different convention.

The mapping to apply, in your paths only:

| old | new |
|---|---|
| "imaginary number", "imaginary part" | "complex number", "quadrature component" |
| "imaginary transform", "multiply by i" | "Gaussian rotation", or "quarter turn" for 90° |
| "the imaginary variable: z = b i" | "the quarter-turn variable: z = b i" |
| "imaginary component" (in a sum A + iB) | "the rotated component (a quarter turn of B)" |

Where the word appears, check the sense first: `scripts/ph_nth_panels.js`,
`scripts/ph_quintic_gallery.py` and `scripts/direction_curves.py` may use it in an
older, unrelated sense. Rename only where it means the rotation.

Files known to carry it: `app/src/pages/sandbox.astro`,
`scripts/sandbox_curves.py`, `scripts/sandbox_parametric.py`,
`scripts/adder_roots.py`, and the state files (those are DeepSeek1's; leave them).

Prove it: `grep -rn "imaginary" app/src scripts --include=*.js --include=*.py
--include=*.astro` returns nothing in the files you changed, and `prepush.sh` is
green. Then commit and push, with the DESIGN entry included.

---

## 2026-11-19 14:20 — commit the prime-mover diagram, and finish the rename

Two things in your queue.

**1. Commit the sandbox upgrade** (DeepSeek1's edits, your commit):

- `app/package.json` + `package-lock.json`: **d3** added — the operator asked for
  "the usual suspects", so the diagram uses `d3.zoom`, `d3.scaleLinear` and
  `d3.curveCatmullRom` rather than hand-written SVG.
- `app/src/scripts/prime-mover.js` (new): two panels — both walks plus the
  lagged sum, and a separated view (positive above the axis, negative mirrored
  below). Controls: factor (2+i, 3+2i, 3+4i, 5+2i), steps 3–10, PM2 lag 0–3.
  Dot radius follows the nearest-neighbour distance; labels only at the first
  stations; zoom on wheel/drag.
- `app/src/pages/sandbox.astro`: the diagram at the top, the builder box under
  it, and the intro line corrected.

**2. The rename you were sent at 13:40 is still open.** `sandbox.astro` still
carries six occurrences of the banned word; the mapping and the proof are in that
entry. Do the rename and this commit together, so the page ships clean.

Gate first, then commit, push and report the hash as usual.

---

## 2026-11-19 15:05 — include the senior-dev pass in your next commit

`TODO.md` now has a section, **Senior-dev pass — the measures and the claims**,
that belongs with your next commit (no code change needed for the commit itself):

1. calibrate the crossing counters against three pinned numbers (`c-0262` = 9,
   `c-0070` = 11, Chebyshev `T3 x T5` = 4) and rebadge or delete the counters
   that disagree — tonight the same curve read 9, 4 and 1;
2. a smoke test per generator, one known number each;
3. one audit pass over the word "exact" against `DESIGN-int` §Trigonometry;
4. a `--check` (dry-run) mode for every script that writes — two page breakages
   tonight came from scripts writing without one;
5. finish the C/D corner rule (the motifs still cross at the corners).

The first item is the one that matters: nothing measured is trustworthy until the
counter is pinned.

## Handover, 2026-11-19 — the prime mover page, please commit and push

The operator asked for this to go to you now. One page and its supporting files:

- `app/src/pages/prime-mover.astro` (rewritten: the walk, the hit points, the curves,
  the spirograph; `/stage-two/` is now a redirect into it)
- `app/src/scripts/prime-mover-driver.js` (the walker, `unitWalk`, `quadrantPoints`,
  `fineWalk`, `toFloat`), `hit-points-chart.js`, `spirograph-curves.js`,
  `stage-two-curves.js`, `linkage-curves.js`, `integer-spirograph.js`
- `app/public/vendor/jsxgraph/` (the geometry library, served locally; MIT)
- `app/public/vendor/app-shell.css` (header, margin, overflow) and
  `app/src/layouts/BaseLayout.astro` (stylesheet versions by mtime)
- `app/scripts/check-prime-mover-page.mjs`, `check-layout.mjs` (both in `test:pages`)
- `state/`: `SPEC-prime-mover-int.md`, `PROBLEMS-prime-mover-int.md`,
  `SPEC-stage-two-int.md` (marked merged), `PROBLEMS-stage-two-int.md`,
  `SPEC-css-int.md`, `PROBLEMS-css-int.md`, `NOTES-prime-mover-gaussian.md`,
  `GEOMETRY-int.md`, `EXACT-NUMBERS-int.md`
- `AGENTS.md`, `LTMemory-int.md`, `state/README.md` (rules added today)
- `scripts/`: `walk_curves.py`, `spirograph_walk.py`, `circle_grid_walk.py`,
  `grid625_demo.py`, `flip_demo.py`, `prime_loop.py`, `pm4_search.py`,
  `pm_deep_search.py`, `pm_product_probe.py`, `spec_page.py`,
  `check_no_imaginaries.py`

**Known state, so you are not surprised:**

- `node app/scripts/check-prime-mover-page.mjs` and `check-layout.mjs` pass;
  `scripts/check_no_imaginaries.py` passes; `npm --prefix app run check` has
  **0 errors, 9 warnings**, all unused variables (`SEAM`, `OUTER`, `INNER`, `MARK`,
  `bigGcd`, `base`, `grid`, `polynomialFromRoots`, `currentTriple`) — mine to clean,
  not a blocker.
- `app/dist/client/vendor/*.css` was stale and has been copied over by hand; a build
  regenerates it.
- Two figures on the page are still rough: the linkage frame, and the integer
  spirograph (module written, not yet on the page).
- No deploy, no force-push.

Commit message suggestion: `The prime mover: one walk, exact fractions, and a guard
for the big ones`.

---

## 2026-11-20 08:30 — export the sandbox rows, and make every hidden table readable as JSON

Job: three related gaps the operator named. (1) The 5-minute sync pushes
`curve-notes.json`, the star files and `operator-list.json`, but **not** `SandboxCurve`
rows, so every hybrid-desk decision (keep / later / reject, 343 candidates, `/hybrids/`)
lives only in `app/prisma/dev.db`. Export them and add the export to
`scripts/sync-data.sh`. (2) Anything hidden in the database must have a JSON copy with a
written explanation, so a session with no DB can understand the data. (3) Every curve
needs a canonical, searchable formula string, so an outside search can find the curve.

Done means:
- `workbench/sandbox-curves.json` exists, written by `scripts/export-sandbox.mjs` (or by
  the save path), with a header that says what each field means; it is in the sync's
  `git add` list and in `state/DATA-int.md`.
- `state/DATA-int.md` (or a new `workbench/DATA-DICTIONARY.md`) gives, for every table and
  every JSON file: what it is, field, type, meaning, unit, who writes it, what reads it,
  and what is lost if it is missing. Plain English; an AI must be able to rebuild the
  picture from it without opening SQLite.
- every registry record carries
  `formula: { plain, rational, parameter }`, for example
  plain `x = cos^5(t), y = sin^3(t)`,
  rational `x = ((1 - t^2)/(1 + t^2))^5, y = (2t/(1 + t^2))^3`,
  parameter `t rational; t = u/(1 - |u|), u = i/100 for the stations`.
  The exports carry the same object, so the name and the formula travel together.
- a test fails when an export is stale, the same pattern as `check-db`.

Proved by: `node app/scripts/check-db.mjs`, the new staleness test, and the export diff.
Blocked: pushing needs the operator's yes; do not push on your own.
Next: waiting for the other session.

---

## 2026-11-20 09:00 — addendum: the JSON is a visible record, not an export

The operator's words: "sqlite is the source of truth, but we need a visible source of
truth in organised json files." So the JSON is not a convenience dump; it is the same
record, readable without the database.

Layout (one file per table, one object per row, no nesting tricks):

    data/README.md            the data dictionary: every file, every field, meaning, unit,
                              who writes it, what reads it, what is lost without it
    data/schema.json          field -> type for every file, machine-readable
    data/curves.json          Curve + its Note + its CurveSet, one object per curve
    data/stars.json           Star
    data/plate-stars.json     PlateStar
    data/users.json           User (local only; never pushed)
    data/sandbox-curves.json  SandboxCurve — the hybrid desk's decisions
    data/metrics.json         CurveMetric
    data/jobs.json            Session + Job
    data/messages.json        Message

Rules:
- written by one exporter (`scripts/export-data.mjs`) on every save and by the 5-minute
  sync; the sync stages `data/` as well as the existing files;
- a save that cannot write its JSON is reported, never silent;
- a test compares row counts (and a hash per file) and fails when a file is stale, the
  same way `check-db` fails on a count mismatch;
- every record carries `formula: { plain, rational, parameter, use, search }`, so the name
  and the formula travel together and an outside search can find the curve;
- `data/README.md` is written in plain English and names what is deliberately not here
  (`app/prisma/dev.db`, `app/data/users.json`).

---

## 2026-11-20 19:10 — a line between conversations

Job: in the side chat, separate every conversation with a horizontal rule (Markdown `---` on
its own line); if your renderer cannot draw one, print 40 hyphens instead. One line, nothing
else on it. Also written into your prompt (`~/.config/opencode/agents/sidechat.md`), so it
holds for every session, not just when you read this.

---

## 2026-11-20 20:00 — try extreme PNG compression on the plate set

Job: the 397 print plates in `app/public/plates-web/` are 1600 px **grey** PNGs, about 19 MB
in total at ~48 KB each. Find out how much smaller they can be and report the numbers; do not
replace the set until the operator picks a quality.

Try, in this order, and say what each cost in bytes and time:
1. `oxipng -o max --strip all` (lossless re-compression);
2. `zopflipng -m` (lossless, slower);
3. `pngquant --quality 70-95 --speed 1` (lossy palette, 8 colours is plenty: the art is two
   greys, black and white with antialiasing);
4. `optipng -o7` as a fallback.

Install nothing that needs a paid service. Homebrew is fine if it is already on the machine and
the operator says yes; if not, say which tools are missing and stop there.

Done means: a table of sizes for ten representative plates (one per shape family), the
smallest setting that keeps the antialiasing clean, and a recommendation. Write it to
`state/PNG-COMPRESSION-int.md` and reply here.

---

## 2026-11-20 20:40 — correction: no Homebrew installs

The operator's rule, now in `AGENTS.md`: **no brew installs on this machine.** Its Xcode is
older than the bottles expect, so brew builds from source — installing oxipng pulled a 30–60
minute LLVM + rust build and delivered nothing. Use a vendor's prebuilt binary (GitHub
releases), a pip wheel that ships the binary, or report the tool as missing and stop. Brew
*reads* are fine. The PNG-compression job stands otherwise.

---

## 2026-11-26 — the Inkscape quintic extension (the operator's workflow, reassigned to DeepSeek2)

Job: build the Inkscape extension the operator specified, as an installable `.inx` + `.py` pair,
then make 100 six-point guide curves to test it on. The operator's own definition of the
problem, 2026-11-26:

> "We will take a curve in inkscape that has been drawn then we will find six points on it.
> From those six points we will calculate where the quintic bezier should fall. From there
> we'll have to create something that inkscape can work with to display."

What it must do:
- Take the selected outer guide curve. If it has **6 nodes**, read their positions; otherwise
  sample 6 points at s = 0, 0.2, 0.4, 0.6, 0.8, 1.0 along the path by arc length.
- One scalar, **Fullness α**: endpoints fixed (`P0 = G0`, `P5 = G5`), chord points
  `Li = (1 − i/5)P0 + (i/5)P5`, then `Pi = (1 − α)Li + αGi` for i = 1..4.
- Evaluate the quintic Bernstein form, then render it as a **cubic** chain, because SVG has no
  degree-5 primitive. Report the measured deviation in the SVG (a `data-` attribute), do not
  claim sub-pixel without the number.
- A **Live Preview** checkbox (`<effect needs-live-preview="true">`), so dragging the slider
  updates the inner curve; Apply commits it as a normal path and leaves the guide intact.
- Export the raw `P0..P5` at the same time, three ways: a sidecar `.json`, a Blender snippet
  (clamped NURBS, `order_u = 6`, `use_endpoint_u = True`), and GeoGebra Input-Bar commands.
- Then 100 guide curves with exactly six nodes, as one SVG sheet, with a fixed seed so the set
  is reproducible, so the operator can test by opening one file.

Constraints here: no Homebrew installs; Inkscape is **1.4.4** and its bundled Python is the one
that must import `inkex` (the system Python does not). Extensions live in
`~/Library/Application Support/org.inkscape.Inkscape/config/extensions/` on this machine — the
folder does not exist yet. Repository rule: new code is TypeScript, but an Inkscape extension is
Python by the host's own API, so Python is correct here and `state/PORT-int.md` should say so.

DeepSeek1 has not started this work: no `.inx`, no `.py`, no guide sheet exists.

Proved by: pending — `inkscape --version` 1.4.4, and `inkex` import checked against the bundled
Python (it failed on the system Python, which is the trap this job must avoid).

**Correction, same minute — this is not a new assignment.** `inkscape/quintic_math.py`,
`inkscape/quintic_guide.py` and `inkscape/quintic-guide.inx` appeared at 23:30–23:31 while this
note was being written, so DeepSeek2 is already building it. The entry above is kept for the
operator's words and the constraints; it is not work to hand out twice.

Two things worth having:
- **`inkscape/` already holds a round-trip set from 2026-11-22** — `ph_extension.py`,
  `ph_handles.py`, `ph_svg.py`, `ph_actions.py`, `ph_variant.py`, `curve-lab-send.inx`,
  `curve-lab-receive.inx`. Extend those conventions (they already talk to this repo) instead of
  starting a second dialect beside them.
- **The two next actions do not collide.** `next-fhandoff-int.md` (the port close-out on
  `root_search` / `coupler_curves`) is DeepSeek1's and touches `scripts/` + `state/PORT-int.md`.
  Your Blender quintic exporter and the Inkscape extension touch `inkscape/` and the app's
  reduction code. Neither is blocked by the other; both can be live. Do not wait on a choice.
