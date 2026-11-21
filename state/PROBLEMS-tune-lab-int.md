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
