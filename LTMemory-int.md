# LTMemory-int — long term memory

Read this first, every session. It exists so a new session can be useful in two
minutes, and so the same ground is not dug twice.

## Read in this order

1. **this file** — the map and the invariants.
2. `state/ACHIEVEMENTS-int.md` — every result we have, with the command that
   re-derives it. Start a session with `.venv/bin/python scripts/recheck.py`.
3. `state/HANDOFF-int.md` — current truth, what is in flight, what is next.
4. `workbench/workbench.html` — the pages, chosen by intent.

Nothing else unless the action names it. `docs/HANDOVER.md` is deliberately long.

## The map

| path | what it is |
|---|---|
| `curve_lab/` | the engine: `Design`, `Segment`, `Piece`, clearance, fillet, junction |
| `web/server.py` | the app: auth, rate limit, `/api/render` |
| `workbench/` | the input pages, one per idea; each has one generator |
| `scripts/` | the generators, the doc builders, and the checkers |
| `docs/` | prose that mkdocs builds; `docs/PH-INTEGER.md` and `docs/HUB.md` are generated |
| `state/` | `HANDOFF-int.md`, `ACHIEVEMENTS-int.md`, `BACKLOG-int.md`, `monitor.log` |
| `founder/` | screenshots and notes, tracked on purpose so they are backed up |
| `tests/` | the suite; `scripts/test.py` runs a fast subset by default |
| `pythagorean-spiral/` | the exact spine layer: rational turns, no floating point |

## Page ↔ generator

Every workbench page is built by one script. If you change a page, change its
script; never the HTML.

| page | generator |
|---|---|
| `workbench/generators.html` | `scripts/generators.py` |
| `workbench/euler-match.html` | `scripts/euler_match.py` |
| `workbench/euler-square.html` | `scripts/euler_square.py` |
| `workbench/hearts.html` | `scripts/hearts.py` |
| `workbench/catenary.html` | `scripts/catenary.py` |
| `workbench/primal.html` | `scripts/primal.py` |
| `workbench/principles.html` | `scripts/principles.py` |
| `workbench/spine-sheet.html` | `scripts/spine_sheet.py` |
| `workbench/branch-points.html` | `scripts/branch_points.py` |
| `workbench/piece-model.html` | `scripts/piece_sandbox.py` |
| `workbench/fleur-study-01.html` | `scripts/study_01.py` |
| `workbench/ornament-board.html` | `scripts/board/build-board.mjs` |
| `workbench/workbench.html` (the hub) | `scripts/hub.py` + `workbench/manifest.json` |
| `docs/PH-INTEGER.md` + `.html` | `scripts/ph_doc.py` |

Two pairings have mismatched names (`piece-model`, `fleur-study-01`); they are
listed here rather than renamed, because the scripts are referenced elsewhere.

## The checkers

| command | what it proves |
|---|---|
| `scripts/recheck.py` | eleven claims re-derived from scratch; writes `state/ACHIEVEMENTS-int.md` |
| `scripts/test.py` | the fast suite (~17 s); `--full` for everything (~42 s) |
| `scripts/hub.py` | rebuilds the hub and every page's bar — **run after any page generator** |
| `scripts/monitor.py` | tells a local failure from a network one |

## One server

```sh
.venv/bin/python scripts/serve.py        # http://127.0.0.1:8003
```

Start it at the top of **every** session; it is idempotent, so running it
when it is already up prints "already serving" and exits 0. It serves the repo
and redirects bare page names (`/catenary.html`) to
`/workbench/catenary.html`. Do not start a second `http.server` — 8003 is the
one, and ports 8000/8001/8002 belong to other projects.

## Invariants

- **Exact means Fraction.** Anything claiming exactness is computed in
  `fractions.Fraction` and asserted integral before it is drawn.
- **Every percentage is an error**, as a share of a stated reference. Where a
  number is not an error, say so in words.
- **A curve is cheap exactly when it has a singularity** — a node, cusp or
  triple point. Smooth curves (squircle, heart) are not rational and cannot be
  made exact.
- **One grid per curve** for now; the grid is a factorisation problem, not a
  size problem.
- **Say where a thing fails.** Three figures on `hearts.html` are recorded as
  broken rather than tuned to look acceptable.

## Already settled — do not redo

- `from_pairs` agrees with `from_hermite`; the half-angle bug is fixed.
- Degree is `n = deg h + 2 max(deg u, deg v) + 1`; quartics and sextics need `h`.
- The square-discriminant route gives 0 of 17,168 hits on the rung ladder. Dead.
- PH does not buy integer milestones; `mⁿ` is the floor and PH costs 3 or 15.
- One clothoid cannot do G2 (Bertolazzi–Frego); two or three can.
- Clothoid chains cannot cross a cusp; the roulettes keep 9–63% error.
- The bean, pear, piriform, trifolium and cruciform are rational and exact; the
  heart and the squircle are not.
- The 3-4-5 ladder is fine to 3125: 350 rungs, median gap 0.14°.

## Open

- The heart half (Fig. 3/4 on `hearts.html`) drifts at 11.7% — the sample path
  has a 0.5-unit jump at the lobe tip, which is where the error comes from.
- Double tangency: the model is rotation *plus* placement; no solution yet.
- The Gerono leaf: the double-tangent line is right, the arc choice is not.
