// POST /api/curve-stars — store a curve's star rating (0 = none, 1..10).
//
// The rating is the note's `importance`, the value every page reads through
// loadRegistry. It is one transaction and then the JSON copy; a bad uid or rating
// is refused before a row is written.

import { z } from "zod";
import { prisma } from "../../lib/db.js";
import { exportTable } from "../../lib/data-export.js";

const Uid = z.string().regex(/^[a-z0-9-]+$/).max(40);
const Payload = z.object({
  uid: Uid.optional(),
  uids: z.array(Uid).min(1).max(400).optional(),
  stars: z.number().int().min(0).max(10),
}).refine((value) => value.uid || value.uids?.length, { message: "give uid or uids" });

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json" },
});

export const POST = async ({ request }) => {
  try {
    const payload = Payload.parse(await request.json());
    const list = payload.uids || [payload.uid];
    const stars = payload.stars;
    const notes = await prisma.note.findMany({ where: { uid: { in: list } }, select: { uid: true } });
    const known = new Set(notes.map((note) => note.uid));
    const missing = list.filter((uid) => !known.has(uid));
    if (missing.length) {
      return json({ error: `no note to rate for ${missing.slice(0, 5).join(", ")}`, missing }, 404);
    }
    const result = await prisma.note.updateMany({ where: { uid: { in: list } }, data: { importance: stars } });
    let warning;
    try {
      await exportTable("curves");
    } catch (error) {
      warning = `stars saved, but the JSON copy is stale: ${String(error.message || error)}`;
    }
    return json({ uids: list, stars, updated: result.count, ...(warning ? { warning } : {}) });
  } catch (error) {
    return json({ error: String(error.message || error) }, 400);
  }
};
