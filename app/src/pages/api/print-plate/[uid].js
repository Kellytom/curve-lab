// GET /api/print-plate/<uid>?format=svg|png
//
// The 300 dpi print plate for one curve, served from book/print. The uid is checked against
// a strict pattern before any path is built, so the route cannot read outside the folder.

import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { repoRoot } from "../../../lib/gallery.js";

const UID = /^c-\d{4}$/;

export const GET = async ({ params, url }) => {
  const uid = String(params.uid || "");
  if (!UID.test(uid)) return new Response("no such curve", { status: 404 });
  const format = url.searchParams.get("format") === "svg" ? "svg" : "png";
  const file = path.join(repoRoot(), "book", "print", `${uid}.${format}`);
  if (!existsSync(file)) return new Response("plate not exported yet", { status: 404 });
  return new Response(readFileSync(file), {
    headers: {
      "content-type": format === "svg" ? "image/svg+xml" : "image/png",
      "cache-control": "public, max-age=600",
    },
  });
};
