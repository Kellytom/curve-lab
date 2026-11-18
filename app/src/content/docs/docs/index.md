---
title: "curve-lab"
---

> **draft A** — a working draft, not a final text.

**curve-lab is a workshop for curves that can be built exactly, and for the
ornaments that follow from them.**

The older layer is the Euler curve — curvature linear in arc length. The newer
layer is stricter: build with whole-number polynomials and Pythagorean triples,
so every point lands on an integer grid instead of being snapped to one.

## What is where

| you want | open |
|---|---|
| what the project is for | [Project](project.md) |
| how the engine is wired | [Architecture](architecture.md) |
| the words used here | [Glossary](glossary.md) |
| the design thinking | [Philosophy](philosophy.md) |
| why integer curves | [Integer PH curves](ph-integer.md) |
| how a claim is checked | [Verification](verify.md) |
| where every folder is | [Structure](structure.md) |
| the accuracy budget | [Fidelity](fidelity.md) |
| the recovered corpus | [Corpus](corpus.md) |

## Run it

```sh
.venv/bin/python scripts/serve.py      # the lab, http://127.0.0.1:8003
npm --prefix app run dev                # this book, http://127.0.0.1:4321/docs
cd app && npm run dev                  # the Astro app, http://127.0.0.1:4321
```

Three layers: the Python engine, the generated lab pages, and the Astro app.
The README at the repository root has the first commands and the engine's
options.

## Working pages are not in this book

The generated pages — the curve studies, the offset and branch work, the
catenary study, the ornament board — live in `workbench/` and are served
directly, because they are read in a browser and rebuilt from a script.

This documentation site is the prose: the truth, the durable reference, the
design writing, and the reviews.

## The short version of the design

A glyph is built from full lines — chains of segments whose curvature hands off
at each join — and the ornament is what those lines do when they meet. Three
parts, three tests: heavy base, clear middle, open top. The curve work exists so
that the base, the middle and the top can be *chosen* rather than discovered.

## For maintainers

`state/` holds the working notes: the handoff, the register of fixed faults, the
design decisions, and the queue. They are written for the next session, not for
a first reader, and they change daily. Start from this page, and use `state/`
only when you are changing the work.
