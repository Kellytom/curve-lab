# FOLD-int — "above the fold", as this project means it

**Settled by the operator, 2026-11-23.** The words come before the numbers, because the
component is not a breakpoint.

## The definition

> "above the fold" … "it is what the user first sees when the page loads before they scroll."

- It is a **height in CSS pixels at the window the reader uses**, not a media query and not a
  device class. Two windows of the same width can have folds hundreds of pixels apart.
- It is measured from the **top of the page**, including the header; the header is what the
  reader sees first, so it is inside the fold whether it helps or not.
- A page is not "wrong" because a word falls above or below it. The point of naming it is to
  know, when a page is opened, what the reader is given before they have to work.

## The operator's calibration (2026-11-23)

The fold was not stated as a number. It was stated as four words that sit at it:

| page | the words | where they sit |
|---|---|---|
| `/plates` | `c-0022 wave3-balance` | just **below** the fold |
| `/review/` | `wave3-balance` | just **below** the fold |
| `/reduce/` | `logspiral-fit` | just **below** the fold |
| `/` (the hub) | `Square and frame lab`, inside the lab window | just **above** the fold |

Read together, those anchor the fold on that machine to roughly **550 to 800 px at a 1200 px
window** — the spread is real, because each page has a different opening. The hub's anchor is
higher than the others because it sits inside a window that starts lower down the page.

## Re-measuring it

```sh
node scripts/fold_report.mjs 1200      # the width of the window you use
```

The script prints the top of each anchor in CSS pixels. Change the width to your own; the
number that matters is the one at the window you read in. The hub's anchor is inside a still
now, so it is reported as "not found" until the window is live — that is expected.

## What to do with it

- **Do not add a page rule for it.** A `--fold` variable that nothing reads is decoration; the
  measurement is the record.
- **Do not shorten a page to win a pixel count.** The curves and the words are the point.
- **When the opening is the problem, change the opening.** A lead paragraph that wraps to five
  lines at 1180 px is five lines of the fold. Two shorter sentences, or a lead set beside the
  title, put the first card higher without touching the layout.
- **A wider text column buys height; a bigger side margin spends it.** The shell's margin is
  `1.25rem` (20 px) each side; a half-inch margin (48 px) would make every paragraph narrower
  and every long opening taller, which is the opposite of buying height. If the operator wants
  a half-inch margin, that is a look decision and the fold is the cost, not the reason.
- **A page with controls above its content** (the desks, the tune page) pays for them at the
  fold. That is why the tune page's readout now sits under the preview in the same column: the
  controls are one block, not a column plus a full-width paragraph.
