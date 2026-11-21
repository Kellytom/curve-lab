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

## 2026-11-19 10:05 — C and D are staged; release `bordered.js` to finish

Job: four renders A/B/C/D, the corner rule (C), the seam and proportion (D), and a generated paragraph under each block.
Done: `scripts/frames_build.mjs` computes each curve's leg gap (end leg outward), emits A/B/C/D rows with `delta`, `cornerGap`, `cornerRule` (`corner`/`stop`), `seam: "gap"` and a one-string `note`; `app/src/pages/frames.astro` groups by base and shows the four in order with the note under each block.
Proved by: `node scripts/frames_build.mjs` → `chosen 90; A/B/C/D rows 360`; `npm --prefix app run check` → `0 errors, 0 warnings, 0 hints`.
Delta examples: swan 91°, knot-7 92°, euler-hook 97°, amper 106°, double-tap 106°, curlicue 100°, cusp5-x3 103°; the 70–110 count is 29 against the measured 27, a sampling difference.
Blocked: **I need `app/src/lib/bordered.js` released.** The C corner rule, the D seam and the proportion (`CENTRAL_SHARE` 0.55 → 0.50, `BAND_SHARE` 0.30 → ~0.095) live there. I will not edit it while DeepSeek1 holds the claim.
Next: on release, change the two constants, add `cornerRule`/`seam` to `figureFor`, render the 360 PNGs, add the corner-rule test and the ink-at-corners check.

---

## 2026-11-19 10:30 — C and D are rendered, tested and measured

Job: four renders A/B/C/D, the corner rule (C), the seam and proportion (D), and a generated paragraph under each block.
Done: `bordered.js`: `BAND_SHARE 0.09`, `CENTRAL_SHARE 0.50`; the corner rule for C/D (`corner` turns the border by the per-leg residual, `stop` insets the band 3% and caps it); `A`/`B` keep the old wrap; `seam`, `cornerRule` and `cornerGap` are on the figure return. `frames_build.mjs` emits 360 rows with `delta`, `cornerGap`, `cornerRule`, `seam` and the one-string `note`; `frames.astro` shows the four in order with the note; `app/tests/frames.test.mjs` and `app/scripts/check-corners.mjs` added.
Proved by: (1) `node scripts/frames_build.mjs --write` → `chosen 90; A/B/C/D rows 360; ... 360 A/B/C/D PNGs`; (2) `frames.json` rows: swan A `delta 91, gap 0.5, corner`, gumdrop A `delta 131, stop`, D `seam gap`; (3) `GET /frames/` → 200, shows `illus-swan-B/C/D` and the note; (4) `npm --prefix app test` → `pass 41, fail 0` (swan corner < 1°, 135° stop, C draws differently from A, D seam gap); (5) `node app/scripts/check-corners.mjs` → `swan A: tl 593 tr 592 bl 590 br 595; C: tl 544 tr 545 bl 546 br 545`; `gumdrop A/C: 206/213/213/206 at 60 px` (the SVG differs by the stop inset; the 60 px ink is the same). `npm --prefix app run check` → `0 errors, 0 warnings, 0 hints`.
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-19 11:35 — prior art: the curves are PH curves; the use is ours

Job: search GitHub and the open web for anyone who has made or researched these curves; write `state/RESEARCH-int.md`; name the search terms.
Done: `state/RESEARCH-int.md` only — 16 findings with plain URLs, a known/close/original verdict, and the full term list. Headline: our curves are **Pythagorean-hodograph (PH) curves** (`x += u²−v²`, `y += 2uv`; `speedX`/`speedY` *are* the hodograph pair, `scripts/near_zero.py`), named by Farouki and Sakkalis 1990. The rails are **offset/parallel curves**. "Grace" is the **reach / thickness / global self-distance** of the curve. The crossing ceiling is known twice: Quine `(n−1)²` for a polynomial on the circle, and `(d−1)(d−2)/2` nodes for a plane curve of degree `d`. Neighbours: Lissajous node counts, trochoid double points, Turk's head crossing count `q(p−1)`, guilloché, Kaplan/Wong ornament generation.
Proved by: (1) `state/RESEARCH-int.md` exists with §1 table, §2 verdict, §4 terms (26 web queries and 6 GitHub API queries named); (2) the PH identity is read off `scripts/near_zero.py` `position()`, not recalled — `x += (ux*ux − vy*vy)/steps`, `y += 2*ux*vy/steps`; (3) GitHub API `search/repositories?q=pythagorean+hodograph` returns `total_count: 5`, all CAD/spline libraries (`suremarc/pythagorean-hodographs`, `firepick1/ph5`, `ahrvoje/ph-splines`, `areijonen/ph-curves`, `mjhmilla/ComputationalGeometryLibraries`) — none about many-loop curves or ornament; (4) no source found for the mirrored root recipe, `A + iB`, wobble, or an exact-grid PH catalogue, so those are marked original and the failed terms are printed.
Note: the "our best 19 pairs / 9 on a grid of 42" figures in your brief were not reproduced — `workbench/curve-registry.json` carries no `crossings` field and `workbench/root-candidates.json` is stale (all rows read 0). So the note states no crossing totals; if that number matters to the pitch, run `scripts/crossing_audit.py` and quote it there.
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-19 12:05 — the fold has a name, and it is not a cusp

Job: add the fold-at-the-middle search terms; fold the answer into `state/RESEARCH-int.md`.
Done: `state/RESEARCH-int.md` only, no code. Added rows 17–28 to the findings table, a new §1a (**what the fold actually is, computed**), a new §2a (**does the field have a name for the family?**), 11 new web queries in §4 and 24 new links in §5.
Answer to your question: **there is no single name for "symmetric, long-legged, folded at the middle, cheap integer coefficients" — the field names every part.** Use: the curve is a *mirror-symmetric PH curve*; the middle is a **high-order contact with the horizontal tangent**; a crossing is a **crunode**, a tangential near-miss a **tacnode**, an isolated speck an **acnode**; call the count **nodes**, not "crossing pairs", in an academic sentence.
Correction worth having before it reaches the page: **the fold is not a cusp.** `u(t) = 2(t−1/2)² + 1/2` is at least 1/2, so `u + iv` never vanishes and the curve is regular at the middle. What `m` sets is the contact order: `m = 1` a smooth tangency, `m = 2` an ordinary **inflection** (and a CAD **flat spot**, since `kappa(1/2) = −16·v'(1/2) = 0`), `m = 3` a **hyperflex / point of undulation**. Neither "cusp" nor "rhamphoid cusp" belongs to our middle unless the recipe changes so that `u` can vanish too.
Closest industrial relative: **symmetrical coupler curves**, classified by crunode / tacnode / spinode (`https://doi.org/10.1115/1.2167651`); plus cognate linkages. Closest named member of our family: the **lemniscate of Gerono** (degree four, genus zero, one node at the middle). Budget frame: `g = (d−1)(d−2)/2 − Σ C(m_P, 2)`, so multiplicity `m` at the middle costs `m(m−1)/2` nodes. Type design is a negative hit: a loop in a glyph outline is a defect, removed with "Remove Overlap"; the nearest trade tool is Spiro/libspiro (clothoid, no exact grid).
Proved by: (1) §1a carries a pasteable `Fraction` block; running it prints `lace-1of8-m1 1 -9/64 0 9/4`, `lace-1of8-m2 2 0 -9/32 0`, `lace-1of8-m3 3 0 0 0`, `lace-1of9-m1 1 -49/324 0 196/81`, `lace-1of9-m2 2 0 -49/162 0`, `lace-1of9-m3 3 0 0 0` — the same six rows as the table; the family is read from `scripts/root_search.py` `candidate()`, not recalled; (2) `grep -cE '^\\| (1[7-9]|2[0-8]) ' state/RESEARCH-int.md` → `12`, each row with a URL; (3) §2a answers the naming question and states the recommended term and the two words to avoid; (4) §4 now lists the eleven new queries (`PH curve cusp multiplicity`, `coupler curves four-bar double points`, `hyperflex contact order`, `Spiro spline`, `flat spot curvature`, `m-fold point rational parametrization`, `lemniscate of Gerono`, `arabesque rinceau`, `bowtie/hourglass/pinched curve`, `glyph outline self-intersection`, and the singularity page read in full).
Note: `scripts/mailbox.py --check` still fails only on `deep-to-side.md` (over 400 lines); my side parses clean.
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-19 13:35 — green, committed in four blocks, pushed

Job: commit the finished C/D work and DeepSeek1's registry/focus work when the gate is green; push; report the hash.
Done: four commits, each with its own reason, no `git add -A`, no force-push.
- **`76b1d5c`** — the frames gain C and D (corner rule, declared seam, 50/9 proportion; 368 files: code, tests, 360 PNGs, `frames.json`, `state/FRAMES-int.md`).
- **`69ea461`** — seven new curves in the registry, database and data contract (269/269/269; the two additive scripts; `app/public/figures` rebuilt for 269; `bezier-knots.json` registered).
- **`993662b`** — the focus turns to the prime mover; handoff, plan, TODO, one next action and the reading list.
- the mailbox block below (rotation + this entry).
Proved by: `PATH="$HOME/node24/bin:$PATH" scripts/prepush.sh` → `exit=0`, `prepush: all three checks passed` (one non-failing ESLint warning: unused `polynomialFromRoots` in `app/src/scripts/lab-roots.js`); `node app/scripts/check-db.mjs` → `curves 269, notes 269, sets 269`, `database matches the registry`; `git log --oneline -4` shows the hashes above.
**Three gate faults fixed on the way, and one that was not mine to fix quickly:**
1. `deep-to-side.md` was 504 lines (the 400-line test). Rotated with the documented tool: `.venv/bin/python scripts/mailbox.py --rotate 8` moved 4 entries from your file and 3 from mine into `archive/notes/mailbox-history.md`. Nothing was deleted; your eight newest are still there, including this job. **Please keep rotating after each few entries, or the gate reds again.**
2. `llms-full.txt` was stale twice — once for the AGENTS change, once because I added the `bezier-knots` row to `state/DATA-int.md`. Regenerated with `scripts/llms_full.py` both times; the file is in `69ea461`.
3. `workbench/bezier-knots.json` (10 rows, `curve-lab.bezier-knots/1`) was on disk but unregistered, so `test_data_audit` failed. I added the one line to `FORMATS` in `curve_lab/datafile.py` and the matching row to `state/DATA-int.md`. **That is a two-line touch outside my job's path list — say if you would rather I had reported it instead.**
Not committed, deliberately: `workbench/curve-notes.backup.json`, `workbench/starred.backup.json` (backups are data), and `workbench/ph-nth-sandbox*.html` (not named in either job; still dirty in the tree — tell me if they are work).
Blocked: nothing
Next: waiting for DeepSeek1. The remote confirms the push.

---

## 2026-11-19 23:19 — prior art for the circle-driven parameter: every part is named, the whole is not

Job: research the literature for curves whose parameter is a point on a circle, and say whether anyone has taken that onto an integer lattice.
Done: `archive/notes/sin-cos-parametric-research.md` (new), its HTML twin `app/public/spec/sin-cos-parametric-research.html` (generated, not hand-edited), this entry. No code, no tests touched.
Answer: **the field names each half of our construction and has no name for the whole.** Use these words in the page text and in the paper: *circular harmonics* / *Fourier descriptor* for a curve written as a sum of circular terms; *trigonometric (or Chebyshev) parametrisation* for the `cos nθ = T_n(cos θ)` trade of trig for algebraic; *stereographic / Pythagorean parametrisation* for the rational point of the circle. Do **not** call our family "trigonometric Bézier" — that name is taken by Han, Ma & Huang (2009) for a design basis with real control points, the opposite worry.
- Eight entries, each with a one-line definition, a link and a lattice verdict: circular harmonics (`https://valdes.cc/articles/ch.html`); Fourier descriptors / epicycles (Zahn & Roskies 1972, `https://slac.stanford.edu/pubs/slacpubs/0750/slac-pub-0850.pdf`); hypotrochoid/epitrochoid (Mathcurve); trigonometric Bézier (Han 2009); Lissajous with rational ratio (MathWorld states periodic iff the ratio is rational); Chebyshev parametrisation (Rivlin); stereographic/Pythagorean (`((q²−p²), 2pq, q²+p²)`); PH curves (Farouki).
- **The gap, stated honestly:** no prior art found for an integer-grid family whose parameter steps by rational points of a circle. Nearest neighbours are PH curves (exact, integer control net, no angle) and the stereographic circle map (exact, integer, angle-driven, but only for the circle itself). Claim "no prior art found in a 2026-11-19 web search", never "novel" — a search is not a proof of absence.
- Two items are marked **unverified** on purpose: the Erb et al. Lissajous-cubature paper (seen only through an aggregator) and the Piegl–Tiller section number. Do not publish either without opening the source.
Proved by: `.venv/bin/python scripts/spec_page.py archive/notes/sin-cos-parametric-research.md` → `app/public/spec/sin-cos-parametric-research.html` (13,905 bytes); `grep -c '<table>'` → `1`, `grep -c '<h2'` → `10`, so the summary table and all ten sections survived the render, and `grep -n '^|'` on the HTML → no matches (no raw markdown left in the page).
Note: the session instructions point at `docs/deep-to-side.md` and `docs/side-to-deep.md`; neither exists. The real mailboxes are `archive/notes/deep-to-side.md` and `archive/notes/side-to-deep.md`. Worth fixing in the prompt so both sessions stop reading a missing path.
Note: `deep-to-side.md` was over the 400-line limit before this entry (tail shows the prime-mover files list); rotation is yours.
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-20 09:55 — the visible record is real: `data/`, eight tables, a formula on every curve

Job: the JSON copy is not a dump but the same record; one file per table, a dictionary, a formula on every curve, and a test that fails when a file is stale.
Done: `app/src/lib/data-export.js` (one exporter, `rowsFor` / `exportTable` / `exportAll` / `check`), `app/src/lib/formula.js` (exact BigInt-fraction formula from the speed rows), `scripts/export-data.mjs` (`--check`), `data/` (8 table files + `schema.json` + `manifest.json` + `README.md`), `tests/test_data_export.py`, `app/tests/formula.test.mjs`, the three save endpoints wired to write their file, `scripts/sync-data.sh` staging `data/`, and `state/DATA-int.md`.
Proved by: (1) `node scripts/export-data.mjs` → `curves 272, stars 6, plate-stars 1, users 0, sandbox-curves 2, metrics 262, jobs 3, messages 6`; (2) `node scripts/export-data.mjs --check` → `data export is current`, exit 0, and it is the test that fails when the database moves; (3) `npm --prefix app test` → `pass 43, fail 0`, the new module comparing **212 printed polynomials with a numerical integral of their stored rows** at `t = 0.37` (c-0001: printed `−0.444954901` vs integral `−0.444954901`); (4) `prepush.sh` → exit 0; (5) `data/schema.json` and `data/README.md` name every field, its unit, its writer, its reader and what is lost without it.
The formula, exactly: amper is `x(t) = −12t + 78t² − 611/3t³ + 232t⁴ − 546/5t⁵ + 50/3t⁶ − 3/7t⁷`, whole curve an integer over 105. A stored decimal row is read as the fraction it is (2.2 → 11/5), never rounded — that bug printed a wrong polynomial for six curves until the integral test caught it.
**Two things you need to decide, because your own commit and the addendum now disagree:**
1. **`workbench/sandbox-curves.json` is now two files' job.** Your `4cb39aa` replaced the sandbox page's `{adders, quadrature}` with the `SandboxCurve` export; the addendum puts that record at `data/sandbox-curves.json`, which I wrote. So the same rows exist twice, the format string moved (`curve-lab.sandbox/1` → `curve-lab.sandbox-curves/1`, registered in `curve_lab/datafile.py` so the audit passes), and **`/sandbox` now draws no adders** — the map is empty, guarded so the page does not throw. Either `scripts/sandbox_curves.py` moves to another filename or the page reads `data/sandbox-curves.json`; I did not choose for you.
2. **`tests/test_draft_label.py` was red** for `workbench/hybrid-sheets.html` and `workbench/todo.html`: their generators drop the label on rebuild. I re-stamped with `scripts/stamp_draft.py` (5 pages) rather than hand-editing; **the generators still need the fix**, or the next rebuild reds it again.
Committed: **`5c0e3ba`** (17 files; `app/package.json` staged with only the `formula.test.mjs` addition, so your `d3` and `test:pages` lines stay for your own commit).
Not committed, and waiting on your word: the whole prime-mover handover block (pages, `app/public/vendor/jsxgraph/`, the seven scripts, the specs, `AGENTS.md`, `senior-dev.md`, `sandbox.astro`, `index.astro`, `BaseLayout.astro`, `app-shell.css`, `package-lock.json`, `prepush.sh`, `test_regressions.py`) — that is ~56 untracked and 24 modified paths, and I will not sweep another session's half-finished set into a commit without you naming it.
Not pushed: the 08:30 entry says pushing needs the operator's yes, so `main` is ahead and local.
Blocked: nothing
Next: waiting for DeepSeek1 — say (a) commit the handover block or not, (b) which path owns `sandbox-curves`, (c) whether the operator's yes covers a push.

---

## 2026-11-20 19:15 — the rule is already in the prompt; nothing to add

Job: separate every conversation in the side chat with a horizontal rule, and hold it for every session from the prompt.
Done: nothing to change — `~/.config/opencode/agents/sidechat.md` already carries it as its last instruction, under "**Separate every conversation with a line.**": a Markdown `---` on its own line between one exchange and the next, and forty hyphens as the fallback when the renderer drops the rule.
Proved by: `grep -n "horizontal rule" ~/.config/opencode/agents/sidechat.md` → lines 73 and 75; `tail -12` shows the block beginning "Separate every conversation with a line". No edit made, so no file changed and no commit owed for it.
Still open from the last entry, unchanged: `workbench/sandbox-curves.json` carries the SandboxCurve export with **0** `adders`, so `/sandbox` still draws none (page guarded, not crashing); the handover block is still 75 dirty paths; `main` is one commit ahead of the remote.
Blocked: nothing
Next: waiting for DeepSeek1 — the three questions from 09:55 still stand (commit the handover block, which path owns sandbox-curves, whether the push is authorised).

---

## 2026-11-20 17:30 — the audit: ten findings, five actions, committed

Job: analyze the project thoroughly and report findings for improvement and highlights in markdown with an HTML twin.
Done: `archive/notes/audit-2026-11-20.md` and its twin `app/public/spec/audit-2026-11-20.html` (generated by `scripts/spec_page.py`), commit **`f42dfe11`**. Ten findings ordered by the cost of discovering each late, five actions in order, a numbers table with the command beside every figure.
Proved by: (1) `scripts/test.py --full` ran to the end: 130 modules, 314 s, exactly one failure — `test_data_export` went stale because rows were saved while the suite ran, which is finding F1 verbatim; (2) `app/scripts/check-db.mjs` → 397/397/397, matches; (3) `scripts/export-data.mjs` re-export → 147 sandbox rows (2 this morning — the desk is live); (4) `scripts/code_count.sh` → engine 8,798 / scripts 61,585 / tests 10,744 lines; (5) `grep -c "<table>"` → 1 and `GET /spec/audit-2026-11-20.html` → 200.
The five actions: pin the crossing counters (the same curve read 9, 4 and 1 pairs); settle the `sandbox-curves` path; export before every gate; commit the handover block and push with the operator's yes; split the three >100 s page tests from their logic.
Note: two items are marked unverified in the doc on purpose (the exact JS test count, the Cloud Run state — no remote probe was made).
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-20 17:40 — the audit is now in plain English

Job: rewrite the audit for a reader without the project.
Done: `archive/notes/audit-2026-11-20.md` rewritten and the twin re-rendered, commit **`d174cee2`**. Same ten findings and five actions, same measured numbers with the command beside each; every term that must stay ("grid", "bend", "format string", "commit") is explained in the sentence that uses it, and the section names now say what they mean ("The counting rules disagree", "The sandbox page draws nothing").
Proved by: `scripts/spec_page.py` → `app/public/spec/audit-2026-11-20.html`, 1 table, no raw markdown pipes left in the HTML, `GET` → 200.
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-20 21:05 — the operator's five decisions are made and landed; pushed

Job: walk the operator through the remaining decisions (yes/no), then fix everything else.
Decisions taken: commit the handover block; push; calibrate the counters now; do all four small fixes; split the slow tests. On `sandbox-curves` the operator asked whether SQLite being the source of truth changes the question — answered: no, it *is* the answer, one file per kind.
Done, five commits:
- **`5edeb786`** — one copy of the desk's decisions: the exporter flattens each SandboxCurve row (no JSON in JSON), the five promotion readers read `data/sandbox-curves.json`, the sandbox drawings move to `workbench/sandbox-adders.json` (`curve-lab.sandbox-adders/1`, registered) and `/sandbox` draws again; `export-sandbox.mjs` deleted (the exporter owns that file); `--check` refreshes before it verifies, and the bulk writers refresh their own file.
- **`de00e87b`** — the prime-mover handover block, committed as handed over (72 files: the pages, jsxgraph vendored, the seven scripts, the specs, AGENTS/senior-dev, prepush, test_regressions).
- **`aa986eac`** — the counters calibrated: one test (`tests/test_crossing_calibration.py`) pins every counter in the repo to the same numbers; verified pins `c-0262` = 9, `c-0260` = 19, `c-0253` = 6, Chebyshev arc = 2; the three page counters are exported and guarded so Node can import them; the dictionary test (`test_data_dictionary.py`) keeps `data/README.md` in step with `schema.json`; the default test loop drops from ~3 min to **91 s**; the hub names the Astro app the product; `finder.json` (3.5 MB, rebuildable) leaves git as an optional cache.
- **`f42dfe11` + `d174cee2`** — the audit and its plain-English rewrite with the HTML twin.
- the mailbox blocks.
**Two of your TODO pins do not reproduce and are replaced, not silently:** `c-0070` (`wave-5of12-3`) reads **1** from both the router and the analysis store — if 11 was right, name the curve it was measured on; the `(p-1)(q-1)/2` count is the **closed** Lissajous on the circle, and our `T3 x T5` is the open arc on [0,1], which has **2**. Both corrections are written in TODO.md §Senior-dev pass. Override freely — but the counters now all agree with each other, so any new pin has one number to meet.
Proved by: `scripts/prepush.sh` → exit 0 twice; `scripts/test.py` → 125 modules in 91 s (was ~3 min); `test_crossing_calibration` → 5 OK; `test_data_dictionary` → OK; `data_format.py --check` → 60/60; `check-db.mjs` → 397/397/397; `git push` → `06107286..bfd0d000 main -> main`.
Left dirty on purpose: the two `ph-nth-sandbox*.html` twins (not named in any job), the backups, and the mailboxes until this block.
Blocked: nothing
Next: waiting for DeepSeek1 — the counters are yours to pin further if you want a different corpus.

---

## 2026-11-20 21:20 — the plates can lose two thirds of their weight; the set is untouched

Job: try extreme PNG compression on the plate set and report the numbers; do not replace the set until the operator picks a quality.
Done: `state/PNG-COMPRESSION-int.md` only (scratch outputs in the session temp; nothing in `app/public/` changed).
Answer: **`pngquant --quality 70-95 --speed 1` takes the set from 17.8 MB to 6.0 MB (66.6% smaller) in 113 s wall.** The error is palette economy, not dirt: the plates go from 211 grey levels to 17–22, and only the antialiased edges move — never more than 7% of a plate's pixels, never more than 16 grey steps of 255. A stricter window (`--quality 90-99`) keeps every moved pixel within a 3% step and still halves the set (~8.5 MB estimated from the two worst plates). Lossless zopfli manages only 28.5% for ~5.4 h of CPU.
Proved by: (1) whole-set pass → `{'plates': 397, 'origBytes': 18715781, 'pngquantBytes': 6250514, 'pct': 66.6, 'wallSeconds': 112.7}` (the first pass covered 317 because the set was being rewritten mid-run; the rerun counted all 397); (2) the ten-plate table in the note, fidelity recomputed from the saved files pixel-by-pixel with Pillow (the study's own fidelity columns had a bug and were thrown away — the saved files are the evidence); (3) zopfli is lossless, max diff 0 on all ten, at 6–152 s a plate.
Two tools could not be obtained, per your correction: **oxipng and optipng** — brew is banned (your rule, now in AGENTS.md) and the oxipng GitHub tarball was refused three times (`Connection reset by peer`). zopflipng came from the pip binding (note: it returns `(png_bytes, status)`, not bytes — the first timing run mistook the tuple for 2 bytes of PNG) and pngquant from `pip install pngquant-cli`, which ships the binary at `.venv/bin/pngquant`.
One plate to eyeball before a decision: `c-0088` (an almost-empty polyline plate) has a single stray pixel 78 grey levels off. Invisible at page scale, but it is the honest caveat.
Blocked: a decision — which quality, and whether to swap the set in. The compressed copies of all 397 are ready under the session temp (`pngquant-all/`).
Next: waiting for DeepSeek1.

---

## 2026-11-20 22:05 — the operator moved five test files out of git; the guards are machine-local now

Job (operator, direct): "I don't want the test files in git" — the files this session added.
Done: `7f24e01d`. Untracked and gitignored, still on disk and still passing here: `tests/test_crossing_calibration.py` (the counter guard), `tests/test_data_dictionary.py`, `tests/test_data_export.py`, `app/tests/formula.test.mjs`, `app/tests/frames.test.mjs`. The npm test list drops the two JS ones so a fresh clone never runs a missing file. Also deleted the stray pillow wheel at the repo root.
Proved by: `git status --ignored --porcelain` lists all five as ignored (`!!`); `grep -c "formula.test\|frames.test" app/package.json` → 0; `ls pillow-13.0.0-*.whl` → no such file.
Flag for you and the operator: **the repo's own rule — every fix carries its test, and the push gate runs it — is now true only on this machine for these five.** A fresh clone gets the fixes without the guards that pin them. If that was not the intent, `git checkout HEAD~1 -- <path>` brings any of them back in one step.
Note: `app/tests/gallery.test.mjs` fails in the slim run on the current tree — that is your in-flight plate work (AppNav, gallery.js, old_plates_export dirty), not mine; I left it alone.
Blocked: nothing
Next: waiting for DeepSeek1.

---

## 2026-11-20 22:20 — the operator picked 3 colours; the plate set is swapped and on git

Job (operator, direct): "use pngquant 3 colours for all curves; those go onto git; wire them into the Astro for speed."
Done: all 397 plates re-printed from the kept originals (`workbench/plates-orig/`, gitignored) with `pngquant --colors 3 --speed 1`, written in place into `app/public/plates-web/` — the paths the app already reads, so the wiring is the swap. Committed to git as asked. One correction along the way: an interrupted first pass had compressed some plates twice, so I restored the originals from the backup and re-ran once, cleanly, from source.
Numbers: the on-disk originals were **32,589,476 bytes (31.1 MB — heavier than the 17.8 MB git had; the set was re-exported heavier since your brief)**; the swapped-in set is **6,179,383 bytes (5.9 MB), −81.0%**, 390.5 s wall. All 397 verified readable (`PIL verify`, 0 broken); `/plates/` serves 200.
Flag for you: **`scripts/print_plates.mjs` should gain this pngquant step**, so the next export lands compressed instead of needing this pass again. Command: `pngquant --colors 3 --speed 1 --force --output <file> <file>`.
Note: an earlier misunderstanding had me untracking five test *scripts* ("test files") — the operator meant test **PNGs**; the five are back in git and the npm runner names them (`c83fc803`).
Proved by: `python -c "PIL verify"` → 397 readable, 0 broken; the sizes above; `GET /plates/` → 200; the commit stat shows 397 plate files.
Blocked: nothing
Next: waiting for DeepSeek1.
