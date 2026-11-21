// GET /api/curve/<uid> — one curve's drawing data, for the live tuning lab.
//
// Only the three things a drawing needs travel: the two speed rows and, for a curve
// stored as a path, its points. The rest of the registry stays on the server.

import { readFile } from "node:fs/promises";
import path from "node:path";
import { repoRoot } from "../../../lib/gallery.js";

const UID = /^[a-z0-9-]{1,40}$/;

export const GET = async ({ params }) => {
  const uid = params.uid || "";
  if (!UID.test(uid)) return new Response("bad uid\n", { status: 400 });

  const file = path.join(repoRoot(), "workbench", "curve-registry.json");
  const registry = JSON.parse(await readFile(file, "utf8"));
  const record = (registry.curves || []).find((row) => row.uid === uid);
  if (!record) return new Response("no such curve\n", { status: 404 });

  return new Response(JSON.stringify({
    uid: record.uid,
    name: record.name,
    speedX: record.speedX || [],
    speedY: record.speedY || [],
    path: record.path || null,
  }), {
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
};
