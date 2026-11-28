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

---

## 2026-11-26 — Done: the 100 six-point guide curves, for testing the Inkscape extension

Job: the operator asked DeepSeek1 for 100 control curves with six points, to test the Inkscape
quintic workflow on.

Done: `scripts/quintic-guides.ts` writes `workbench/quintic-guides.json` (the exact record) and
`workbench/quintic-guides.svg` (a sheet, `Fig. QG1`, openable in Inkscape). Ten classic families,
ten members each — parabola, bowl, S, C (half a circle), hyperbola, cusp (semicubical parabola),
sine wave, loop, flattened arch, tangent rise. Every coordinate is an integer on a 120 × 120 grid,
y up; the SVG flips y once, when it writes.

Two numbers that matter when you test:
- **Fit error** (a fitted quintic against its classic): worst **0.634** grid units, on the wave.
  Parabola, bowl and the cubic S fit exactly; the C, hyperbola and wave are sampled, so they are
  approximations and say so in their note.
- **Cubic-chain error** at six spans: worst **0.0443** grid units across all 100.

Proved by: `node scripts/quintic-guides.ts` prints 100 curves, the worst chain deviation and the
loop crossings (`1,1,1,1,1,1,1,1,1,1`); the script refuses to write if any curve has other than six
points, a non-integer coordinate, or a "loop" that does not cross.

**Addendum, same job:** the test file is `workbench/quintic-guides-paths.svg` (`Fig. QG2`) — 100
separate paths, each with exactly six nodes, no dots and no drawn curve, so selecting one gives
the extension six nodes and nothing else. The big sheet (`Fig. QG1`) is for looking at; QG2 is for
feeding the tool.

**Extends the same job — 200 curves now, and the ornament canon.** `scripts/quintic-guides.ts`
writes four files: `quintic-guides.svg` (QG1, math classics), `quintic-guides-paths.svg` (QG2, the
same as clean six-node paths), `quintic-guides-ornament.svg` (QG3, ten Roman/Greek/French families)
and `quintic-guides-ornament-paths.svg` (QG4, the clean paths). 200 curves, 20 families, six
integer points each.

The measured limit is the useful part: one polynomial quintic holds one lobe (fit ≤ 0.5 grid units
on cyma, echinus, volute, rocaille) and does not hold multi-lobe forms (2.0–2.4 on trefoil,
arabesque, acanthus). The canon therefore splits into arcs (mouldings, volute, tracery) and single
quintics (scrolls, lobes). Written up with a first step per line in
`state/EXPLORATION-int.md`, "The classical canon".

Proved by: `node scripts/quintic-guides.ts` prints 200 written and the worst chain deviation; the
script refuses a non-integer or non-six-point curve, and a "loop" that does not cross.

---

## 2026-11-27 — the shared data contract, and the split

Job: the operator set the division — DeepSeek2 owns the Inkscape code, DeepSeek1 owns the repo side,
and both work to one data structure.

Done: `format/quintic.schema.json` is **`curve-lab.quintic/1`**, an ordinary JSON Schema both
languages can read. `scripts/quintic-guides.ts` now writes exactly that shape: a curve is
`{uid, group, family, name, closed, winding, fitError, selfCrossings, spans[], joins[]}`; a span is
`{uid, kind:"quintic", points[6], weights:null, frame{start,end}}`.

The four facts you may rely on:
1. `points` are six **integers**, y up. The exact object; anything drawn is an approximation.
2. `frame.start.tangent = P1 − P0` and `frame.end.tangent = P5 − P4`, both **forward**, so a join
   needs no sign flip. `kappa` and `rate` are signed along the same direction.
3. `closed:false` promises nothing about the ends; `closed:true` means the last span ends exactly
   where the first starts.
4. A join carries a **measured residual**. Refuse a G2 claim without one.

`tests/js/quintic-data.test.ts` is the runnable form of the contract — 8 tests, both sides run it.
It already caught a real bug of mine: the end tangent pointed backwards, which would have made every
G1 check fail in your extension.

Ownership is written in `state/RESPONSIBILITIES-int.md` §7. You read the data, you never write it;
a schema change is a format bump and one commit, not an edit.

Proved by: `node --test tests/js/quintic-data.test.ts` → 8 pass, 0 fail; `node
scripts/quintic-guides.ts` → 200 curves written.

---

## 2026-11-27 — three fixtures you can test against, and one thing that will bite you

Job: the operator's split — you take the Inkscape extension, I take the repo side, one shared data
structure. This is what is ready for you to read. Nothing here needs you to change your files.

1. **`workbench/quintic-guides.json`** — 200 curves, the contract shape (`curve-lab.quintic/1`).
2. **`workbench/quintic-fullness.json`** — the α fixture: five guides × α = 0, ¼, ½, ¾, 1, with the
   six points written out. Your extension's output at each α should match these **point for point**.
   If it does not, the disagreement is the bug, and it is worth knowing which side is wrong before
   either of us "fixes" it.
3. **`workbench/quintic-chain.json`** and **`quintic-closed.json`** — span frames and join residuals,
   so you can see what a G3 join looks like as numbers (Δκ 0.00 %, tangent 0.0°).

**The thing that will bite you:** `frame.end.tangent` is `P5 − P4`, pointing **forward** along the
curve, and `kappa` is signed along that same direction. My first version had the end tangent
reversed; the contract test caught it. If your extension compares an end tangent to a start tangent
without that convention, every G1 check will read as a 180° corner.

**The measured limit worth knowing before you judge a shape:** one polynomial quintic holds one lobe
(fit 0.07–0.50 grid units) and fails on multi-lobe forms (2.0–2.4). So a trefoil or a volute will not
look right however the extension draws it — that is the primitive, not your code.

Proved by: `node --test tests/js/quintic-*.test.ts` → 25 pass, 0 fail; `node
scripts/quintic-fullness.ts` writes the fixture.

---

## 2026-11-27 — what is ready for your Inkscape work, and what not to touch

Job: you are on the Inkscape extension and the quintic lab; this note is what is stable on this side,
so you do not spend an hour re-deriving it.

**Stable, test-covered, safe to read**
- `workbench/quintic-guides.json` — 200 curves, contract `curve-lab.quintic/1`.
- `workbench/quintic-fullness.json` — the α fixture: 5 guides × α = 0, ¼, ½, ¾, 1, with the six
  control points written out. Check your output against it point for point.
- `workbench/quintic-chain.json` — four spans placed end to end with the measured joins.
- `workbench/quintic-closed.json` — the closed ring, `closed: true` and a winding.
- `format/quintic.schema.json` — the written contract.
- `scripts/lib/quintic-geometry.ts` — evaluate, split, sub-curve, cubic chain, end frame. Plain
  functions, no I/O. If your lab needs a cubic chain of a quintic, import this rather than writing a
  third copy.
- `tests/js/quintic-*.test.ts` — 25 tests; `tests/test_quintic_contract.py` — 4, the Python side.

**The convention that would otherwise cost you a day:** `frame.end.tangent` is `P5 − P4`, pointing
**forward**, and `kappa` is signed along that direction. My first version had it reversed; the contract
test caught it. A join compared without that convention reads as a 180° corner.

**Do not write these:** `workbench/quintic-guides.json`, `quintic-fullness.json`, `quintic-chain.json`,
`quintic-closed.json` — they are generated. Regenerate, do not patch. A meaning change is a format
bump (`curve-lab.quintic/2`) and both readers in one commit, not an edit.

**Measured limit worth knowing before judging a shape:** one polynomial quintic holds one lobe
(fit 0.07–0.50 grid units on cyma, echinus, volute, rocaille) and fails on multi-lobe forms (2.0–2.4 on
trefoil, arabesque, acanthus). A trefoil that looks wrong is the primitive, not your renderer.

Proved by: `node --test tests/js/quintic-*.test.ts` 25 pass; `node --test tests/test_regressions.ts`
38 pass; `python -m unittest tests.test_quintic_contract` 4 pass.

---

## 2026-11-27 — two bugs in `quinticControls`, measured, with a workaround on this side

Job: chain spans with the solver in `app/src/lib/glue.ts` instead of placing whole shapes, and prove
the joins. It works — three spans, G3 at both joins, station residuals 3e-16 — but only after two
faults in the solver, both measured, neither guessed.

**1. `unitDirection` is not unit for a slope that is not a Pythagorean triple.**

```ts
return { x: x / l2, y: y / l2, exact: false };   // l2 = x*x + y*y
```

Dividing by the **squared** length leaves a vector of length `1/√l2`. Slope `1/1` gives
`(0.5, 0.5)`, length 0.707. The solver's `E0`/`E1` rows use `cross(u, …)`, so the curvature it aims
for arrives scaled: asking for κ = 0.01 produced **0.028284** on both ends (2√2 × too large). With
p-triple slopes — 3/4, 5/12, 20/21 — the exact branch runs and κ lands to 1e-17. The fix is
`x / Math.sqrt(l2)`.

**2. `dkappa1` is taken along the reversed direction, while `kappa1` is forward.**

One span, `dkappa0 = 0.0002`, `dkappa1 = -0.0001`: the measured start rate was **+0.0002** and the
measured end rate **+0.0001** — the end sign inverted. Passing `dkappa1 = -rate` fixes it; the joins
then read Δ(dκ/ds) ~1e-13 instead of 2× the rate.

**Workaround on this side, not a change to your file:** `scripts/quintic-connect.ts` uses p-triple
slopes only and negates `dkappa1`, and says why in its header. `tests/js/quintic-connect.test.ts`
asserts the chain, not the workaround, so both tests keep passing if you fix either.

**What it produces:** `workbench/quintic-connect.json` (stations, spans, joins with residuals) and
`Fig. QN1`. Three spans, each a quintic, G3 at both joins, no self-crossing, drawn as cubic chains.

Proved by: `node scripts/quintic-connect.ts` → both joins G3, worst station residual 3.3e-16;
`node --test tests/js/quintic-connect.test.ts` → 6 pass.
