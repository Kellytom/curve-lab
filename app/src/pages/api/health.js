// GET /api/health — who is actually serving. A 200 is not enough: after an
// upgrade an old daemon can still hold the port, and /fhandon must not reuse it.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
const astro = (() => {
  try { return require("astro/package.json").version; } catch {
    const pkg = JSON.parse(readFileSync(path.join(process.cwd(), "package.json"), "utf8"));
    return pkg.dependencies?.astro || "unknown";
  }
})();

export const GET = async () =>
  new Response(JSON.stringify({
    ok: true,
    app: "curve-lab",
    node: process.version,
    astro,
  }), { status: 200, headers: { "content-type": "application/json" } });
