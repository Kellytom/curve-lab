// Desk io for the tuning pages.
//
// One record is one curve, with a uid. A tuning row holds the four values for that uid.
// "Save" writes the row. "Save as a new curve" makes a new record beside its parent —
// uid c-0002a, the name the operator typed — copies the spine's geometry, and renders its
// plate, so it appears on /plates next to the curve it came from.
//
// The rules live in pure functions (planOverwrite, planVariant) so they can be tested
// without a database. createVariant writes the registry seed, the database, the desk row
// and the plate, in that order, and rolls the seed back if a later step fails.

import { execFile } from "node:child_process";
import { copyFileSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import path from "node:path";
import { promisify } from "node:util";
import { prisma } from "./db.js";
import { exportTable } from "./data-export.js";

const run = promisify(execFile);
const ROOT = path.resolve(import.meta.dirname, "..", "..", "..");
const REGISTRY = path.join(ROOT, "workbench", "curve-registry.json");
const BACKUP = path.join(ROOT, "state", "backups", "curve-registry.backup.json");

export const PROFILES = ["bow", "s", "taper"];
export const VALUES = { widthPct: [0.5, 20, 6], plus: [-8, 8, 2], minus: [-8, 8, 2],
                        degrees: [-360, 360, 0] };

export class DeskError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}

const parsed = (row) => {
  try { return JSON.parse(row.data) || {}; } catch { return null; }
};

const clamp = (raw, fallback, [low, high, usual]) => {
  const value = Number(raw ?? fallback);
  return Number.isFinite(value) ? Math.min(high, Math.max(low, value)) : usual;
};

// the four values and the turn, in the shape a row stores them
export function valuesFrom(raw, fallback = {}) {
  const profile = PROFILES.includes(raw.profile) ? raw.profile
    : PROFILES.includes(fallback.profile) ? fallback.profile : "bow";
  return {
    widthPct: clamp(raw.widthPct, fallback.widthPct, VALUES.widthPct),
    plus: clamp(raw.plus, fallback.plus, VALUES.plus),
    minus: clamp(raw.minus, fallback.minus, VALUES.minus),
    profile,
    transform: { degrees: clamp(raw.degrees, fallback.transform?.degrees ?? fallback.degrees,
                                VALUES.degrees) },
  };
}

export function registryUids(root = ROOT) {
  const seed = JSON.parse(readFileSync(path.join(root, "workbench", "curve-registry.json"), "utf8"));
  return new Set(seed.curves.map((curve) => curve.uid));
}

// a curve name is also a path component: "Euler Hook Thin" -> "euler-hook-thin"
export function safeCurveName(name) {
  return String(name || "")
    .replace(/(\d+)\s*\/\s*(\d+)/g, "$1of$2")
    .toLowerCase().replace(/_/g, "-").replace(/\s+/g, "-")
    .replace(/[^a-z0-9.-]+/g, "-").replace(/-+/g, "-").replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

// 0 -> a, 25 -> z, 26 -> aa
const letters = (index) => {
  let n = index + 1;
  let out = "";
  while (n > 0) {
    n -= 1;
    out = String.fromCharCode(97 + (n % 26)) + out;
    n = Math.floor(n / 26);
  }
  return out;
};

export function variantUid(baseUid, taken) {
  for (let i = 0; i < 702; i += 1) {
    const uid = `${baseUid}${letters(i)}`;
    if (!taken.has(uid)) return uid;
  }
  throw new DeskError(`every suffix on ${baseUid} is used`, 409);
}

// Save (overwrite) one tuning row. Keeps every field the tune does not own.
export function planOverwrite({ rows, uids, mode = "overwrite", rowId, spine, values }) {
  const base = String(spine || rowId || "").trim();
  if (!uids.has(base)) return { ok: false, status: 400, error: `${base || "(no id)"} is not a curve id` };
  if (mode !== "overwrite") return { ok: false, status: 400, error: `unknown mode "${mode}"` };

  const id = String(rowId || base).trim();
  if (!uids.has(id)) return { ok: false, status: 404, error: `curve "${id}" no longer exists` };
  const owner = rows.find((row) => row.name === id);
  const previous = owner ? (parsed(owner) || {}) : {};
  const data = { ...previous, ...values, spine: previous.spine || base, tune: true };
  return { ok: true, created: !owner, name: id, data };
}

// A new curve beside its parent. The parent's own parent is the spine, so a variant of a
// variant still lands in the c-0002a, c-0002b series.
export function planVariant({ curves, baseUid, name, values, deskNames = [], deskIds = [] }) {
  const base = curves.find((curve) => curve.uid === baseUid);
  if (!base) return { ok: false, status: 400, error: `${baseUid || "(no id)"} is not a curve id` };
  const root = String(base.params?.variantOf || base.uid);

  const chosen = safeCurveName(name);
  if (!chosen) return { ok: false, status: 400, error: "a new curve needs a name" };

  const takenNames = new Map();
  for (const curve of curves) {
    for (const label of [curve.name, ...(curve.aliases || [])]) {
      const key = String(label || "").trim().toLowerCase();
      if (key && !takenNames.has(key)) takenNames.set(key, curve);
    }
  }
  for (const label of deskNames) {
    const key = String(label || "").trim().toLowerCase();
    if (key && !takenNames.has(key)) takenNames.set(key, null);
  }
  const owner = takenNames.get(chosen.toLowerCase());
  if (owner !== undefined) {
    const where = owner ? `${owner.uid} (${owner.name})` : "a desk row";
    return { ok: false, status: 409, error: `name "${chosen}" is already used by ${where}` };
  }
  if (curves.some((curve) => curve.uid === chosen)) {
    return { ok: false, status: 409, error: `"${chosen}" is a curve id; choose another name` };
  }

  // a desk row may hold a uid that never became a record; never take its name either
  const uid = variantUid(root, new Set([...curves.map((curve) => curve.uid), ...deskIds]));
  const record = {
    ...JSON.parse(JSON.stringify(base)),
    uid,
    name: chosen,
    aliases: [],
    lists: [...new Set([...(base.lists || []), "variant"])],
    source: "variant",
    family: base.family,
    family_id: base.family_id || base.family,
    variant: chosen,
    auto_named: false,
    starred: false,
    candidate: false,
    importance: 0,
    widthPct: values.widthPct,
    plus: values.plus,
    minus: values.minus,
    profile: values.profile,
    transform: {
      degrees: values.transform.degrees,
      exact: [0, 90, 180, 270].includes(values.transform.degrees),
    },
    params: {
      ...(base.params || {}),
      parent: root,
      parentName: base.name,
      variantOf: root,
      tuned: { ...values, degrees: values.transform.degrees },
    },
    note: `variant of ${root} (${base.name}) · width ${values.widthPct}% · ` +
      `${values.profile} plus ${values.plus} minus ${values.minus} · turn ${values.transform.degrees}°`,
  };
  delete record.updated;
  delete record.savedName;
  return { ok: true, uid, name: chosen, root, record, base };
}

async function renderPlate(uid) {
  await run(process.execPath, [path.join(ROOT, "scripts", "print_plates.mjs"), "--only", uid],
    { cwd: ROOT, timeout: 180000 });
}

export async function saveTune(input) {
  const uids = registryUids();
  const plan = await prisma.$transaction(async (tx) => {
    const rows = await tx.sandboxCurve.findMany();
    const outcome = planOverwrite({ ...input, rows, uids });
    if (!outcome.ok) throw new DeskError(outcome.error, outcome.status);
    const body = JSON.stringify(outcome.data);
    if (outcome.created) {
      await tx.sandboxCurve.create({ data: { name: outcome.name, data: body } });
    } else {
      await tx.sandboxCurve.update({ where: { name: outcome.name }, data: { data: body } });
    }
    return outcome;
  });

  let warning;
  try {
    await exportTable("sandbox-curves");
  } catch (error) {
    warning = `saved, but the JSON copy is stale: ${String(error.message || error)}`;
  }
  // the plates page shows the plate, so saving one rebuilds it; a render failure is a
  // warning, not a lost save
  if (!warning) {
    try {
      await renderPlate(plan.name);
    } catch (error) {
      warning = `saved; the plate did not render: ${String(error.message || error)}`;
    }
  }
  return { name: plan.name, spine: plan.data.spine, created: plan.created,
           values: input.values, ...(warning ? { warning } : {}) };
}

// one writer at a time inside this process: two tabs cannot take the same uid
let queue = Promise.resolve();
const serial = (work) => {
  const next = queue.then(work, work);
  queue = next.then(() => {}, () => {});
  return next;
};

export async function createVariant({ spine, name, values }) {
  return serial(async () => {
    const registry = JSON.parse(readFileSync(REGISTRY, "utf8"));
    const deskRows = await prisma.sandboxCurve.findMany();
    const deskNames = deskRows.map((row) => parsed(row)?.curveName).filter(Boolean);
    const plan = planVariant({ curves: registry.curves, baseUid: spine, name, values, deskNames,
                               deskIds: deskRows.map((row) => row.name) });
    if (!plan.ok) throw new DeskError(plan.error, plan.status);

    const record = plan.record;
    const uid = plan.uid;

    // the seed is a file, so keep the previous copy and write the new one atomically
    mkdirSync(path.dirname(BACKUP), { recursive: true });
    copyFileSync(REGISTRY, BACKUP);
    registry.curves.push(record);
    registry.sets = registry.sets || [];
    registry.sets.push({
      uid: `set-${uid}`, name: record.name, inner_uid: uid, border_uid: uid,
      rotation: 0, pieces: 1, perSide: 9, importance: 0,
    });
    const temp = `${REGISTRY}.tmp`;
    writeFileSync(temp, `${JSON.stringify(registry, null, 2)}\n`);
    renameSync(temp, REGISTRY);

    let wrote = false;
    try {
      await prisma.$transaction([
        prisma.curve.create({
          data: {
            uid, name: record.name,
            family: record.family_id || record.family || null,
            lists: JSON.stringify(record.lists || []),
            aliases: JSON.stringify(record.aliases || []),
            starred: false, candidate: false,
          },
        }),
        prisma.note.create({
          data: {
            uid, name: record.name, importance: 0, rotation: 0, pieces: 1,
            borderUid: null, perSide: 9, borderTurn: 0, offsets: 0,
            widthPct: Number(values.widthPct), plus: Number(values.plus),
            minus: Number(values.minus), profile: values.profile || null,
            formula: record.formula ? JSON.stringify(record.formula) : null,
            params: record.params ? JSON.stringify(record.params) : null,
            grid: record.grid || null,
            stationRule: record.params?.stationRule || null,
            algorithm: record.conversion?.algorithm || record.kind || null,
            conversion: record.conversion ? JSON.stringify(record.conversion) : null,
            transform: JSON.stringify(record.transform),
            note: record.note || null,
          },
        }),
        prisma.curveSet.create({
          data: {
            uid: `set-${uid}`, name: record.name, innerUid: uid, borderUid: uid,
            rotation: 0, pieces: 1, perSide: 9, importance: 0,
          },
        }),
      ]);
      wrote = true;
      await prisma.sandboxCurve.create({
        data: { name: uid, data: JSON.stringify({
          ...values, spine: plan.root, curveName: record.name, tune: true, variant: uid,
        }) },
      });
      await exportTable("sandbox-curves");
      await exportTable("curves");
    } catch (error) {
      // put the seed and the database back, so a half-made curve is never listed
      try { copyFileSync(BACKUP, REGISTRY); } catch { /* the file is reported below */ }
      if (wrote) {
        await prisma.curveSet.deleteMany({ where: { innerUid: uid } }).catch(() => {});
        await prisma.note.deleteMany({ where: { uid } }).catch(() => {});
        await prisma.curve.deleteMany({ where: { uid } }).catch(() => {});
      }
      await prisma.sandboxCurve.deleteMany({ where: { name: uid } }).catch(() => {});
      throw new DeskError(`could not make the new curve: ${String(error.message || error)}`, 500);
    }

    // the plate is what /plates shows: a render failure is a warning, not a lost curve
    let warning;
    try {
      await renderPlate(uid);
    } catch (error) {
      warning = `the curve is saved; its plate did not render: ${String(error.message || error)}`;
    }
    return { uid, name: record.name, spine: plan.root, created: true, values,
             ...(warning ? { warning } : {}) };
  });
}
