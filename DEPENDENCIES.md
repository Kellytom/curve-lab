# Dependencies

> **draft A** — a working draft, not a final text.

What this project uses, why it uses it, and what it deliberately does not use.
Every pin is in `requirements.txt`, `requirements-dev.txt` or
`app/package.json`; this page explains them.

## What you need to run it

| layer | needs | install |
|---|---|---|
| the engine | Python 3.12 and `numpy` | `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` |
| the engine's C surface | a C++17 compiler | `bash scripts/build-native.sh` |
| the lab pages | Python and `numpy` | `.venv/bin/python scripts/serve.py` |
| the prose book | `markdown`, `mkdocs`, `mkdocs-material` | `.venv/bin/pip install -r requirements-dev.txt` |
| the Astro app | Node 22 and npm | `npm --prefix app install` |

The engine and the lab need no Node. The app needs no Python. The book needs
neither the compiler nor Node.

## Python

| package | version | licence | why |
|---|---|---|---|
| Python | 3.12 | PSF-2.0 | runs the engine, the scripts and the tests |
| `numpy` | 2.5.4 | BSD-3-Clause | numeric work in `curve_lab/nodes.py` and the finder scripts |
| `markdown` | 3.11.2 | BSD-3-Clause | builds the HTML twins of two docs pages |
| `mkdocs` | 1.6.1 | BSD-2-Clause | builds the prose book |
| `mkdocs-material` | 9.8.0 | MIT | the book's theme |
| `pyclothoids` | 0.2.0 | MIT | optional: the prebuilt wheel, a second opinion on the C wrapper, and a fallback when no compiler is available |

`pyclothoids` carries the same engine as the vendored source, so it agrees on
the mathematics by construction. It is not an independent check of the maths,
only of the wrapper.

## C++, vendored

These live in `vendor/` and are compiled by `scripts/build-native.sh`. They are
not fetched at build time.

| library | licence | why |
|---|---|---|
| Clothoids (Bertolazzi and Frego) | BSD-2-Clause | Euler-curve evaluation, exact offsets, the G1 fitter, trim, projection, intersection |
| Eigen | MPL-2.0 | header-only linear algebra, reached through UtilsLite; not called directly here |
| GenericContainer, UtilsLite, quarticRootsFlocke | permissive; see `ATTRIBUTION.md` | included by Clothoids |

## JavaScript, in the app

| package | version | licence | why |
|---|---|---|---|
| Node | 22 | MIT | runs the Astro app and the page checks |
| `astro` | 5.18.2 | MIT | the app and its pages, server-rendered |
| `@astrojs/node` | 9.5.5 | MIT | the Node adapter that runs Astro as a server |
| `zod` | 3.25.76 | MIT | validates the payload the save route receives |
| Pico CSS | vendored 2.x | MIT | the app's stylesheet, kept as one file, no build step |

## What is deliberately not a dependency

- **No front-end framework.** No React, Vue, Svelte or bundler. The lab pages are
  plain HTML with small scripts; the app is Astro.
- **No path library.** Writing `M` and `C` is a formatting job, not a package.
- **No server framework.** The Python server is the standard library's HTTP
  server; the app is Astro's own.
- **No test runner beyond the standard ones.** `unittest` in Python, `node:test`
  in JavaScript.
- **No ORM and no database.** The data is JSON files with a declared `format`
  field, read through one loader.
- **No auth library.** The server's shared-token gate is a few lines of
  `hmac.compare_digest` and Basic auth.

## What "pinned" means here

Exact versions are pinned for the tools that change behaviour: `numpy` and
`markdown` in `requirements.txt`, the app packages in `package.json`. A pin is
changed on purpose, in its own commit, with the tests run afterwards.

The one exception is `vendor/Clothoids`, which is a source tree, not a package.
Its version is the commit recorded in the submodule.

## Check it

```sh
.venv/bin/pip install -r requirements.txt       # the engine
.venv/bin/pip install -r requirements-dev.txt   # the book and the wheel
npm --prefix app install                        # the app
.venv/bin/python scripts/test.py --slim          # does the engine still work
```
