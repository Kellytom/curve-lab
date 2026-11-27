// GET /api/plate/<id> — one exported book plate, as PNG bytes.
//
// The plates live in book/old-plates/ at the repo root, outside the app, so they are
// read from disk rather than copied into public/. The id is checked against the
// plate-name pattern before it reaches the filesystem, and the resolved path
// must stay inside book/old-plates/.

import { readFile } from "node:fs/promises";
import path from "node:path";
import { repoRoot, PLATE_ID } from "../../../lib/gallery.js";

const PLATE_DIR = "book/old-plates";

export const GET = async ({ params }) => {
  const id = params.id;
  if (!PLATE_ID.test(id || "")) {
    return new Response("bad plate id\n", { status: 400 });
  }
  const dir = path.join(repoRoot(), PLATE_DIR);
  const file = path.resolve(dir, `${id}.png`);
  if (path.dirname(file) !== path.resolve(dir)) {
    return new Response("bad plate id\n", { status: 400 });
  }
  try {
    const bytes = await readFile(file);
    return new Response(bytes, {
      status: 200,
      headers: {
        "content-type": "image/png",
        "cache-control": "public, max-age=60",
      },
    });
  } catch {
    return new Response("plate not exported yet\n", { status: 404 });
  }
};
