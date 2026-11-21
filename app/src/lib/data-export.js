// The visible record: one JSON file per database table, written from the same
// rows the app reads. SQLite is the source of truth; these files are the same
// truth, readable by a session that cannot open SQLite.
//
// One exporter, used by the CLI (`scripts/export-data.mjs`) and by the save
// endpoints. A save that cannot write its file reports the failure; it never
// pretends the write happened.
//
// The manifest records, per file, the row count and a hash of the rows as they
// were written. `--check` recomputes both from the database, so a file that has
// fallen behind is a failing test, not a surprise later.

import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";
import { prisma } from "./db.js";
import { formulaFor } from "./formula.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.resolve(HERE, "..", "..", "..");
export const DATA = path.join(ROOT, "data");

export const FORMATS = {
  curves: "curve-lab.data.curves/1",
  stars: "curve-lab.data.stars/1",
  "plate-stars": "curve-lab.data.plate-stars/1",
  users: "curve-lab.data.users/1",
  "sandbox-curves": "curve-lab.data.sandbox-curves/1",
  metrics: "curve-lab.data.metrics/1",
  jobs: "curve-lab.data.jobs/1",
  messages: "curve-lab.data.messages/1",
};

const FILE_OF = {
  curves: "curves.json",
  stars: "stars.json",
  "plate-stars": "plate-stars.json",
  users: "users.json",
  "sandbox-curves": "sandbox-curves.json",
  metrics: "metrics.json",
  jobs: "jobs.json",
  messages: "messages.json",
};

const NOTE = {
  curves: "One object per curve: the Curve row, its Note, its CurveSet, its metric and its formula.",
  stars: "One object per starred curve in the book gallery.",
  "plate-stars": "One object per starred plate.",
  users: "The accounts table. Local only: this file is deliberately not pushed.",
  "sandbox-curves": "One object per sandbox or hybrid-desk save: the decision is the save.",
  metrics: "One object per curve: the exact measurements. A number here is generated, never typed.",
  jobs: "The session and job rows: who is working, on what, and which files they hold.",
  messages: "The inter-agent message bus history.",
};

const plain = (value) => {
  if (typeof value === "bigint") return Number.isSafeInteger(Number(value)) ? Number(value) : String(value);
  if (Array.isArray(value)) return value.map(plain);
  if (value && typeof value === "object" && !(value instanceof Date)) {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, plain(item)]));
  }
  return value instanceof Date ? value.toISOString() : value;
};

// The speed rows and the polyline stations live in the seed, not in SQLite:
// the database holds the names, the notes and the measurements.
function seedByUid() {
  const seed = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
  return new Map(seed.curves.map((curve) => [curve.uid, curve]));
}

async function rowsFor(name) {
  if (name === "curves") {
    const [curves, notes, sets, metrics] = await Promise.all([
      prisma.curve.findMany({ orderBy: { uid: "asc" } }),
      prisma.note.findMany(),
      prisma.curveSet.findMany(),
      prisma.curveMetric.findMany(),
    ]);
    const byUid = (rows) => new Map(rows.map((row) => [row.uid, row]));
    const noteOf = byUid(notes);
    const setOf = byUid(sets);
    const metricOf = byUid(metrics);
    const seed = seedByUid();
    return curves.map((curve) => {
      const note = noteOf.get(curve.uid) || null;
      const set = setOf.get(curve.uid) || null;
      const metric = metricOf.get(curve.uid) || null;
      const source = seed.get(curve.uid) || {};
      const record = plain({ ...curve, ...(note ? { name: curve.name } : {}) });
      const kind = source.kind || (metric ? metric.kind : "rows");
      const formula = formulaFor(
        { ...record, kind, speedX: source.speedX || [], speedY: source.speedY || [], path: source.path || [] },
        metric ? plain(metric) : null,
      );
      return { ...record, stars: note && Number(note.importance) > 0 ? Number(note.importance) : null,
               formula, note: plain(note), set: plain(set), metric: plain(metric) };
    });
  }
  if (name === "stars") return plain(await prisma.star.findMany({ orderBy: { name: "asc" } }));
  if (name === "plate-stars") return plain(await prisma.plateStar.findMany({ orderBy: { id: "asc" } }));
  if (name === "users") return plain(await prisma.user.findMany({ orderBy: { id: "asc" } }));
  if (name === "sandbox-curves") {
    // One object per row, with the record's own fields unfolded: a JSON string
    // inside a JSON file is double encoding, and every reader would have to
    // parse it twice.
    const rows = await prisma.sandboxCurve.findMany({ orderBy: { name: "asc" } });
    return plain(rows.map((row) => {
      let record = {};
      try { record = JSON.parse(row.data); } catch { record = { raw: row.data }; }
      delete record.name;
      return { name: row.name, ...record, savedAt: row.updatedAt };
    }));
  }
  if (name === "metrics") return plain(await prisma.curveMetric.findMany({ orderBy: { uid: "asc" } }));
  if (name === "jobs") {
    const [sessions, jobs] = await Promise.all([
      prisma.session.findMany({ orderBy: { id: "asc" } }),
      prisma.job.findMany({ orderBy: { id: "asc" } }),
    ]);
    return { sessions: plain(sessions), jobs: plain(jobs) };
  }
  if (name === "messages") return plain(await prisma.message.findMany({ orderBy: { id: "asc" } }));
  throw new Error(`no export for table ${name}`);
}

export function hashRows(rows) {
  return createHash("sha256").update(JSON.stringify(rows)).digest("hex").slice(0, 16);
}

export async function manifest() {
  try {
    return JSON.parse(await readFile(path.join(DATA, "manifest.json"), "utf8"));
  } catch {
    return { format: "curve-lab.data.manifest/1", files: {} };
  }
}

async function writeFileAtomic(file, text) {
  await writeFile(file, text, "utf8");
}

// Write one table's file and refresh its manifest entry. Returns {rows, hash}.
export async function exportTable(name) {
  const rows = await rowsFor(name);
  const body = {
    format: FORMATS[name],
    note: NOTE[name],
    count: Array.isArray(rows) ? rows.length : Object.values(rows).reduce((total, list) => total + list.length, 0),
    rows,
  };
  await mkdir(DATA, { recursive: true });
  await writeFileAtomic(path.join(DATA, FILE_OF[name]), `${JSON.stringify(body, null, 1)}\n`);
  const current = await manifest();
  current.files[name] = { file: FILE_OF[name], count: body.count, hash: hashRows(rows) };
  await writeFileAtomic(path.join(DATA, "manifest.json"), `${JSON.stringify(current, null, 1)}\n`);
  return { name, count: body.count, hash: current.files[name].hash };
}

export async function exportAll() {
  const written = [];
  for (const name of Object.keys(FORMATS)) written.push(await exportTable(name));
  await exportSchema();
  return written;
}

// The machine-readable dictionary: file -> field -> kind. Built from the rows
// that were just written, so it cannot drift from them.
export async function exportSchema() {
  const files = {};
  for (const [name, format] of Object.entries(FORMATS)) {
    const text = await readFile(path.join(DATA, FILE_OF[name]), "utf8");
    const body = JSON.parse(text);
    const first = Array.isArray(body.rows)
      ? body.rows[0]
      : Object.values(body.rows).map((list) => list[0]).filter(Boolean)[0] || null;
    files[FILE_OF[name]] = {
      format,
      kind: Array.isArray(body.rows) ? "array" : "object",
      count: body.count,
      fields: first ? kindsOf(first) : {},
    };
  }
  await writeFile(path.join(DATA, "schema.json"), `${JSON.stringify({ format: "curve-lab.data.schema/1", files }, null, 1)}\n`);
}

function kindsOf(row) {
  const out = {};
  for (const [key, value] of Object.entries(row)) {
    if (value === null) out[key] = "null";
    else if (Array.isArray(value)) out[key] = "array";
    else if (typeof value === "object") out[key] = "object";
    else if (typeof value === "bigint") out[key] = "integer";
    else out[key] = typeof value;
  }
  return out;
}

// The staleness check: recompute every table from the database and compare with
// what the files and the manifest say. Returns a list of problems.
export async function check() {
  const problems = [];
  const current = await manifest();
  for (const name of Object.keys(FORMATS)) {
    let file;
    try {
      file = JSON.parse(await readFile(path.join(DATA, FILE_OF[name]), "utf8"));
    } catch {
      problems.push(`${FILE_OF[name]}: missing`);
      continue;
    }
    const rows = await rowsFor(name);
    const hash = hashRows(rows);
    const seen = current.files[name];
    if (!seen) problems.push(`${FILE_OF[name]}: not in the manifest`);
    else if (seen.hash !== hash) problems.push(`${FILE_OF[name]}: stale, the database changed`);
    else if (hashRows(file.rows) !== hash) problems.push(`${FILE_OF[name]}: the file and the manifest disagree`);
  }
  return problems;
}
