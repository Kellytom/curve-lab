# SPEC — quintic-lab (the sandbox page)

**What it is for.** A drawing pad in the browser where a stroke becomes six points
and a quintic, and the curve gets a width that thins at the ends and swells in the
middle. It is the Inkscape extension's maths without the install, so a shape can be
felt before anything is drawn in Inkscape. It is not a record: nothing is saved, and
the page claims no exactness for the drawn stroke.

**Words it owns.** Stroke (the hand), guide (the six points as taken), spine (the
quintic), rails (a constant width for comparison), modulated offset (the filled
shape, each side pushed along the normal by the width at that `t`). "Miss" is always
measured between the quintic and the cubic chain, in px.

**Layout.** Title and lede; one pad (`0 0 1000 540`) with a grid, the filled
outline, dashed rails, the dashed guide, the spine, the six marks and the readout
inside the drawing; the controls under it; one note explaining the offset and the
crossing count.

**Rules, each with a check that can fail.**

1. The page carries no rules: its `<script>` is one import of
   `app/src/scripts/quintic-lab.ts`, and the maths lives in
   `app/src/lib/quintic-lab.ts` / `scripts/lib/quintic-geometry.ts`.
   Check: `grep -c '<script' app/src/pages/quintic-lab.astro` is 1 and the tag is an
   import.
2. Coordinates are y up in the model, flipped once at drawing. Check: the axis note
   is inside the SVG (`x right, y up`); the lib's header states the flip.
3. The maths is the extension's: six even points or a best fit, the fullness blend
   `Pi = (1−α)Li + αGi`, the C2 cubic chain. Check:
   `node --test tests/js/quintic-lab.test.ts` (10 tests).
4. Every control changes the drawing, and the readout reports the measured cubic
   miss and the crossing count rather than hiding a crossing. Check:
   `node app/scripts/check-quintic-lab.mjs` (script loaded, drag drew, controls
   change the drawing).
5. Controls carry their unit or their symbol (`px`, `α`, `t`) so a number cannot be
   read in the wrong unit. Check: every `label.ql-field` text contains `px`, `α`, or
   a named position.
6. The figure labels itself inside the frame: axis note, readout at the top left,
   dashed guide and rails with the note saying what they are. Check: the SVG holds
   the axis text and the `ql-readout` element.
