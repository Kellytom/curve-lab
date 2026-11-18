# Where everything lives

**Repository root: `/Users/thomaskelly/developer/curve-lab`** — every path below
is relative to it, and `$REPO` in a command means that directory. The repository
sits under `/Users/thomaskelly/developer/`; it is not inside any other project.

Generated from the tree on 2026-11-17. Excluded because they are large or
regenerable: `.git`, `node_modules`, `.venv`, `vendor/`, `reference/` (13 GB,
gitignored except the licensed images), `out/`, `site/`, `dist/`.

## Top level

| path | files | what |
|---|---|---|
| `.github/` | 1 | the manual `native` workflow |
| `app/` | 21 | the Astro app: hub, lab, book, finder, API routes |
| `book/` | 61 | the exported plates: PNG, SVG, the manifest |
| `build/` | 51 | the compiled `libclothoidlab.dylib` and its objects |
| `csrc/` | 1 | the C surface over the vendored Clothoids engine |
| `curve_lab/` | 46 | the Python engine (measure, reduction, grammar, plates maths) |
| `curves/` | 77 | one folder per curve with a picture and notes |
| `docs/` | 54 | the mkdocs book and page twins |
| `engine/` | 1 | `Dockerfile` for the native build |
| `exercises/` | 2 | the closed-clothoid exercise |
| `focus-math/` | 771 | a fetched maths corpus: sources, headers, samples |
| `founder/` | 5 | screenshots and the founder's log |
| `legacy/` | 4 |  |
| `pythagorean-spiral/` | 97 | the exact spine layer |
| `scripts/` | 203 | generators, audits, checks, page builders |
| `state/` | 23 | the working memory: handoff, plan, register, registry |
| `tests/` | 124 | the Python suite (and js/ for the browser modules) |
| `tph_tri_chain/` | 12 | the triangle-chain study |
| `web/` | 6 | the older stdlib server and static pages |
| `workbench/` | 363 | the generated input pages and their JSON data |

## The files that matter most

| `$REPO/…` | what |
|---|---|
| `AGENTS.md` | how to work here |
| `next-fhandoff-int.md` | the one next action |
| `state/HANDOFF-int.md` | current truth (read the tail) |
| `state/PLAN-int.md` | the next few sessions |
| `state/REGRESSIONS-int.md` | fixed faults and their tests |
| `state/DATA-int.md` | every dataset, its format, writer and reader |
| `LTMemory-int.md` | the map and invariants |
| `senior-dev.md` | twelve working rules |
| `docs/TUNNEL.md` | how the phone reaches the app |
| `deep-to-side.md` / `side-to-deep.md` | mail between the sessions |
| `workbench/manifest.json` | every input page, with its purpose |
| `workbench/finder.json` | the curve finder's current results |
| `workbench/starred.json` | the stars saved from the lab |
| `app/src/pages/` | `index.astro` (hub), `lab.astro`, `book.astro`, `finder.astro` |
| `app/src/lib/` | `gallery.js`, `finder.js`, `pages.js`, `stars.js`, `tunnel.js` |
| `curve_lab/reduction.py` | properness and collapse |
| `scripts/curve_finder.py` | writes `workbench/finder.json` |
| `scripts/curvature_power.py` | the power-curve numbers |
