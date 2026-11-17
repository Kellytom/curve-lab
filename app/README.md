# The Astro app

Astro 5.18 with `@astrojs/node`, on **http://localhost:4321**. The lab page is
ported; its stars are saved by the page itself to `workbench/starred.json`.

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
- **The endpoint:** `POST /api/stars` with `{ "plates": [...] }` wrote
  `workbench/starred.json` in the test run.

```sh
cd app && npm run dev      # http://localhost:4321
npm test                   # the save tests, no browser
```

Not ported yet: the book gallery and the other workbench pages. The old lab at
`:8003` stays until the Astro page reaches parity.
