# SPEC — the root lab (`/roots`)

The clean description. Faults would live in `state/PROBLEMS-roots-int.md`; none yet.

**The page:** `app/src/pages/roots.astro`
**The maths:** `app/src/scripts/lab-roots.js` (`build`, `explain`)
**The twin:** `scripts/root_search.py` builds the same numbers exactly, so a find on the page can
be written down as a record
**The test:** `tests/js/root-lab.test.mjs`; the page check is `app/scripts/check-pages.mjs /roots/`

## What it is

The recipe that worked — `lace-1of9-3` — made visible: a mirrored pair of roots for the y speed,
a stack of roots at ½, and one x speed. Drag the numbers and the curve redraws; the note under it
says what the numbers did, generated from the curve on screen.

- **The pair is mirrored.** Roots at `p/q` and `(q−p)/q`; every root `r` has a partner `1 − r`,
  which is what keeps the curve symmetric about `t = ½`.
- **A second pair can be added.** Roots at `p2/q2` and `(q2−p2)/q2`; `p2 = 0` turns it off. The
  operator's TODO: the lab "needs a second pair … before it can find anything" (2026-11-23).
- **The x row can vary.** `u(t) = A + B(t² − t)`, integers, default `A = 1, B = 2` — the known
  good `1 − 2t + 2t²`. It stays symmetric about ½ for any `A`, `B`, so the sums stay proper and
  stay mirror-symmetric.
- **The curve is the PH integral** of `(u² − v², 2uv)`, not the rows themselves. Treating `u, v`
  as velocities draws a different curve.

## The rules, each with a check

- [x] The maths is one module, exported for Node. Check: `tests/js/root-lab.test.mjs` imports
      `build` with no `document`.
- [x] Both speed rows are symmetric about ½, so the curve is: `x(1−t) = x(t)`, `y(1−t) = y(t)`.
      Check: the same test, on the default curve and on one with a second pair.
- [x] A second pair adds two roots to `v` and nothing to `u`. Check: the same test, degree +2.
- [x] The x row changes only `x` (through `u² − v²`), and keeps the curve symmetric. Check: the
      same test with `B = 0`.
- [x] The page's numbers are the picture's numbers: the facts line prints the crossing pairs,
      inflections and grace the drawing was computed from.
- [x] The page and the Python twin build the same rows for the same inputs. Check: the twin's
      docstring names the construction, and `--second` / `--x` take the same two choices.
- [x] No floats in the construction: the roots are integer rows and the denominators are never
      cleared, so a zero coefficient cannot break it.

## What it does not do

- No save from the page. A curve found here is written as a record by the search script.
- The x row is the symmetric family `A + B(t² − t)`, not an arbitrary quadratic; a row that
  broke the symmetry would also break the "sums stay proper" argument.
