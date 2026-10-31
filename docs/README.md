# docs

What is in this folder, which pages are generated, and where new writing belongs.

## Start here

| File | What it is |
|---|---|
| — | The state files (`HANDOFF`, `BACKLOG`, `SESSIONS`, `WORK`, `STATUS`) live in `state/`, not here. |
| `HANDOVER.md` | Durable reference: architecture, deploy, security, decisions. Long on purpose. |
| `FIDELITY.md` | **The accepted accuracy budget** (1.4–1.6%), its precedent and metrics. |
| `REVIEW.md` | Architecture and print review; act after the current work. |
| `ARCHITECTURE.md` | How the engine and the spine layer fit, and which gate conditions hold. |
| `WEB-GUIDE.md` | The browser workbench: controls, the design recipe, the status line, the limits. |
| `SPINE.md` | The spine layer step by step: turns, closure, cusps, rails, and a worked S-curve. |
| `GLOSSARY.md` | Plain-English terms for both sides, and how the vocabularies map. |
| `CURVE-MODEL.md` | Design/Segment, Piece/Trace, terminals, junctions, Section, Bundle, clearance, grades. |
| `CORPUS.md` | The recovered plates, the terminal and spiral formats, units, regenerating. |
| `VERIFY.md` | The four checks and what passing means. |
| `CREDITS.md` | The engine's authors, the corpus, the licences. |

## Handwritten reference

| File | Subject |
|---|---|
| `PHILOSOPHY.md` | What a glyph is: parts, full lines, sections, joints. |
| `CLEARANCE.md` | The clearance/crossing rule and its limits. |
| `JUNCTION.md` | Junctions: vocabulary, fillet, what comes next. |
| `PRIMAL.md` | Fire, water, earth, air: the primal ornaments and their gate. |
| `caps.md` | Cap families and the 120° rule. |
| `sandbox.html` | Handwritten index of the working pages. |
| `clothoid-grid-3125.md` | The 3125 lattice and the old source pages. |
| `web.md` | The web MVP. |
| `PROJECT.md`, `TODO.md` | Older planning, kept for history. Do not treat as current. |

## Generated working pages — not here any more

The working pages moved out of `docs/` to `workbench/`, on their own server root:

    .venv/bin/python -m http.server 8003 --directory sandbox

`docs/` is prose only: the durable reference
(`HANDOVER`), the design writing, and the reviews. A generated page never
belongs here, because a generated page is a *working* artefact — it is read
with a browser, rebuilt from a script, and thrown away when the question it
was built to answer is settled.

An **HTML twin of a markdown file stays here**, beside its source:
`HANDOVER.html` is the printable mirror of `HANDOVER.md` and is kept in step by
hand. Prose and its twin are one artefact; a generated page is not.

`workbench/` holds one generator per page (`scripts/<name>.py`, or
`scripts/board/build-board.mjs` for the board), plus the hand-written index
`workbench/workbench.html` and a one-line `workbench/index.html` that points at it
for now.

## Conventions

- The app is **+y up**, page 200 × 250 mm. Recovered page data is stored as
  found, which is y-down — say so when you quote it.
- `W` numbers are work items and `P` numbers are plates; do not renumber them.
- Generated pages carry links back to the work board; keep that shape when adding
  one.
- The spike has its own docs and its own generators:
  `pythagorean-spiral/docs/` (`EXPLAINER`, `GALLERY`, `EXTREMES`, `TRANSFER`,
  `CLOUD`, `CLOUD-FORM`), each with an HTML twin and a `scripts/*.py` source.
- New handwritten docs go here as `docs/<subject>.md`. New generated docs get a
  script, a line in the table above, and a note in the script's docstring.
