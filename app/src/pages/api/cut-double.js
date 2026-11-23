// POST /api/cut-double  { uid, cusp, keep, name }
//
// Cut a double-wonk at one of its cusps — the big blue dot on its plate — and keep the long
// arc (or the short one). The cut is saved by the same writer as the tuning desk's "new curve":
// a record with the next uid beside its parent, a database row, and its plate rendered.
//
// Nothing is overwritten: the parent stays on /plates, and the cut lands beside it.

import { readFileSync } from "node:fs";
import path from "node:path";
import { repoRoot } from "../../lib/gallery.js";
import { cuspsOf, cutAt } from "../../lib/cut-doubles.js";
import { DeskError, createVariant } from "../../lib/desk-tune.js";

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json" },
});

export const POST = async ({ request }) => {
  try {
    const body = await request.json().catch(() => ({}));
    const uid = String(body.uid || "");
    const keep = body.keep === "short" ? "short" : "long";

    const registry = JSON.parse(
      readFileSync(path.join(repoRoot(), "workbench", "curve-registry.json"), "utf8"));
    const record = registry.curves.find((curve) => curve.uid === uid);
    if (!record) return json({ error: `${uid} is not a curve` }, 404);
    if (!Array.isArray(record.path) || record.path.length < 4) {
      return json({ error: `${uid} has no stored path to cut` }, 422);
    }

    const cusps = cuspsOf(record.path);
    const asked = Number(body.cusp);
    const index = Number.isInteger(asked) ? asked : 0;
    const cusp = cusps[index];
    if (!cusp) return json({ error: "this curve has no cusp; there is no dot to cut at" }, 422);

    const cut = cutAt(record.path, cusp.index, keep);
    if (cut.points.length < 3) return json({ error: "that cut leaves too little to draw" }, 422);

    // A zero in a record is the note migration's placeholder, not a choice (the plate's row
    // rule treats it the same way), so a cut falls back to the presets instead of drawing a
    // spine-only plate at width 0.
    const real = (value, fallback) => {
      const number = Number(value);
      return Number.isFinite(number) && number !== 0 ? number : fallback;
    };
    const values = {
      widthPct: real(record.widthPct, 1.5),
      plus: real(record.plus, 2.5),
      minus: real(record.minus, 0.1),
      profile: record.profile || "bow",
      transform: { degrees: Number(record.transform?.degrees ?? 0) },
    };

    const askedName = String(body.name || "").trim();
    const base = askedName || `${record.name}-cut`;
    // Cutting several dots of one curve is the normal use; the default name takes the next
    // free number instead of refusing the second cut. A name the operator typed is honoured
    // and its collision is reported.
    let result = null;
    let lastError = null;
    for (let attempt = 1; attempt <= 9; attempt += 1) {
      const name = attempt === 1 ? base : `${base}-${attempt}`;
      try {
        result = await createVariant({
          spine: uid, name, values, path: cut.points, cut: { cusp: index, keep },
        });
        break;
      } catch (error) {
        lastError = error;
        const collision = error instanceof DeskError && error.status === 409;
        if (askedName || !collision) throw error;
      }
    }
    if (!result) throw lastError || new DeskError("could not name the cut", 400);
    return json({
      ...result,
      cut: {
        parent: uid, cusp: index, keep,
        points: cut.points.length,
        kept: Number(cut.keptLength.toFixed(3)),
        dropped: Number(cut.droppedLength.toFixed(3)),
      },
    });
  } catch (error) {
    const status = error instanceof DeskError ? error.status : 400;
    return json({ error: String(error.message || error) }, status);
  }
};
