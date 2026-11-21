# PROBLEMS — the tuning lab (`/tune/`)

Every fault this page has had, as it showed up, what was actually wrong, and the guard
that keeps it fixed. The clean spec is `SPEC-tune-lab-int.md`.

**Rule:** a fix and its entry land together. If a guard is removed, the entry stays and
says why.

## 1. The page drew nothing and said something confident

**Seen:** the per-curve page (`/tune/c-0001`) showed "No drawable points for this curve at
these values" under a caption that said "the rows are too large for the rail routine;
spine only".

**Wrong:** two faults in one. The page loaded the maths with
`(await import(path)).default`; under Vite that came back `undefined`, so the drawing
code threw on the first call. The `catch` swallowed the error and printed a reason
invented for it — nothing in the code measures row size.

**Fix:** the page uses `createRequire` to load `workbench/plate_math.js` as Node does
(it is CommonJS, outside `app/`, so Vite's interop has no default). The invented message
is gone; the catch falls back to the spine and says so. The live lab serves the same file
at `/api/plate-math`.

**Guard:** `scripts/check-tune-lab.mjs` waits for `#lab-preview svg` and reads the readout;
a blank preview fails it.

## 2. The form started from the registry, not from the saved row

**Seen:** the page showed plus 2 / minus 2 while the plate had been built with 2.5 / 0.1.

**Wrong:** the defaults came from the registry record, which carries no character values.
Opening the page and pressing save would have written 2 / 2 back and silently undone the
tuning.

**Fix:** the page reads `data/sandbox-curves.json` — the same one copy the plate reads —
and starts the controls from that row.

**Guard:** `scripts/check-tune-lab.mjs` and the plate row law in
`tests/js/plate-row.test.mjs` (note → desk row → defaults, in one place).

## 3. A control that did nothing, and no way to see what it did

**Seen:** "make /tune/ a live render so i can see what each variable does" — the page only
redrew on a form post, and only for one curve.

**Wrong:** the lab did not exist; the per-curve page is a save form, not a sandbox.

**Fix:** `/tune/` — curve picker, four values, live redraw, readout in shares of the
curve's size, and a legend that says what each value does, including the flat case.

**Guard:** `scripts/check-tune-lab.mjs`: the SVG changes when `plus` changes, the ratio is
above 1.05 (not parallel), plus 0 / minus 0 reads 1.00×, and a path curve says so.

## 4. The route name carried the file extension

**Seen:** `/api/plate-math.js` → 404, and Astro reported "a `getStaticPaths()` route pattern
was matched".

**Wrong:** an endpoint file `plate-math.js` is the route `/api/plate-math`; the `.js` in the
URL is not part of it.

**Fix:** the script tag loads `/api/plate-math`.

**Guard:** the lab check fails on a blank preview, which is what a wrong script URL gives.

## 5. One save could not hold two versions

**Seen:** "we might have 5 different versions from one spine, and that is good."

**Wrong:** the only write was "save + render". It wrote one row keyed by the uid and replaced
that row's data with just the four values, so a chosen name or a construction was lost; there
was no second row; and a name collision could not happen because there was no name.

**Fix:** `app/src/lib/desk-tune.js`. *Save over this row* merges and keeps every field the
tune does not own; *save as new version* makes a new row on the same `spine`; a name is
slugged into a URL key; a collision is refused, case-insensitively, and names the row that
holds it; a new version may not take a registry uid. The page lists every row on the spine.
The automatic render is gone: the operator asked for desk io instead.

**Guard:** `app/tests/desk-tune.test.mjs` (ten rules, no database), and the desk checks in
`scripts/check-tune-lab.mjs` (a name, both buttons, the version list).

## 6. A rail change that looked local and was not

**Seen:** "the curve looks fine on page refresh but as soon as i touch any control it gets
crushed... so it works, but wrong", then "you cant cheat and use another way to make the
character rails".

**Wrong:** to make width visible, the fold guard was replaced by a per-station pinch cap in
`plate_math.js`. That is a second rail construction. At the same saved number it drew what
the guard used to cut to 1.5 %, so every saved row came out about four times too wide. The
per-curve page's first paint also came from a stale server module, so it looked right until
a control was touched.

**Fix:** `workbench/plate_math.js` was reverted exactly. The character rail is one law, and
the guard still halves the whole width. The live drawing and the desk are the only new work.

**Guard:** none is needed in code because the change was reverted; the rule is written in
`state/DESIGN-int.md` §The desk. A session that wants a smoother rail must bring a reason to
the operator first.
