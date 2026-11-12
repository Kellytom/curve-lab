# Retired agent rules — 2026-11-11

Rules that were taken out of `AGENTS.md`, `state/READING-int.md`,
`next-fhandoff-int.md` and `tph_tri_chain/` because they were about focus, and
they were costing more than they bought. Kept verbatim so the history is
recoverable, not so they can be reinstated without thought.

## Context window and reading

> "Keep the context small. Read only what the current action names."

Why it went: it turned every message into a new narrow spec, and made a reading
list outrank the person in front of it. Replaced by: instructions accumulate,
and a new emphasis adds to the work.

> "`next-fhandoff-int.md` — the one action; **nothing else decides priority**."

Why it went: it said a five-line file outranks the operator. A handoff is the
default next action when nobody has said otherwise.

## Work-in-progress gate

> "add no code until the rule is written and checked"

Why it went: the rule was never written, and the operator kept asking for code,
pages and figures. The gate blocked the work it was meant to protect.

> "Holding pen / held / do not wire in" — a status assigned to `tph_tri_chain/`.

Why it went: it made every step feel like an exception that needed permission.
The directory is ordinary working code.

## Figures

> "Never load images … a visual judgement is the operator's — ask them to look
> and report."

Why it went: the engine genuinely cannot accept image input, and that fact
stays. What went is the policy that ends the work at "ask the operator" — it
turned every figure into a round trip. Replaced by a plain technical note:
SVG is text and is fine; raster sizes come from `file` or `sips`.

## Not retired

> "Never print the token."

Still live, and not a focus rule. The auth token sits in `~/.config/<app>/token`
and in Secret Manager; printing it puts a live credential into a transcript that
is stored and may be shared. Nothing else depends on it.
