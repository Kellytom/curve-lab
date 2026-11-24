// POST /api/trim-curve  { uid, from, to, name, widthPct, plus, minus, profile }
//
// Cut a curve's legs off at two rational fractions of its parameter. `from` and `to` are
// fractions written as text ("1/4", "3/4"); t = 0 is the first station, t = 1 the last. The
// stations between them are kept, the legs outside are dropped, and the two cut points sit
// exactly on the fractions. The result is a new record beside its parent; nothing is overwritten.
//
// The operator, 2026-11-24: "cutting the legs off the curves using rational fractions of t".

import { readFileSync } from "node:fs";
import path from "node:path";
import { repoRoot } from "../../lib/gallery.js";
import { parseRange, trimRecord } from "../../lib/trim-curve.js";
import { DeskError, createVariant, valuesFrom } from "../../lib/desk-tune.js";

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json" },
});

export const POST = async ({ request }) => {
  try {
    const body = await request.json().catch(() => ({}));
    const uid = String(body.uid || "");
    const registry = JSON.parse(
      readFileSync(path.join(repoRoot(), "workbench", "curve-registry.json"), "utf8"));
    const record = registry.curves.find((curve) => curve.uid === uid);
    if (!record) return json({ error: `${uid} is not a curve` }, 404);
    if (!Array.isArray(record.path) || record.path.length < 2) {
      return json({ error: `${uid} has no stored path to trim` }, 422);
    }

    let range;
    try {
      range = parseRange(body.from, body.to);
    } catch (error) {
      return json({ error: String(error.message || error) }, 422);
    }
    const trimmed = trimRecord(record, range.from, range.to);
    if (!trimmed || trimmed.path.length < 3) {
      return json({ error: "that cut leaves too little to draw" }, 422);
    }

    const real = (value, fallback) => {
      const number = Number(value);
      return Number.isFinite(number) && number !== 0 ? number : fallback;
    };
    const values = valuesFrom({
      widthPct: body.widthPct, plus: body.plus, minus: body.minus, profile: body.profile,
      degrees: body.degrees,
    }, {
      widthPct: real(record.widthPct, 1.5),
      plus: real(record.plus, 2.5),
      minus: real(record.minus, 0.1),
      profile: record.profile || "bow",
      degrees: Number(record.transform?.degrees ?? 0),
    });

    const defaultName = `${record.name}-trimmed`;
    const askedName = String(body.name || "").trim();
    const autoNumber = !askedName || askedName === defaultName
      || askedName.startsWith(`${defaultName}-`);
    const base = askedName || defaultName;
    const cut = { mode: "trim", of: record.uid, ofName: record.name,
                  from: range.from.text, to: range.to.text, sampled: true };

    let result = null;
    let lastError = null;
    for (let attempt = 1; attempt <= 9; attempt += 1) {
      const name = attempt === 1 ? base : `${base}-${attempt}`;
      try {
        result = await createVariant({
          spine: uid, name, values,
          path: trimmed.branches[0],
          branches: trimmed.branches.length > 1 ? trimmed.branches : null,
          cut,
        });
        break;
      } catch (error) {
        lastError = error;
        const collision = error instanceof DeskError && error.status === 409;
        if (!autoNumber || !collision) throw error;
      }
    }
    if (!result) throw lastError || new DeskError("could not name the cut", 400);

    return json({
      ...result,
      trim: {
        parent: uid, from: range.from.text, to: range.to.text,
        keptStations: trimmed.keptStations, droppedStations: trimmed.droppedStations,
        branches: trimmed.branches.length,
      },
    });
  } catch (error) {
    const status = error instanceof DeskError ? error.status : 400;
    return json({ error: String(error.message || error) }, status);
  }
};
