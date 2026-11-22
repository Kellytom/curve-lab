# PROBLEMS — the review desk (`/review/`)

Every fault this page has had, as it appeared, what was wrong, the fix and the guard. The clean
spec is `SPEC-review-int.md`.

**Rule:** a fix and its entry land together. If a guard is removed, the entry stays and says why.

No faults yet. The first guard is `app/scripts/check-review.mjs`: the cards, the five quick
buttons, the empty-selection message, and the refusal of a rating of 11 without a write.
