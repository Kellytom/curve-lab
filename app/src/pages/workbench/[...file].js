// GET /workbench/<file> — the working pages, served from workbench/ at the repo root.
//
// The pages there are hand-built working views (adder, wobble, the sandboxes). They live
// outside app/, so they are read from disk rather than copied into public/: one copy, and a
// rebuild of a working page shows up here at once. Their /vendor/ links already resolve,
// because app/public/vendor is served at the site root.

import { readFile } from "node:fs/promises";
import path from "node:path";
import { repoRoot } from "../../lib/gallery.js";

// only the things a working page loads; nothing executable from outside this list
const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".woff2": "font/woff2",
};

const SAFE = /^[a-zA-Z0-9._/-]+$/;

export const GET = async ({ params }) => {
  const rest = params.file || "";
  const type = TYPES[path.extname(rest).toLowerCase()];
  if (!type || !SAFE.test(rest) || rest.includes("..")) {
    return new Response("not served\n", { status: 404 });
  }

  const root = path.join(repoRoot(), "workbench");
  const file = path.resolve(root, rest);
  if (file !== root && !file.startsWith(root + path.sep)) {
    return new Response("not served\n", { status: 404 });
  }

  try {
    const bytes = await readFile(file);
    return new Response(bytes, {
      headers: { "content-type": type, "cache-control": "no-store" },
    });
  } catch {
    return new Response("not found\n", { status: 404 });
  }
};
