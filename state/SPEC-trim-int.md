# SPEC — the trim desk (`/trim/`, `/trim/<uid>`)

**Status, 2026-11-24:** built; a trim saved end to end on c-0274 and removed.

**The pages:** `app/src/pages/trim/index.astro` (the list), `app/src/pages/trim/[uid].astro`
**The maths:** `app/src/lib/trim-curve.ts` (pure, node-tested)
**The save:** `app/src/pages/api/trim-curve.ts` → `createVariant` in `app/src/lib/desk-tune.js`
**The script:** `app/src/scripts/trim-desk.ts`
**The tests:** `tests/js/trim-curve.test.ts`, `app/tests/desk-tune.test.mjs` (the record's cut
metadata); the page check is `scripts/check-trim.ts`

## What it is

The operator, 2026-11-24: "cutting the legs off the curves using rational fractions of t".

Any curve with stored points can have its legs cut off. `t = 0` is the first station, `t = 1`
the last. The cut is given as two fractions, `from` and `to`, typed as `p/q` (a decimal is
refused on purpose). The stations between the cuts are kept; the legs outside are dropped; the
two cut points are placed exactly on the fractions by interpolating the one segment they fall on.

## The rules

- **A fraction is whole numbers, `p/q`, in 0 … 1, in lowest terms.** `1/4`, `3/4`, `1`; `2/4` is
  shown and saved as `1/2`; `0.25` is refused with a message, `3/2` is past the end, `1/0` is
  refused. Check: `tests/js/trim-curve.test.ts`.
- **A preset is one fraction, and its other end is the mirror `(q − p)/q`, ordered low to high.**
  `1/4 → 3/4`, `2/5 → 3/5`, `5/13 → 8/13`, `8/17 → 9/17`, `1/25 → 24/25`,
  `200/10001 → 9801/10001`, plus the whole curve `0 → 1`. The operator's rule, 2026-11-24:
  "each time follow that algorithm of (num-denom)/denom for the end". The denominators are
  hypotenuses where the fraction is a p-triple leg over its hypotenuse; the mirror itself is a
  parameter symmetry, not a second triangle.
- **The front cut comes before the back cut.** `from < to`; equal or reversed is refused.
- **The kept stations are the record's own, and the two new ends lie on a stored segment.** The
  cut points are exact in `t`; the curve between stations is the record's sample, and the saved
  record says `sampled`.
- **Every branch is cut by the same fractions, and every branch's two cut points are marked.** A
  record with `branches` (the cruciform and its kind) keeps each branch's middle; the branch
  count is preserved and the figure carries two red marks per branch. Check: the same test
  (`marks.length === 2 × branches`).
- **The record says how it was made.** `params.cut = { of, ofName, mode: "trim", from, to,
  sampled }`, the conversion algorithm is "trimmed at rational fractions of t", and the note names
  the parent and the two fractions. Check: `app/tests/desk-tune.test.mjs`.
- **The parent is never changed.** A trim is a new record with the next uid beside its parent,
  with the four side values chosen before saving; it lands on `/plates` beside the parent.
- **The save answers at once.** The record, database rows and exports are written in the request;
  the plate and the figure render in the detached child (`scripts/render_saved_curve.mjs`) under
  the render lock.
- **The tuning page is a door in and out.** `/tune/<uid>` carries
  "cut this curve's legs off at a rational t", whose link keeps the width, plus, minus and
  profile on screen — edited but not yet saved — so the cut is made with the band being looked
  at. The trim page's defaults are the record's own side values, and it links back to the
  parent's tune page; a saved cut's banner links to the new curve's tune page. Check:
  `scripts/check-trim.ts` (the door follows the slider, and the trim page keeps the value).
- **The preview follows the form.** `preview the cut` is a plain GET carrying the fractions; only
  `cut and save` is posted. Check: `scripts/check-trim.ts` (a decimal is refused on the page, and
  the caption follows 1/3 → 2/3).

## The pages

- **`/trim/`** leads with the curves on `/plates` — the 196 the plates page draws, in its star
  order — and the 209 other cuttable records follow, 50 a page, with a uid/name search. Each card
  opens its trim page and says `plates` when it is one.
- **`/trim/<uid>`** draws the whole curve grey, the dropped legs dashed ochre, the kept piece
  solid, and marks the two cut fractions in red. Under it, the cut piece is drawn with the side
  curves the plate will draw. The form carries the fractions, the four side values and a name.

## What it does not do

- **A rows record is sampled, and says so.** A curve stored as speed rows is drawn from the
  plate's own sampler (`app/src/lib/curve-points.js`, 700 stations); t is the fraction of that
  sample, and the saved record says `fromRows` and "sampled from ... speed rows" in its note.
- **No cut between sample stations.** The cut point is exact in t but lies on the straight segment
  between two stations; the curve there is the record's sample, never a new curve.
- **No batch trim.** One curve, one range at a time.
