// GET /api/print-plate/<uid>?format=svg|png
//
// The 300 dpi print plate for one curve, served from book/print. The uid is checked against
// a strict pattern before any path is built, so the route cannot read outside the folder.

import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { repoRoot } from "../../../lib/gallery.js";

const UID = /^[a-z0-9-]+$/;

export const GET = async ({ params, url }) => {
  const uid = String(params.uid || "");
  if (!UID.test(uid)) return new Response("no such curve", { status: 404 });
  const format = url.searchParams.get("format") === "svg" ? "svg" : "png";
  // the name carries the size and the tone; the svg is vector and has no size in its name
  const candidates = format === "svg"
    ? [`${uid}.svg`]
    : [`${uid}-3000-grey-300dpi.png`, `${uid}.png`];
  const file = candidates.map((name) => path.join(repoRoot(), "book", "print", name))
    .find((candidate) => existsSync(candidate));
  if (!file) return new Response("plate not exported yet", { status: 404 });
  return new Response(readFileSync(file), {
    headers: {
      "content-type": format === "svg" ? "image/svg+xml" : "image/png",
      // the SVG is the live plate; a reload must show the current law, not a ten-minute old copy
      "cache-control": format === "svg" ? "no-cache" : "public, max-age=600",
    },
  });
};
