// Session and job state, in SQLite through Prisma: one source of truth.
//
//   node scripts/jobs.mjs session set --id deepseek2 --role assistant --model kimi --state working --job offsets
//   node scripts/jobs.mjs session list
//   node scripts/jobs.mjs job claim --id offsets --owner deepseek2 --files app/src/lib/bordered.js,scripts/frames_build.mjs
//   node scripts/jobs.mjs job release --id offsets --state done
//   node scripts/jobs.mjs job list
//
// A claim is refused when another queued or active job names one of the same
// files. That is the ownership rule with teeth: it is checked, not remembered.

import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
process.env.DATABASE_URL ||= `file:${path.join(ROOT, "app", "prisma", "dev.db")}`;
const require = createRequire(path.join(ROOT, "app", "package.json"));
const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const args = process.argv.slice(2);
const get = (name, fallback) => {
  const at = args.indexOf(`--${name}`);
  return at >= 0 && at + 1 < args.length ? args[at + 1] : fallback;
};
const list = (value) => String(value || "").split(",").map((s) => s.trim()).filter(Boolean);

const [group, command] = args;

async function session() {
  if (command === "set") {
    const id = get("id");
    if (!id) throw new Error("session set needs --id");
    const row = {
      role: get("role", "assistant"),
      model: get("model", "unknown"),
      state: get("state", "idle"),
      job: get("job", null),
      lastSeen: new Date(),
    };
    await prisma.session.upsert({ where: { id }, create: { id, ...row }, update: row });
    console.log(`session ${id}: ${row.role}, ${row.model}, ${row.state}${row.job ? `, ${row.job}` : ""}`);
    return;
  }
  if (command === "list") {
    const rows = await prisma.session.findMany({ orderBy: { id: "asc" } });
    for (const row of rows) console.log(`${row.id}\t${row.role}\t${row.model}\t${row.state}\t${row.job || "-"}\t${row.lastSeen.toISOString()}`);
    return;
  }
  throw new Error("session set|list");
}

async function job() {
  if (command === "claim") {
    const id = get("id");
    const owner = get("owner");
    const files = list(get("files"));
    if (!id || !owner || !files.length) throw new Error("job claim needs --id, --owner, --files");
    const active = await prisma.job.findMany({
      where: { state: { in: ["queued", "active"] }, id: { not: id } },
    });
    const conflicts = active.flatMap((other) => {
      const owned = JSON.parse(other.files);
      const overlap = files.filter((file) => owned.includes(file));
      return overlap.length ? [{ id: other.id, owner: other.owner, overlap }] : [];
    });
    if (conflicts.length) {
      console.error(`refused: ${JSON.stringify(conflicts)}`);
      process.exitCode = 1;
      return;
    }
    await prisma.job.upsert({
      where: { id },
      create: { id, owner, files: JSON.stringify(files), state: "active" },
      update: { owner, files: JSON.stringify(files), state: "active" },
    });
    console.log(`claimed ${id} by ${owner}: ${files.length} files`);
    return;
  }
  if (command === "release") {
    const id = get("id");
    const state = get("state", "done");
    if (!id) throw new Error("job release needs --id");
    await prisma.job.update({ where: { id }, data: { state } });
    console.log(`released ${id}: ${state}`);
    return;
  }
  if (command === "list") {
    const rows = await prisma.job.findMany({ orderBy: { updatedAt: "desc" } });
    for (const row of rows) console.log(`${row.id}\t${row.owner}\t${row.state}\t${row.files}`);
    return;
  }
  throw new Error("job claim|release|list");
}

try {
  if (group === "session") await session();
  else if (group === "job") await job();
  else throw new Error("usage: node scripts/jobs.mjs session|job ...");
} catch (error) {
  console.error(String(error.message || error));
  process.exitCode = 1;
} finally {
  await prisma.$disconnect();
}
