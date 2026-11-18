// GET /workbench/<file> — figures and other assets the generated workbench pages
// reference by absolute path (/workbench/figures/x.png). The pages themselves are
// served at /pages/<file>; this route exists so their images resolve in the app.

import { readFile } from "node:fs/promises";
import path from "node:path";
import { repoRoot } from "../../lib/gallery.js";

const TYPES = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".svg": "image/svg+xml",
  ".json": "application/json; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
};

export const GET = async ({ params }) => {
  const relative = String(params.file || "");
  const dir = path.join(repoRoot(), "workbench");
  const file = path.resolve(dir, relative);
  if (!relative || (file !== dir && !file.startsWith(dir + path.sep))) {
    return new Response("bad path\n", { status: 400 });
  }
  try {
    const bytes = await readFile(file);
    return new Response(bytes, {
      status: 200,
      headers: {
        "content-type": TYPES[path.extname(file).toLowerCase()] || "application/octet-stream",
        "cache-control": "no-store",
      },
    });
  } catch {
    return new Response("no such workbench file\n", { status: 404 });
  }
};
