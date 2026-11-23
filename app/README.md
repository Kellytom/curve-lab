# The Astro app

Astro 5.18 with `@astrojs/node`, on **http://localhost:4321**.

- **`/` is the hub:** every page the app will use, live in one scroll — the lab
  and the book gallery first, then the 86 workbench pages by intent, then any
  workbench HTML the manifest does not name. The shell is an admin-dashboard
  layout (fixed sidebar, top bar, card grid); the colours and type are
  curve-lab's own. `src/lib/pages.js` builds the list from
  `../workbench/manifest.json` plus the files on disk.
- **Workbench pages are served, not copied:** `src/pages/pages/[...file].js`
  reads `../workbench/<file>` (with a path check) so a preview is always the
  current generated page.
- **Shell credit:** the hub's layout — fixed sidebar, top bar, card grid — follows
  the Flowbite Astro admin dashboard (MIT, Bergside). No Tailwind, Flowbite or
  template code is used; the CSS here is ours.
- **`/lab` is the lab; `/book` is the book gallery.** The lab page is ported; its
  stars are saved by the page itself to `workbench/starred.json`.

- **The stack now:** Astro **7.4.13** on Node **24** (`~/node24/bin`); `/api/health`
  reports both. Astro 5 needed this machine's older Node 22; that constraint is gone.
- **Shared code:** `../workbench/plate_math.js` and `../workbench/real-curves.json`
  through Vite's `server.fs.allow`; one copy of the maths and the data.
- **The design is remembered:** the lab writes its controls to
  `localStorage` (`square-lab-state`) on every change and restores them on load,
  so reopening the tab returns the design on screen, not just the page.
- **The save:** `src/lib/stars.js` is plain Node (atomic write, validated ids);
  `src/pages/api/stars.js` is a thin adapter. A Next route handler or a Hono
  route can import the same function.
- **The book gallery:** `/book` (`src/pages/book.astro`) lists the starred
  plates from `../workbench/starred.json`, then the cross and leaf from
  `../book/plates.json`, then the singles. `src/lib/gallery.js` reads both files
  on every request and takes each caption from `../workbench/plate_compose.js`,
  the same call the exporter makes. The PNGs are served by
  `src/pages/api/plate/[id].js` from `../book/plates/`, so nothing is copied.
  The generated `book/index.html` is gone.
- **The database:** `npx prisma db push` after a schema change. `node
  scripts/migrate.mjs` seeds an **empty** database from `workbench/curve-registry.json`
  and does nothing when rows exist; the additive path is
  `node scripts/add-registry-curves.mjs` (insert the registry curves the database is
  missing — used after `scripts/add_classical.py`). `node scripts/check-db.mjs` prints
  the expected counts and compares them. Snapshots: `npm run backup`, `npm run restore`.
- **The endpoint:** `POST /api/stars` with `{ "plates": [...] }` wrote
  `workbench/starred.json` in the test run.

```sh
cd app && npm run dev      # http://localhost:4321
npm test                   # the save tests, no browser
```

**After a Prisma schema change**, restart the dev server. The running process
keeps the client it loaded at start, so a new model or field is `undefined`
until the restart. Run `cd app && npx prisma db push`, then restart `npm run dev`.

Not ported yet: the other workbench pages (the hub previews them from the
Python-generated files). The old lab at
`:8003` stays until the Astro page reaches parity.
