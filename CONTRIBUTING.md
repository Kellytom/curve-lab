# Contributing

> **draft A** — a working draft, not a final text.

Thanks for looking. This is a small project with a strict habit: **a claim is
either proved by a test, or measured and printed with its number.** A picture is
never the proof.

## Set up

```sh
git clone https://github.com/Kellytom/curve-lab.git
cd curve-lab
bash scripts/build-native.sh          # the engine, about a minute
python3 -m venv .venv                 # no runtime dependencies
.venv/bin/python scripts/test.py --slim
```

You need a C++ compiler for the engine. Without one, `pip install -r
requirements-dev.txt` and set `CLOTHOID_BACKEND=pyclothoids`; the wheel is a
second opinion, not the default.

Every package, version and licence is in `DEPENDENCIES.md`. If you add one, add
its row there in the same commit.

## The loop

```sh
.venv/bin/python scripts/test.py --slim   # engine only, about 3 s
.venv/bin/python scripts/test.py --full   # the gate: Python, JS, data, pages
.venv/bin/python scripts/serve.py         # the lab pages, port 8003
.venv/bin/python -m mkdocs serve          # the book, port 8000
```

Run `--full` before you send a change. A truncated log hides a red test: read
the summary, or grep for `FAILED`, rather than the last four lines.

## Rules that are not negotiable

1. **One exact core.** Grid, bend, arc, inflections and closest live in
   `curve_lab/measure.py`, in `Fraction`. Do not add a second implementation.
2. **No floats on an exact path.** A `cos` or `sin` of a general angle is
   irrational and leaves the integer grid. Use a Pythagorean triple, or a
   rational `t = tan(θ/2)`.
3. **Positive y is up in the model.** SVG's y is down; the writer flips once, at
   output. Never inherit y-down silently.
4. **A fix lands with its test.** Add the test to `tests/test_regressions.py`,
   named after the fault, and add the row to `state/REGRESSIONS-int.md` in the
   same commit.
5. **A generated page is never edited by hand.** Change the generator in
   `scripts/` and rebuild. `scripts/stamp_draft.py --check` fails if a page
   loses its label.
6. **One number, one definition.** If two things share a name, name them apart
   in the same breath.

## The draft label

Every outward page carries `draft A`: an HTML page gets a corner badge and a
title suffix, a Markdown page gets one line under the first heading.
`scripts/stamp_draft.py` applies it, `--check` enforces it in the suite, and
`scripts/build-pages.py` re-stamps after a rebuild.

Two deliberate exceptions: book plate images carry no text at all, because the
image is the plate; and `llms.txt` / `llms-full.txt` are machine-facing files,
not pages.

## Naming

- Python: `snake_case`.
- JavaScript: `camelCase` for values and verbs for functions; DOM ids and
  classes in `kebab-case`, prefixed by the figure (`q9-plot`).
- Names say what the thing is: `bendRatio`, not `c`. Maths symbols stay on the
  page, with a descriptive code name beside them.

## Commits

- One action per commit, with a message that says what changed and why.
- Stage only the paths you touched.
- Say what you ran. If a number is in the message, it came from a command.
- Do not commit generated files by hand; commit the generator and run it.

## Where to start

- `llms.txt` — the map, if a tool is reading this.
- `docs/index.md` — the book's front page.
- `docs/VERIFY.md` — how a claim is checked.
- `state/BACKLOG-int.md` — the work queue, with the W-labels.
- `docs/GLOSSARY.md` — the words, each with one meaning.

## Questions

Open an issue with the command you ran, what you expected, and what you saw.
Numbers and file paths are more useful than screenshots.
