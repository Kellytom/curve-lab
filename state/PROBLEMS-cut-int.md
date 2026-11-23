# PROBLEMS — the cut desk (`/cut/`, `/cut/<uid>`)

Faults, in the operator's words, with what was actually wrong, the fix and the guard. The clean
description is `state/SPEC-cut-int.md`; no fault belongs there.

## 1. "still doesnt have a way to save the cut curves" (2026-11-23, twice, then again)

**What the operator saw.** The button said "cutting…" and nothing else happened. The page was
reloaded by the dev server before the answer arrived, so no banner appeared. Asked at 16:55,
then quoted again at 17:40 with the 16:23 text.

**What was wrong.** The save wrote the record, then **awaited the plate and figure renders in
the request** (up to 180 s each, and the figure retried). The browser sat on a pending POST; the
record existed but the operator had no result. A browser probe: click → no response after 9 s,
status "cutting…", while `c-0274a` was already in the registry.

**Fix.** `createVariant` returns after the database and exports are written; the renders run in
a detached child (`scripts/render_saved_curve.mjs`, log in `state/jobs/render-saved.log`). The
client's banner then survives, carried in the URL.

**Proof.** Click on `/cut/c-0274` → POST 200 → URL `?saved=c-0274a … 5.458 units kept, 3.426
dropped` → banner with links; plate at 11 s, figure at 22 s after the answer.

## 2. A dot cut previewed the line's halves

**What the operator saw.** The form said "at dot 1", the picture below showed the top and bottom
halves cut by the red line. "does not cut at the dotted line. it cuts at 1 and 2 the blue dots,
remember? algorithmically, not looking at the plot and cutting it in half." (2026-11-23)

**What was wrong.** The preview section was hard-wired to `lineRuns(points, "top"|"bottom")`
and never read the form's mode. The cut itself was correct (the API cut at the cusp), so the
picture and the saved record disagreed with the form.

**Fix.** `previewCut(points, mode, cuspIndex, keep)` in `app/src/lib/cut-doubles.js`; the page
previews one result, the chosen one, and the form restores the chosen mode and arc after the
preview reload.

**Guard.** `tests/js/cut-doubles.test.mjs` — "a dot cut previews the arc, never the line's
halves": one run, deep-equal to `cutAt`, and the line modes still give 2 and 1 runs.

## 3. The name field was lost on preview (fixed in the same work)

The preview button is a GET of the page; the name now comes from the query like the four side
values, so a preview does not reset it.
