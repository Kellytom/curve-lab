# The Inkscape round trip — how to send a curve over and take it back

*For whoever runs the desk: the operator, DeepSeek1, or the next agent. The
machinery is `inkscape/ph_actions.py`, `ph_svg.py`, `ph_handles.py`,
`ph_variant.py`, `ph_extension.py` + two `.inx` files, guarded by
`tests/test_ph_actions.py`, `test_ph_roundtrip.py`, `test_ph_variant.py`.*

---

## The contract

**The recipe is the truth; the SVG is a view.** A curve travels as its
speed rows (exact fractions) in the SVG's `<metadata>` block. The path
Inkscape shows is a Catmull-Rom cubic chain through the exact stations —
approximate between them, and the file says so. Reading the file back
reproduces the rows bit for bit: the round trip is lossless by
construction, because every edit on offer is exact algebra on the speed
rows. There is **no re-fit** anywhere in this loop.

## The closed vocabulary

Only these actions are offered. Each is an exact formula on the rows
(`inkscape/ph_actions.py`); anything else is refused with a miss in curve
units — never a percentage.

| action | exact effect | notes |
|---|---|---|
| translate `(dx, dy)` | the offset enters the position's **constant term alone** | rational; a view-level move |
| rotate | the speed picks up `(a + ib)` — a **half** angle from a p-triple | the position turns by the double angle, still rational |
| scale `q` | speed ×q, position ×q² | rational; the square comes free in the derivative |
| mirror | the speed is conjugated | a flag, not a rotation — a reflection isn't one |
| end-edit | the **top** coefficients of u and v | the end tangent and end speed; degree unchanged |
| recipe swap | the sibling's rows from the registry | the sibling already exists — no new record |

The degree gate reads `position = 2·speed + 1` off the rows before
anything is drawn; over the ceiling (11, or 7 in the prefer-7 mode), the
action is refused.

## How a drag becomes an action

The drawn chain is exact and deterministic (every node and handle a
Fraction), so a drag can be measured against it:

1. The user drags on-curve nodes in Inkscape and saves.
2. The receiver reads the drawn nodes from the path data and compares them
   with the recipe's own nodes. A shift under `DRIFT` (0.001 curve units —
   Inkscape 1.4.4's own text precision measured 4.8e-05) is rounding, not
   a drag.
3. Every candidate action re-draws the chain; its miss is the total
   distance over the dragged nodes. **One action must explain all the
   moved nodes** — the vocabulary applies to the curve, not to single
   nodes.
4. The winner rewrites the file with the acted recipe. If no legal action
   is within tolerance, the drag is refused and the miss is stated in
   curve units.

## Running it

The extension lives in Inkscape's user extensions folder
(`~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/`).
**Re-copy after every edit:**

    cp inkscape/*.py inkscape/*.inx ~/Library/"Application Support"/org.inkscape.Inkscape/config/inkscape/extensions/

**Send** — registry → SVG:

    INK=/Applications/Inkscape.app/Contents/Resources
    PYTHONPATH="$INK/share/inkscape/extensions" "$INK/bin/python3" \
      "$HOME/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/ph_extension.py" \
      /tmp/blank.svg --mode=send --uid=c-0002 --path=/tmp/out.svg

**Receive** — snap the drag, rewrite, propose, post:

    ... ph_extension.py /tmp/blank.svg --mode=receive --path=/tmp/out.svg \
        --variant=yes --post=http://127.0.0.1:4321/api/sandbox-curves

(A headless run needs a small input SVG — `/tmp/blank.svg` is fine. In the
GUI, the same extensions appear under **Extensions → Curve Lab**.)

## What comes back

- **The acted recipe** rewrites the file's metadata.
- **A variant proposal** (`--variant`) — the registry-variant payload with
  `base_uid` set, `transform` exact. **A translation is a view, not a
  curve**: a moved curve stays one curve, so translated placements are
  refused as variants; rotations, scales, mirrors and end-edits bake into
  the rows exactly and propose `parent+letter` (`c-0002a`,
  "euler-hook-end-edited"). A recipe swap maps back to the sibling already
  in the registry.
- **The candidate** (`--post`) goes to `POST /api/sandbox-curves` — the
  sandbox table is the funnel; promotion to the registry is the names
  flow's job. The registry is never written directly.

## The test that guards it

    .venv/bin/python -m unittest tests.test_ph_actions tests.test_ph_roundtrip tests.test_ph_variant

27 tests (14 actions, 7 round trip, 6 variant). The fixture `tests/fixtures/through-inkscape-c-0002.svg` is
Inkscape's own re-serialization — the snap is proven against Inkscape's
real precision, not self-produced numbers. Register rows 54 and 55 record
the two faults that wrote these guards (a running sum standing in for the
integral; a translation that stretched as 1+t+t²+…).

## The tie-breakers, verbatim

- "restrict the user to doing certain actions on the special grid so that
  any action could be reconstructed in the parametric polynomial.
  preferably degree 7 or lower, max 11"
- "dont say 'within the dial' since it is not a real expression and gives
  no exact meaning" — misses are stated in curve units.
