# curve-lab

A workshop for one thing: **curves that can be built exactly, and ornaments that
follow from them.**

The unit of work is the clothoid — curvature linear in arc length — and the
recent direction is a stricter one: build with pythagorean triples and let
everything else follow, so every joint lands on an integer lattice instead of
being snapped to one.

## What is where

| you want | open |
|---|---|
| what is true right now | `state/HANDOFF.md` |
| how the engine is wired | [Architecture](ARCHITECTURE.md) |
| the vocabulary | [Glossary](GLOSSARY.md) |
| the design thinking | [Philosophy](PHILOSOPHY.md) |
| the recovered corpus | [Corpus](CORPUS.md) |
| the accuracy budget and its precedent | [Fidelity](FIDELITY.md) |
| what to do next | `state/SESSIONS.md`, then `state/BACKLOG.md` |

## Working pages are not in this book

The generated pages — the curve studies, the offset and branch work, the
catenary study, the ornament board — live in `workbench/` and are served
directly, because they are read in a browser and rebuilt from a script:

```sh
.venv/bin/python -m http.server 8003 --directory .
# http://127.0.0.1:8003/workbench/workbench.html
```

This documentation site is the prose: the truth, the durable reference, the
design writing, and the reviews. Build it with:

```sh
.venv/bin/mkdocs serve      # live at http://127.0.0.1:8000
.venv/bin/mkdocs build      # static output in site/
```

## The short version of the design

A glyph is built from full lines — chains of segments whose curvature hands off
at each join — and the ornament is what those lines do when they meet. Three
parts, three tests: heavy base, clear middle, open top. The curve work exists so
that the base, the middle and the top can be *chosen* rather than discovered.
