// GET /api/plate-math.js — the one plate maths, served as a plain script.
//
// workbench/plate_math.js loads either as a global script (globalThis.PlateMath) or
// through require, and it lives at the repo root, outside app/. It is served here rather
// than copied into public/, so there is exactly one implementation behind the printed
// plate, the per-curve page and the live lab.

import { readFile } from "node:fs/promises";
import path from "node:path";
import { repoRoot } from "../../lib/gallery.js";

export const GET = async () => {
  const bytes = await readFile(path.join(repoRoot(), "workbench", "plate_math.js"));
  return new Response(bytes, {
    headers: {
      "content-type": "text/javascript; charset=utf-8",
      "cache-control": "no-cache",
    },
  });
};
