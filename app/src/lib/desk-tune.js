// Desk io for the tuning pages.
//
// One row is one tuning. A row's `name` is its key and its URL; `curveName` is what the
// operator typed. Many rows may share one spine — five versions of one curve is the
// point, not a duplicate — but two rows may never share a name, and a new version may
// never squat on a registry id.
//
// The rules live in planSave so they can be tested without a database. saveTune applies
// the plan in one transaction, then writes the JSON copy the plate reads.

import { readFileSync } from "node:fs";
import path from "node:path";
import { prisma } from "./db.js";
import { exportTable } from "./data-export.js";

const ROOT = path.resolve(import.meta.dirname, "..", "..", "..");

export const PROFILES = ["bow", "s", "taper"];
export const VALUES = { widthPct: [0.5, 20, 6], plus: [-8, 8, 2], minus: [-8, 8, 2],
                        degrees: [-360, 360, 0] };

export class DeskError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}

// a name that can be a key and a URL: "Amper 2" -> "amper-2"
export const slugOf = (name) => String(name || "")
  .trim().toLowerCase()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/^-+|-+$/g, "")
  .slice(0, 60);

const parsed = (row) => {
  try { return JSON.parse(row.data) || {}; } catch { return null; }
};

const chosenName = (row) => {
  const data = parsed(row);
  return String((data && data.curveName) || row.name).trim();
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

// The decision, without touching a database.
//   rows: [{ name, data }]      every sandbox row, data still a JSON string
//   mode: "overwrite" | "new"
// Returns { ok, name, data, created } or { ok: false, status, error }.
export function planSave({ rows, uids, mode, rowId, spine, curveName, values }) {
  const base = String(spine || rowId || "").trim();
  if (!uids.has(base)) return { ok: false, status: 400, error: `${base || "(no id)"} is not a curve id` };

  const byName = new Map(rows.map((row) => [row.name, row]));
  const typed = String(curveName || "").trim();

  if (mode === "new") {
    if (!typed) return { ok: false, status: 400, error: "a new version needs a name" };
    const id = slugOf(typed);
    if (!id) return { ok: false, status: 400, error: `"${typed}" has no letters or digits to make a name` };
    if (uids.has(id)) {
      return { ok: false, status: 409, error: `"${id}" is already a curve id; choose another name` };
    }
    const owner = byName.get(id);
    if (owner) {
      return { ok: false, status: 409, error: `name "${typed}" is already used by ${chosenName(owner)}` };
    }
    const lower = typed.toLowerCase();
    for (const row of rows) {
      if (chosenName(row).toLowerCase() === lower) {
        return { ok: false, status: 409, error: `name "${typed}" is already used by ${row.name}` };
      }
    }
    const version = rows.filter((row) => {
      const data = parsed(row);
      return data && (data.spine === base || row.name === base);
    }).length + 1;
    return { ok: true, created: true, name: id,
             data: { ...values, spine: base, curveName: typed, tune: true, version } };
  }

  if (mode !== "overwrite") return { ok: false, status: 400, error: `unknown mode "${mode}"` };

  const id = String(rowId || base).trim();
  const owner = byName.get(id);
  if (!owner && id !== base) {
    return { ok: false, status: 404, error: `version "${id}" no longer exists` };
  }
  const previous = owner ? (parsed(owner) || {}) : {};

  // a chosen name may be changed on overwrite, but not into another row's name
  if (typed) {
    const lower = typed.toLowerCase();
    for (const row of rows) {
      if (row.name === id) continue;
      if (chosenName(row).toLowerCase() === lower) {
        return { ok: false, status: 409, error: `name "${typed}" is already used by ${row.name}` };
      }
    }
  }
  const data = { ...previous, ...values, spine: previous.spine || base, tune: true };
  if (typed) data.curveName = typed;
  return { ok: true, created: !owner, name: id, data };
}

export async function saveTune(input) {
  const uids = registryUids();
  let saved;
  try {
    saved = await prisma.$transaction(async (tx) => {
      const rows = await tx.sandboxCurve.findMany();
      const plan = planSave({ ...input, rows, uids });
      if (!plan.ok) throw new DeskError(plan.error, plan.status);
      const body = JSON.stringify(plan.data);
      if (plan.created) {
        await tx.sandboxCurve.create({ data: { name: plan.name, data: body } });
      } else {
        await tx.sandboxCurve.update({ where: { name: plan.name }, data: { data: body } });
      }
      return plan;
    });
  } catch (error) {
    if (error instanceof DeskError) throw error;
    throw new DeskError(String(error.message || error), 400);
  }

  // the plate reads the JSON copy, so a save that cannot write it says so
  let warning;
  try {
    await exportTable("sandbox-curves");
  } catch (error) {
    warning = `saved, but the JSON copy is stale: ${String(error.message || error)}`;
  }
  return { name: saved.name, spine: saved.data.spine, created: saved.created,
           version: saved.data.version, values: input.values, ...(warning ? { warning } : {}) };
}

// every row built on one spine, the base row first and the rest newest first
export async function versionsFor(spine) {
  const rows = await prisma.sandboxCurve.findMany({ orderBy: { updatedAt: "desc" } });
  const list = [];
  for (const row of rows) {
    const data = parsed(row);
    // an old base row predates the `spine` field; its own name is its spine
    if (!data || (data.spine !== spine && row.name !== spine)) continue;
    list.push({
      name: row.name,
      curveName: String(data.curveName || row.name),
      version: Number(data.version || 0),
      widthPct: data.widthPct, plus: data.plus, minus: data.minus, profile: data.profile,
      degrees: Number(data.transform?.degrees || 0),
      savedAt: row.updatedAt.toISOString(),
    });
  }
  list.sort((a, b) => (a.name === spine ? -1 : b.name === spine ? 1 : b.savedAt.localeCompare(a.savedAt)));
  return list;
}
