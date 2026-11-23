# ASKS-int — the operator's asks, in their own words

This file exists because the operator said, on 2026-11-23:

> "i should not have to repeat myself"

An ask that lives only in the chat is gone when the session ends. The next
session reads the code, guesses what mattered, and fixes something adjacent.
So every ask is written here **when it is asked**, in the operator's words, not
paraphrased into a plan. A repeated ask is a fault in the first answer, and the
row says what blocked it.

Read this file at the top of every session (Tier 0 of `state/READING-int.md`).
A row is closed only by a commit or a command that proves it, and
`scripts/check_asks.py` fails the register when a row is incomplete.

| # | date | the ask, in the operator's words | status | what proves it | note |
|---|---|---|---|---|---|
| 1 | 2026-11-23 | "still doesnt have a way to save the cut curves" — asked 2–3 times | fixed | `6e458d6d`; click → save → reload on `/cut/c-0288` names the new uid | two answers read the code and changed the server; neither clicked the button on the page where the operator sees it. The faults were a name collision on the prefilled name and a result message lost in the dev-server reload. The lesson: test the ask where the operator looks, first |
| 2 | 2026-11-23 | "find a way to listen and make it part of agents. i should not have to repeat myself" | fixed | this file, the AGENTS rule, `scripts/check_asks.py`, `RepeatedAskTest` in `tests/test_regressions.py` | the mechanism is a register read at Tier 0 plus a check that every row carries a real commit or a next step; a repeated ask must say what blocked the first answer |
| 3 | 2026-11-23 | "use class V and make an html page so i can see each curve that is cut; model it on http://127.0.0.1:4321/plates with the same curves but a link to a tuner that will help us cut the curve and save the new gothic type curve" | fixed | `app/src/pages/gothic/index.astro`, `app/src/pages/gothic/[uid].astro`, `tests/js/gothic.test.js` | built and used: the desk lists curves, the tuner cuts and saves; c-0008a is saved and its plate renders |
| 4 | 2026-11-23 | "correction: everything that sasys ' rows only, no stored path' is a high degree parametric polynomial. is is not 'stored lines' go deeper; find the equation in the database. do what has to be done." | fixed | `app/src/lib/curve-points.js`, `tests/js/gothic.test.js` | the equation is the record's speedX/speedY; the desk samples it with the plate's own spine (240 stations on the list, 700 on the tuner), so the rows curves are cuttable |
| 5 | 2026-11-23 | "use c-0008 u-bowl for instance" | fixed | `workbench/curve-registry.json`, `app/src/pages/gothic/[uid].astro` | c-0008 at a 10 % cut is saved as c-0008a u-bowl-gothic, kept, with its plate |
| 6 | 2026-11-23 | "for example http://127.0.0.1:4321/gothic/c-0008 give the original curve at the bottom with integer hits, and the new curve at the top... we will not use percent in the end, but you can leave it for now. we will use rational fraction values of the parametric. if that is t, then t" | fixed | `app/src/lib/gothic.js`, `tests/js/gothic.test.js` | the figure has the new arch on top and the original below at one scale, with the removed middle and the integer hits; the cut prints and stores the exact t pair (9/20 … 11/20); percent is kept as the temporary control |
| 7 | 2026-11-23 | "c-0134 mobile-exact-helmet-45-5 is also interesting" | fixed | `app/src/lib/gothic.js`, `tests/js/gothic.test.js` | no mirror (9.97 %), so it is offered as one arm with the gap printed; 12.4° at a 10 % cut; the page opens |
| 8 | 2026-11-23 | "c-0134 is the 'helmet' is from an algorithmic parametric equation so the middle can be found, right? they all are parmetric algorithms. so that we can cut in the middle and do fun stuff,,....." | fixed | `state/SPEC-gothic-int.md` | yes: rows records store the equation, paths the construction's walk; both have the middle at t = 0.5, which is where the cut is made |
| 9 | 2026-11-23 | "are you having problems?" | fixed | `state/HANDOFF-int.md` | no blocker; the slow first hit after an edit is the dev server recompiling, and the page answers in about 0.8 s after that |
| 10 | 2026-11-23 | "first of all, we have to put in other curves than most of the ones listed;;;" | open | next: list every stored curve with points in `/gothic/`, not only the plates set, and open the page after the change | the list was the 2-star plates set (mostly doubles); the operator wants the other curves in the desk |
