// POST /api/cut-double  { uid, mode, cusp, keep, name, widthPct, plus, minus, profile }
//
// Cut a double-wonk and save the result as a new curve beside its parent. Two cuts:
//
//   mode "dot" (the default)  cut at one of the cusps the plate marks in blue; the long arc is
//                             kept unless keep is "short".
//   mode "top" / "bottom"     cut across the horizontal line through the middle of the curve
//                             as the plate draws it; the runs on one side are kept, each as an
//                             open curve (a tulip has two petals above its line, so a side may
//                             be several runs, stored as branches).
//
// Nothing is overwritten: the parent stays on /plates and the cut lands beside it.

import { readFileSync } from "node:fs";
import path from "node:path";
import { repoRoot } from "../../lib/gallery.js";
import { cuspsOf, cutAt, lineRuns, lineY, turnPoints } from "../../lib/cut-doubles.js";
import { DeskError, createVariant, valuesFrom } from "../../lib/desk-tune.js";

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json" },
});

export const POST = async ({ request }) => {
  try {
    const body = await request.json().catch(() => ({}));
    const uid = String(body.uid || "");
    const keep = body.keep === "short" ? "short" : "long";
    const mode = body.mode === "top" || body.mode === "bottom" ? body.mode : "dot";

    const registry = JSON.parse(
      readFileSync(path.join(repoRoot(), "workbench", "curve-registry.json"), "utf8"));
    const record = registry.curves.find((curve) => curve.uid === uid);
    if (!record) return json({ error: `${uid} is not a curve` }, 404);
    if (!Array.isArray(record.path) || record.path.length < 4) {
      return json({ error: `${uid} has no stored path to cut` }, 422);
    }

    // The side curves are chosen here, before saving: the four values come from the form and
    // fall back to the presets (a zero in a record is the note migration's placeholder, so a
    // parent's zero is not a choice). valuesFrom clamps each to its range.
    const asked = Number(body.cusp);
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

    let cutPath;
    let cutBranches = null;
    let cutInfo;

    if (mode === "dot") {
      const cusps = cuspsOf(record.path);
      const asked = Number(body.cusp);
      const index = Number.isInteger(asked) ? asked : 0;
      const cusp = cusps[index];
      if (!cusp) return json({ error: "this curve has no cusp; there is no dot to cut at" }, 422);
      const cut = cutAt(record.path, cusp.index, keep);
      if (cut.points.length < 3) return json({ error: "that cut leaves too little to draw" }, 422);
      cutPath = cut.points;
      cutInfo = {
        mode, cusp: index, keep,
        points: cut.points.length,
        kept: Number(cut.keptLength.toFixed(3)),
        dropped: Number(cut.droppedLength.toFixed(3)),
      };
    } else {
      // The line runs across the curve as the operator sees it on the plate: the record is
      // turned for the cut, and the kept runs are turned back to the record's own frame.
      const degrees = Number(record.transform?.degrees ?? 0);
      const shown = turnPoints(record.path, degrees);
      const at = lineY(shown);
      const runs = lineRuns(shown, mode, at);
      if (!runs.length) {
        return json({ error: `the line does not leave a ${mode} run to keep` }, 422);
      }
      cutBranches = runs.map((run) => turnPoints(run, -degrees));
      cutPath = cutBranches[0];
      cutInfo = {
        mode, side: mode, runs: runs.length,
        points: cutBranches.reduce((count, run) => count + run.length, 0),
      };
    }

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
          spine: uid, name, values, path: cutPath, branches: cutBranches, cut: cutInfo,
        });
        break;
      } catch (error) {
        lastError = error;
        const collision = error instanceof DeskError && error.status === 409;
        if (askedName || !collision) throw error;
      }
    }
    if (!result) throw lastError || new DeskError("could not name the cut", 400);
    return json({ ...result, cut: { parent: uid, ...cutInfo } });
  } catch (error) {
    const status = error instanceof DeskError ? error.status : 400;
    return json({ error: String(error.message || error) }, status);
  }
};
