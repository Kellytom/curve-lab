// One bordered figure, as its own cacheable file.
//
// The gallery used to inline all 238 drawings into one document: 82 MB of HTML
// that had to be rebuilt and re-sent on every visit. Each figure is now a file
// the browser can keep, and the page asks for it with loading="lazy" so only
// the visible ones travel.
import { createHash } from "node:crypto";
import { buildIlluminations } from "../../lib/bordered.js";

export const prerender = false;

export async function GET({ params, request }) {
  const gallery = await buildIlluminations();
  const item = gallery.byId?.[params.figure];
  if (!item) return new Response("no such figure\n", { status: 404 });

  const etag = `"${createHash("sha1").update(item.svg).digest("base64url")}"`;
  const headers = {
    "content-type": "image/svg+xml; charset=utf-8",
    "cache-control": "public, max-age=604800, stale-while-revalidate=86400",
    etag,
  };
  if (request.headers.get("if-none-match") === etag) {
    return new Response(null, { status: 304, headers });
  }
  return new Response(item.svg, { status: 200, headers });
}
