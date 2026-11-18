# Verification

> **draft A** — a working draft, not a final text.
Four checks. Each answers one practical question, and each can fail on its own.

## 1. Does the curve engine still work?

```sh
.venv/bin/python -m unittest discover tests
```

239 tests: curve geometry, pieces, ends, junctions, clearance, the web API, the
shared-token gate, and the work board's principle cards. When they pass, the
engine still does what it says.

*Status:* 239 pass (1 skipped), 2026-10-30. The spine bridge is included:
`tests/test_spine.py` checks the anchor import, the 200 × 250 sheet and the
declared contact; `tests/test_spine_study.py` holds the chain study to the
1.6% fidelity rule; `tests/test_practical.py` holds the practical profile and
the boundary-tangent regression.

## 2. Does the spine layer still work?

```sh
cd pythagorean-spiral && ../.venv/bin/python -m unittest discover -s tests -t .
```

139 tests: exact closure, the exponent dial, joins and forks, the rails, large
drawings in ordinary decimals, placement, and a frozen digest of the legacy curl
so its shape cannot drift by accident.

*Status:* last run 2026-10-29, all passing.

## 3. Do the local and deployed copies match?

```sh
.venv/bin/python scripts/check-parity.py
```

Compares the served files, presets, caps, the drawing and the report between the
local server and the deployed copy. Both must be running. This is a standalone
audit and is never run during a handoff.

## 4. Do the pages fit small screens?

```sh
node scripts/check-web.mjs
```

Draws the documentation pages and the app at 900, 390 and 320 pixels wide, and
fails if anything overflows sideways. It starts its own headless Chrome; single
screenshots use `scripts/shot.mjs`, which launches its own browser through
Playwright — nothing needs to be running first.

## What passing does not mean

Passing shows the code follows its rules without crashing or breaking an
invariant. It says nothing about how the result looks:

- how naturally a curve sweeps along its chords;
- how closely a transferred cap matches its source plate;
- how a veil or a fill reads to the eye.

Those are recorded as measured studies in the documentation. Read the numbers
there; they are evidence, not tests.
