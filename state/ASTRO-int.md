# ASTRO-int — the app, and what moves into it

Settled 2026-11-17, by the operator: **Astro is the app.** "The final result
will be in astro.js anyway"; no React; local file support; it must work on
Next and other servers too. `docs/web.md` is the older stack note (Svelte/WASM,
no server); this file supersedes its UI choice, not its engine plan.

## What is running

- `app/` — Astro **5.18.2** with `@astrojs/node` **9.5.5**, at **:4321**.
- **Why 5.18:** the machine's Node is **22.4.1**; Astro 7 requires >=22.23.4 and
  refused to start. Astro 5 accepts >=22.0. A **global Astro 5.18.2** is
  installed; the old `~/developer/grid-8` project is on 4.15 (legacy).
- **One copy of the maths and data:** the page imports `workbench/plate_math.js`
  (`?url`, classic script) and `workbench/real-curves.json`; Vite is allowed the
  repo root. Nothing is copied into `app/`.
- **The save is the point:** `app/src/lib/stars.js` writes
  `workbench/starred.json` atomically, after validating every id; the Astro
  route `app/src/pages/api/stars.js` is a thin adapter. The library is plain
  Node and has no Astro import, so a Next route or a Hono route calls the same
  function. The lab's "save to workbench" button posts to `/api/stars`; the
  download remains as the fallback.
- **Tested:** `app/tests/stars.test.mjs` (4 tests) and a browser run: 88 cards,
  star pressed, save pressed, `workbench/starred.json` written and read back.

## The migration order

1. **The lab** — landed: page, star, save, the 88-card picker.
2. **The book gallery** — next: port `book/index.html` to an Astro page that
   lists the star file and the simple designs, then retire the generated page.
3. **The other workbench pages** — one at a time, on touch: the page moves to
   `app/src/pages/`, its generator stops writing HTML, and the shared JS stays
   the one implementation. The old page is deleted in the same commit.
4. **The Python engine** — keep it. The exact core and the spline connector
   stay in `curve_lab`; expose them through one Node bridge (a whitelisted
   `child_process` call or an API route) rather than porting the exact maths
   again. The JS exact core (`exact.js`, `ph_offset.js`) covers what the page
   must compute live.
5. **Deploy** — the Node adapter runs the same app on a normal server; static
   pages and the API travel together. Local files are a dev/desktop feature; a
   hosted instance would write to its own storage, not the repo.

## Tooling (offline, 2026-11-17)

- **zod** is the one runtime addition: the star payload is parsed against a
  schema before the write; a missing plate, a bad id or a duplicate fails the
  request.
- `@astrojs/check`/`typescript` and `prettier`/`prettier-plugin-astro` were
  tried and removed. The checker throws `ERR_REQUIRE_ESM` from
  `@astrojs/language-server` on this install; the Astro Prettier plugin cannot
  find its native binding. Both need a fresh install with the network, which is
  off by the operator's instruction (2026-11-17). `npm run build` and
  `npm test` are the gate in the meantime.
- **No more network.** Installs, fetches and registry probes stop here; the
  global Astro 5.18.2 and `app/node_modules` are the fixed kit.

## Rules

- One implementation: the Astro page uses the same `plate_math.js`; do not fork
  the maths into `app/src`.
- The save validates before it writes, and writes via a temp file and rename: a
  failed read must never become an empty list (the 2026-11-16 fault).
- `CURVE_LAB_ROOT` points the app at the repo root; the dev script sets it to
  `..`. A hosted deployment sets it to its own data directory.
- Node is a tool, not a second build system: no bundler beyond what Astro
  already is.

## Commands

```sh
cd app && npm run dev      # http://localhost:4321
npm --prefix app test      # the save tests
astro --version            # the one global Astro (5.18.2)
```
