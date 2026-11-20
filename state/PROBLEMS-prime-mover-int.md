# PROBLEMS — the prime mover page (`/prime-mover/`)

Every fault this page has had, as the operator saw it, what was actually wrong,
and the guard that keeps it fixed. The clean spec is `SPEC-prime-mover-int.md`; this
file is the scar tissue, kept so nobody fixes the same thing twice.

**Rule:** a fix and its entry land together. If a guard is ever removed, the entry
stays and says why.

## 1. The page was not in the app

**Seen:** "remember we are in astro" — a standalone HTML file had been written into
`workbench/` instead of a page in the app.

**Wrong:** the project has one shell (nav, theme, skip link) and one build. A stray
file bypasses all of it and does not get checked.

**Fix:** the page is `app/src/pages/prime-mover.astro`; the stray file and its throwaway
generator were deleted.

**Guard:** `app/scripts/check-pages.mjs` visits `/prime-mover/` and asserts no page errors
and no self-link.

## 2. "Negative set, below the axis"

**Seen:** "it is definitely not supposed to be 'negative set, below the axis' as I
have said about 3+ times … it is the first part of the i set."

**Wrong:** colouring was described by where the dots fell, not by what they are.
The label taught the consequence instead of the rule.

**Fix:** blue is the **first part** of the i set (`i < 0`); orange is the **second
part** (`i > 0`); they are drawn interleaved so they alternate. The phrase "below
the axis" is gone from the page.

**Guard:** shapes alternate around the ring (`S O S O …`), and the page text no
longer contains the axis phrasing.

## 3. The loop stopped short of a turn

**Seen:** "land the curves at ±372 … go past the end."

**Wrong:** six steps reached 318.78°, so the loop never completed a turn.

**Fix:** seven steps reach 371.91° for `(3,4,5)`; the number of steps per triple is
now chosen as the smallest that passes a full turn.

**Guard:** the figure title names the triple and the step count; the driver table's
last row is `+1`.

## 4. A rounded number placed the dots

**Seen:** "no cheating, no nudging. numbers must be exact on top and bottom."

**Wrong:** the wave placed stations using `53.1301`, a rounded angle. Positions
looked right and were not derived from the data.

**Fix:** x comes from the exact counter `k/steps`; y comes from the stored ratios.
The angle is printed as a note only.

**Guard:** the table is checked against a value computed in the check itself, and
no table cell may contain a decimal point.

## 5. Decimals in the tables

**Seen:** "i see decimals. please use rational fractions", then "exact does not mean
fraction. it means integer value or rational fraction."

**Wrong:** coordinates were printed with `toFixed(2)`, which hides the ratio and
cannot be checked.

**Fix:** every value is a whole number or `n/d`; whole numbers are written whole
(`1`, not `1/1`).

**Guard:** no cell contains `.`; integers appear without a denominator.

## 6. The imaginary unit came back

**Seen:** "did imaginary number sneak back in? what is this? (44+117i)/125", then
"we ditched imaginaries because for example it adds sqrt5".

**Wrong:** the step table printed complex notation, so `i` meant two things on one
page (the dial and the square root of minus one). Worse, a complex step imports an
irrational length, which is why it was dropped in the first place.

**Fix:** a step is always written as its triple, `(3, 4, 5)`. The reason is recorded
in `state/EXACT-NUMBERS-int.md`.

**Guard:** `scripts/check_no_imaginaries.py` (runs in `scripts/prepush.sh`), plus an
assertion that no `number + number i` appears on the page and that the step reads as
a triple.

## 7. Rotten patching left dead code

**Seen:** "something is broken… you have some restriction making you not do the
job" — the page had two helpers that only returned `pad`, three checkboxes wired to
nothing, a `picked` value written and never read, and two copies of one comment
block.

**Wrong:** a dozen string replacements in a row, each blind to the rest of the file.

**Fix:** the file was rewritten whole in one pass.

**Guard:** the page check asserts there is no dead control; the unused-variable
lint runs in `npm --prefix app run check`.

## 8. Two minus signs

**Seen:** caught by the first run of the new page check: the table printed
`-16124/78125` while the prose used `−`.

**Wrong:** `String(negative)` gives a hyphen; the project writes the true minus.

**Fix:** one `ratio()` helper builds every printed number with U+2212.

**Guard:** the check compares the table against values built the same way, and the
page text is asserted to contain no hyphen in a number.

## 9. Branch strokes with no meaning

**Seen:** "take away all those lines from fig 1. i really don't see the need."

**Wrong:** a short stroke was drawn at every station as a "preview of stage II".
It crowded the ring and said nothing.

**Fix:** removed, with their constant and comment.

**Guard:** the ring has exactly three lines (two axes and the seam), one path (the
loop), and zero green marks.

## 10. Lines on Fig. 1, again

**Seen:** "take away all those lines from fig 1. i really don't see the need", and
after the branches went, "imagine my surprise to see lines on figure 1 again".

**Wrong:** the branch strokes were removed, but the loop path was not: it joined the
stations in i order, so every pair of neighbouring stations was a chord straight
across the circle. The seam was a second chord. Both were read as clutter, and the
second one survived the first fix.

**Fix:** Fig. 1 draws the dashed reference circle, the two axes, the station marks
and their labels — and nothing else.

**Guard:** the page check asserts exactly two lines on the ring (the axes), zero
paths, and zero green marks. A new chord fails the check.

## 11. The circle was three quarters off the page

**Seen:** "you dont understand or graph basic geometry correctly … he who does not
understand geometry shall not enter here."

**Wrong, measured:** the figure put the origin at the **bottom-left corner** of a
620 × 620 drawing and gave the window only positive coordinates (0…27). A circle
centred there with radius 25 is 453 px wide, so it ran from x = −380 to x = 528 and
y = 94 to y = 1002: **three quarters of it lay outside the canvas**. What the page
showed was an arc, labelled as a circle. The geometry of the triangle was right;
the window was not.

Numbers, from the page itself: centre `(74, 548)`, radius `453.70`, canvas
`620 × 620`.

**Fix:** the figure is rebuilt on **JSXGraph** (open source, installed as
`jsxgraph@1.11.1`), with the origin at the centre, the window `−27 … 27` on both
axes, equal scale on both axes, and every object constructed from points rather
than placed by hand at pixels.

**Guard:** the check measures the rendered circle against the canvas and fails if
any part of it leaves the visible area — the exact test that would have caught this
before it shipped.

## 12. Three triangles drawn as three separate shapes

**Seen:** "no no no no! basic geometry! we are walking around the circle. the next
triangle has side 24 that is shared with triangle 2 … we are flipping triangles and
laying them on top of each other."

**Wrong:** I drew triangle 1, its mirror, and then a *third* triangle standing on its
own with the step doubled. Each was placed as an independent shape. The construction
is a **chain**: every triangle is the mirror of the one before across a shared side,
alternating the hypotenuse and the 24 leg, so the feet walk the 24 circle and the
apices the 25 circle. Independent shapes cannot show that, which is why the picture
looked like three drawings rather than one walk.

**Fix:** the figure is built by repeated reflection in JSXGraph — the library does
the geometry, and each new triangle is generated from the previous one.

**Guard:** the page check counts the chain's segments (three per triangle) and the
dashed reference circles; a hand-placed extra shape would have to change the count.
The walk is 23 triangles, so it passes a full turn (373.98°), and every apex carries
an orange ring because the apex is the station the engine uses.

## 13. A temporal dead zone broke the page

**Seen:** the page rendered nothing and the console said
`Cannot access 'DRIVE_STEPS' before initialization`.

**Wrong:** helpers were appended after the first call to `draw()`.

**Fix:** declarations moved above their first use, and the file reordered so the
reader sees the order the browser runs.

**Guard:** the page check fails on any page error, so a dead page cannot pass.

## 13. Four constructions parked, not deleted

**Seen:** "we just spent hours finding the right way to walk the circle for 7,24,25,
and now you are using something else."

**Wrong:** the page carried four other ways of walking — the `(3,4,5)` seven-step
chain, a sine wave of `x` and `y` against the counter, a test-grid table of step
budgets, and a triple chooser. Each was built before the walk was settled, and each
invites the reader to think the walk is negotiable.

**Fix:** the page now shows only the settled walk: the triangle figure, the twelve
hit points, and two tables (exact fractions, and the compressed `a = x/24`,
`b = y/7`, hypotenuse form). The other four are removed from the page.

**Not working for now, kept in the record:**

- the `(3,4,5)` seven-step chain, and its driver table;
- the `x(i)` / `y(i)` sine plot with the pale reference curve;
- the test-grid tables (125 / 625 / 3125 / 15625);
- the triple chooser and the guard line.

They were honest experiments and they are superseded. If one comes back it must run
on the settled walk, not beside it.

## 14. Stage II merged in, and the page tidied

**Seen:** "we need to choose variables and see equations that are common to them both."

**Wrong:** the walk lived on one page and the curves on another, so the shared object —
`walker(k)` — was invisible, and the two pages drifted apart (two different walks at
one point).

**Fix:** one page. The triple chooser drives every figure; the equations for the walker,
the curve and the spirograph sit together; the numeric tables moved to the notes.

**Guard:** the page check asserts the triple chooser drives the board, the chart, the
curve and the spirograph; and that no numeric table is back on the page.

## 15. The thin triple froze the page, and Fig. 3 showed a dot

**Seen:** "dont allow step 9 for the spirograph when i am using the very thin
triangles. the page becomes unresponsive. you are using bigint?" and "all i see is a
little blue dot in the top left."

**Wrong:** two faults. The spirograph multiplied BigInt rationals by the thin triple's
hypotenuse for ninety-nine steps at ratio 9 — thousands of digits, seconds of work. And
Fig. 3 framed itself on the largest value, so a shallow arc of stations (the half walk
at 4°) sat at the edge of an empty square and read as a dot.

**Fix:** a cost estimate per ratio, and ratios above it disabled (ratio 5, 7 and 9 are
off for `(56, 783, 785)`); and Fig. 3 now frames the drawn points, never tighter than
the unit circle.

**Guard:** the page check asserts the chooser disables the expensive ratios for the
thin triple, and that Fig. 3 draws one dot per station.

## 16. The spirograph drew nothing for the thin triple

**Seen:** "at the thin triangle Fig. 4 · the spirograph doesnt work."

**Wrong:** the stations are exact BigInt ratios, and the thin triple's denominators run
to hundreds of digits. The drawing converted them with `Number(x) / Number(d)` — both
sides became `Infinity`, so every coordinate was `Infinity / Infinity = NaN`. The SVG
was written with `MNaN,NaN`, and the browser dropped it. The data was right; only the
conversion was wrong.

**Fix:** one conversion for the whole project, `toFloat(n, d)`, which divides in BigInt
at a fixed scale of 10¹² before converting. Twelve digits of precision, no overflow.

**Guard:** the page check asserts no `NaN` or `Infinity` in any coordinate or path
attribute of the three figures — a bad conversion fails the run instead of drawing an
empty box.

**Enforced at the boundary:** the conversion is a fixed-point shift in the driver
(`fixed(n, d, 30)`), so the quotient is small whatever the size of the inputs. A
conversion outside the driver would be a second way to draw the same number, which is
how the first fault happened.

## 17. The default the operator asked for twice was not the page's default

**The operator's words:** "i must have said put the thin triangle with the 2 quadrant
button on as default and no one cared what i said..."

**What was actually wrong:** the thin triple and the half box were wired to the
chooser's `change` event only. The markup still opened on `(7, 24, 25)` with the box
unticked, so a reader who never touched the dropdown saw the wrong start — including
the operator, every time the page was reloaded.

**Fix:** the markup is the default: `selected` on the `(56, 783, 785)` option and
`checked` on `#pm-half`. The `change` handler stays, so another triple clears the tick
and the thin one puts it back.

**Guard:** `app/scripts/check-prime-mover-page.mjs` reads the chooser and the box on
load and fails unless the triple is `56,783,785`, the box is ticked, and the hit chart
draws 23 points with 46 guides. Before the fix that check would have failed on all
three counts.

## How a new problem is added

1. Write the operator's words first — they are the evidence.
2. Say what was actually wrong, in one sentence.
3. Say the fix.
4. Name the guard: the command, the test, or the assertion. If there is no guard,
   write "none" and say why that is acceptable.
