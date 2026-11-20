# SPEC — the hybrid desk (`/hybrids/`)

One page for every candidate of the hybrid family, so they can be judged, kept,
put aside or rejected — without filling the collection with rejects.

## What the page is for

The family is `x = C(t)^p`, `y = S(t)^q`, where `C(t) = (1 − t²)/(1 + t²)` and
`S(t) = 2t/(1 + t²)` are the rational circle. The middle-term polynomial `P` of
`(x + y)^n` is used in 2D only: as a tint (colour use) or as a radial scale
(radius use). The desk exists to look at all of them at once and decide.

## Words it owns

- **candidate** — one (`p`, `q`, `block`, `use`) combination, with its figure.
- **decision** — `keep`, `later` or `reject`; one per candidate, stored by name.
- **colour use** / **radius use** — the two uses of `P` (tint / scale).
- **block** — which middle terms of `(x + y)^n` are included.
- **crossing pairs** — the measure, counted as pairs, never as places.

## Layout

- The app shell: one header, one `<main id="main">`, the draft mark, the sentence
  "this page is the hybrid desk", no self-link.
- A count line: how many candidates, how many kept / later / rejected.
- A grid of cards, one per candidate, in a fixed order (colour sheet first, then
  each radius sheet, `p` then `q`).
- Each card: the figure, the id, the crossing-pair count, and three buttons.
- The formula and the station rule printed once at the foot.

## Rules, each with the check that fails without it

1. **Every candidate has a figure.** `scripts/hybrid_figures.py` writes one SVG per
   candidate into `app/public/hybrid-figures/`; `workbench/hybrids.json` lists them.
   Check: the page has one card per entry in `workbench/hybrids.json`, and every
   `<img>` answers 200.
2. **A decision is saved, not just coloured.** Pressing a button writes
   `{name, decision}` to `/api/sandbox-curves`. Check: keep one, reload, it is still
   kept.
3. **A save never erases another decision.** Each candidate is its own row, keyed by
   name. Check: decide two candidates, reload, both survive.
4. **No page errors.** Check: the browser run reports none.
5. **The numbers are exact where they exist.** The crossing count is the router's,
   written by the generator; the card prints the generator's number, it does not
   re-derive it.
6. **The drawing says what it is.** The foot states: stations are exact ratios,
   the join between them is a line, and no sin or cos is used.

## Not on this page

- No editing of `p` or `q`; the family is fixed by the generator. A kept candidate
  becomes a registry record in a separate step.
- No second store: the decisions live in the same `SandboxCurve` table the sandbox
  uses.
