# PROBLEMS — the stylesheets

Every fault the styling has had, as the operator saw it, what was wrong, and the guard.
The clean spec is `SPEC-css-int.md`.

## 1. The header took too much room and wrapped badly

**Seen:** "clean up the html css for the top of the page: it takes way too much
vertical space, and the items do a text wrap … indent so the 'curve-lab' looks like a
title for this page, and the rest like options."

**Wrong:** the brand, the draft mark, the page name and the whole menu sat in one flex
row of equal weight, so the menu wrapped into the same block and everything read as one
list. Nothing was a title; nothing was subordinate.

**Fix:** two rows. The brand is a title line at 1.12rem Georgia, the draft mark beside
it; the page name and the menu sit indented behind a 2px rule in the mono face.

**Guard:** the header is measured in `check-prime-mover-page.mjs` and in the CSS spec —
96 px is the ceiling at 1280 px wide, 86 px the working value.

## 2. The header's line spacing was wrong

**Seen:** "first thing again: fix the line spacing on the header."

**Wrong:** the two rows were set from the flex gap alone, with no line-height of their
own, so the title and the options drifted apart at some widths and touched at others.

**Fix:** explicit line-heights — 1.2 on the title row, 1.15 on the brand, 1.5 on the
options — with a `0.15rem` margin under the title row.

**Guard:** the header-height measurement fails if the block grows past its budget.

## 3. Pages had no margin of their own

**Seen:** the raw-number tables pushed the whole document sideways on `/stage-two/`.

**Wrong:** there was no `main` rule at all; pages relied on pico's `.container`, so a
page that opted out had no margin, and any wide table widened the document.

**Fix:** one `main` rule in `app-shell.css`, and `overflow-x: auto` on panels.

**Guard:** `check-pages.mjs` asserts no document-level horizontal overflow at two
widths.

## 4. Text zoom was never tested

**Seen:** "this user usually increases the size using command + twice. other users
might do something else."

**Wrong:** the layout was only ever checked at 100% width. Browser zoom shrinks the
layout width to 853 px at 150%, which is a different layout and was never measured.

**Fix:** a written rule — no sideways scrolling, the brand on one line, the menu free to
wrap — and a gate that measures it.

**Guard:** `app/scripts/check-layout.mjs` runs at 1280, 853, 683 and 420 px.

## How a new problem is added

The operator's words first, then the cause in one sentence, the fix, and the command
or measurement that fails if it returns.
