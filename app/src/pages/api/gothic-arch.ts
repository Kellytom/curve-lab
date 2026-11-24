// POST /api/gothic-arch  { uid, q | share, name, force }
//
// Cut the middle out of a mirrored curve and save the two arms joined at the cut, as a new curve
// beside its parent. The parent is never changed; the new record is a variant with the next uid.
//
// The maths is app/src/lib/gothic.ts (the same file the page draws with), and the write is the
// tuning desk's createVariant, so the registry, the database rows, the exports and the plate
// all happen in one place.

import type { APIRoute } from "astro";
import { readFileSync } from "node:fs";
import path from "node:path";
import { repoRoot } from "../../lib/gallery.js";
import { bestAxis, characterOf, cutArch, asFraction, MIRROR_GAP_LIMIT,
  type Point, type RecordLike } from "../../lib/gothic.ts";
import { pointsOf, type CurveLike } from "../../lib/curve-points.ts";
import { DeskError, createVariant } from "../../lib/desk-tune.js";

// the JS writer's inferred parameter types are narrower than its actual contract
const writeVariant = createVariant as unknown as (options: {
  spine: string;
  name: string;
  values: unknown;
  path: Point[];
  cut: Record<string, unknown>;
}) => Promise<{ uid: string; name: string }>;

type Registry = { curves: Array<CurveLike & { uid: string; name?: string }> };
type SaveBody = {
  uid?: unknown;
  q?: unknown;
  share?: unknown;
  force?: unknown;
  name?: unknown;
};

const json = (body: unknown, status = 200): Response => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json" },
});

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = (await request.json().catch(() => ({}))) as SaveBody;
    const uid = String(body.uid || "");
    const registry = JSON.parse(
      readFileSync(path.join(repoRoot(), "workbench", "curve-registry.json"), "utf8")) as Registry;
    const record = registry.curves.find((curve) => curve.uid === uid);
    if (!record) return json({ error: `${uid} is not a curve` }, 404);

    // A path record uses its own points; a rows record is sampled from its speed polynomials
    // with the plate's own sampler, so the arch and the plate cannot disagree.
    const points = pointsOf(record);
    if (!points || points.length < 12) {
      return json({ error: `${uid} has no stored path or speed rows to cut` }, 422);
    }
    const axis = bestAxis(points);
    if (!axis) return json({ error: `${uid} has too few points to measure a mirror` }, 422);
    const force = body.force === true;
    if (axis.gap > MIRROR_GAP_LIMIT && !force) {
      const gap = `${(axis.gap * 100).toFixed(2)} %`;
      return json({
        error: `${uid} has no mirror within 0.5 % of its size (best ${gap}); ` +
          "send force to cut one arm and mirror it",
      }, 422);
    }

    const askedQ = body.q === undefined || body.q === null || body.q === ""
      ? null : Number(body.q);
    const arch = cutArch(points, { q: askedQ, share: Number(body.share), axis, force });
    if (!arch) return json({ error: "that cut leaves too little to draw" }, 422);

    // the character values are the parent's; a zero is the note migration's placeholder
    const values = { ...characterOf(record as RecordLike), transform: { degrees: arch.degrees } };
    const askedName = String(body.name || "").trim();
    const base = askedName || `${record.name}-gothic`;
    // Cutting several arches from one parent is the normal use; an automatic name takes the next
    // free number, while a name the operator typed is honoured and its collision is reported.
    let result: { uid: string; name: string } | null = null;
    let lastError: unknown = null;
    for (let attempt = 1; attempt <= 9; attempt += 1) {
      const name = attempt === 1 ? base : `${base}-${attempt}`;
      try {
        result = await writeVariant({
          spine: uid, name, values, path: arch.path,
          cut: { mode: "gothic", share: arch.share, axis: arch.axis,
                 apexAngle: arch.apexAngle, q: arch.q, t: arch.t,
                 tRequested: arch.tRequested,
                 tLabel: `${asFraction(arch.t[0])} … ${asFraction(arch.t[1])}`,
                 mirrored: arch.mirrored, gap: arch.gap,
                 sampled: !Array.isArray(record.path) },
        });
        break;
      } catch (error) {
        lastError = error;
        const collision = error instanceof DeskError && error.status === 409;
        if (askedName || !collision) throw error;
      }
    }
    if (!result) throw lastError || new DeskError("could not name the arch", 400);
    return json({
      ...result,
      cut: { parent: uid, share: arch.share, axis: arch.axis, apexAngle: arch.apexAngle },
    });
  } catch (error) {
    const status = error instanceof DeskError ? error.status : 400;
    return json({ error: String(error instanceof Error ? error.message : error) }, status);
  }
};
