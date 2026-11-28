# SPEC — quintic-explained (docs page)

**What it is for.** One page that takes a reader from "what is a quintic in Inkscape"
to the expert record: the beginner's walkthrough first, the contract, the measured
miss and the C3 correction at the end. It is the explainer; `docs/QUINTIC-GUIDE.md`
stays the dialog reference, and this page links to it rather than copying it.

**Words it owns.** Quintic, six points, fullness, span, cubic chain, miss, bound,
record, seam. "Miss" is always stroke→quintic; "bound" is always the proved
chain→quintic limit. The three layers are named in that order.

**Layout.** Part 1 (beginner): what it is, fullness, numbered walkthrough, control
table, why cubics, what leaves the file, how to tell it worked. Part 2 (expert):
contract and the open question, the generated numbers block, the C3 correction,
fullness recovery, PH and offsets, what is not done. Links on their own lines.

**Rules, each with a check that can fail.**

1. Every measurement in the page is produced by
   `.venv/bin/python scripts/quintic_explained.py` into the `numbers` block.
   Check: `scripts/quintic_explained.py --check` fails when the block is stale.
2. The HTML twin is generated from the Markdown, never edited by hand.
   Check: the same `--check` compares `docs/quintic-explained.html`.
3. No sales words (robust, seamless, powerful, nice, leverage).
   Check: `grep -inE 'robust|seamless|powerful|nice|leverage' docs/QUINTIC-EXPLAINED.md`
   returns nothing.
4. The page never states the cubic-pair claim as true. The correction names the
   reason (a cubic's third derivative is constant) and carries the measured jump.
   Check: the words "third derivative" and "constant" appear in Part 2, and the
   numbers block has the C3 column.
5. Headings run beginner before expert. Check: the first `## ` is Part 1, the last is
   Part 2.
6. Numbers are plain decimals, no exponents. Check: the generator's `num()`;
   `grep -E '[0-9]e[-+]?[0-9]' docs/QUINTIC-EXPLAINED.md` returns nothing.
