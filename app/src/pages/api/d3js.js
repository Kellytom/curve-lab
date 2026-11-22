// Serve the installed d3 UMD bundle to a workbench page.
//
// The sandbox pages are static files outside app/, so Vite does not bundle their imports.
// This route hands them the same d3 the app already carries; nothing is copied or vendored.

import { readFile } from "node:fs/promises";
import path from "node:path";
import { repoRoot } from "../../lib/gallery.js";

export const GET = async () => {
  const file = path.join(repoRoot(), "app", "node_modules", "d3", "dist", "d3.min.js");
  const bytes = await readFile(file);
  return new Response(bytes, {
    headers: {
      "content-type": "text/javascript; charset=utf-8",
      "cache-control": "no-cache",
    },
  });
};
