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

- **Why 5.18, not 7:** this machine's Node is 22.4.1; Astro 7 needs >=22.23.4.
  Astro 5 supports >=22.0. A **global Astro 5.18.2** is installed; Astro still
  needs the adapter (`@astrojs/node`) local to each project, so the shared thing
  is the version and the CLI, not one `node_modules` for every folder.
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
- **The endpoint:** `POST /api/stars` with `{ "plates": [...] }` wrote
  `workbench/starred.json` in the test run.

```sh
cd app && npm run dev      # http://localhost:4321
npm test                   # the save tests, no browser
```

Not ported yet: the other workbench pages (the hub previews them from the
Python-generated files). The old lab at
`:8003` stays until the Astro page reaches parity.
