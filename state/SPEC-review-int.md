# SPEC — the review desk (`/review/`)

The clean description. Faults live in `state/PROBLEMS-review-int.md`.

**Status, 2026-11-21:** first slice built and checked.

**The page:** `app/src/pages/review.astro`
**The driver:** `app/src/scripts/review.js`
**The write:** `POST /api/curve-stars` with `{ uids, stars }`
**The check:** `app/scripts/check-review.mjs` (headless, against a running server)

## 1 · What the page is

The operator: "i am trying to do bulk changes so i can quickly approve the curves instead of
hand rolling each one." One card per curve with its plate, its uid and name, its stars and its
provenance; a checkbox; a sticky bar that writes the stars once for the whole selection.

- [x] The scopes are **the plates** (2 stars or more, or a variant of a kept parent), **unrated**
      (under 2) and **every curve**; the counts are printed. Check: the three links return 200.
- [x] Selecting cards updates the count; **select all** toggles every pick. Check: the browser
      check.
- [x] One write for the selection; the page says `stars X on N curves`. Check: the manual round
      trip this session (two cards set to 2, then restored).
- [x] A write with no selection says `select a curve first` and sends nothing. Check: the check.
- [x] A bad rating is refused by the endpoint and shown in place; the card's stars do not move.
      Check: the check sets 11 and expects `not saved` with the card unchanged.
- [x] A bad uid is refused before any write (the note lookup precedes `updateMany`).
- [x] Only the note's `importance` changes; the exact curve is untouched; `data/curves.json`
      is refreshed after the write.
- [x] After a change, a reload re-filters the scope; the page has no hidden re-order.

## 2 · Words

    the plates     2 stars or more, or a new curve made from a kept curve
    unrated        under 2: 1 or none, including 0-star variants being reviewed
    every curve    all 371
    stars          1..10, or none. 2 or more is on /plates; 1 and none are off it.
    the selection  the checked cards; select all toggles them

## 3 · Layout

- [x] The sticky bar above the grid: the count, the quick ratings (10/5/2/1/0), a number with
      **apply**, select all and the status.
- [x] The grid is `minmax(280px, 1fr)`; the plate is 220 px high, contained; the provenance is
      under the name; the shell margin is the app's own; no width of its own.
- [x] The status sits in the bar, not in a banner: `saving`, `stars X on N`, or the refusal.

## 4 · Inherited from the tuning lab

The visible state beside the control, one write path, no dead controls, the shell margin, and the
rule that a failed read is never a write.
