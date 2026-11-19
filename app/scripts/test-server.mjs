// The click-everything gate on a scratch database.
//
//   node app/scripts/test-server.mjs
//
// It copies app/prisma/dev.db with `sqlite3 .backup` (a consistent copy even
// with WAL on), builds the app with DATABASE_URL pointed at the copy, starts
// app/dist/server/entry.mjs on a free port, waits for /api/health, runs
// check-clicks.mjs against it, restores the three export files the server
// writes, stops the server and removes the copy.
//
// The record the operator is naming into is never touched: the server's
// DATABASE_URL is the copy, and this script never opens app/prisma/dev.db for
// writing.

import { execFileSync, spawn } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import net from "node:net";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const APP = path.join(ROOT, "app");
const DB = path.join(APP, "prisma", "dev.db");
const ENTRY = path.join(APP, "dist", "server", "entry.mjs");
const EXPORTS = [
  path.join(ROOT, "workbench", "finder-stars.json"),
  path.join(ROOT, "workbench", "starred.json"),
  path.join(ROOT, "workbench", "curve-notes.json"),
];

function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      server.close(() => resolve(port));
    });
    server.on("error", reject);
  });
}

async function waitForHealth(url, timeoutMs = 30000) {
  const start = Date.now();
  let last = "";
  while (Date.now() - start < timeoutMs) {
    try {
      const response = await fetch(url);
      const body = await response.json();
      if (response.ok && body.ok) return body;
      last = JSON.stringify(body);
    } catch (error) {
      last = String(error);
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error(`health check timed out: ${last}`);
}

function backupExports(backupDir) {
  for (const file of EXPORTS) {
    if (existsSync(file)) copyFileSync(file, path.join(backupDir, path.basename(file)));
  }
}

function restoreExports(backupDir) {
  for (const file of EXPORTS) {
    const backup = path.join(backupDir, path.basename(file));
    if (existsSync(backup)) copyFileSync(backup, file);
  }
}

async function main() {
  if (!existsSync(DB)) {
    console.error(`no database at ${DB}`);
    process.exit(1);
  }

  const scratch = mkdtempSync(path.join(tmpdir(), "curve-lab-gate-"));
  const copy = path.join(scratch, "dev.db");
  const backupDir = path.join(scratch, "exports");
  mkdirSync(backupDir, { recursive: true });

  let server = null;
  let code = 1;

  try {
    execFileSync("sqlite3", [DB, `.backup '${copy}'`], { stdio: "pipe" });
    backupExports(backupDir);

    execFileSync("npm", ["--prefix", "app", "run", "build"], {
      cwd: ROOT,
      stdio: "inherit",
      env: { ...process.env, DATABASE_URL: `file:${copy}` },
    });

    const port = await freePort();
    server = spawn(process.execPath, [ENTRY], {
      cwd: APP,
      env: {
        ...process.env,
        HOST: "127.0.0.1",
        PORT: String(port),
        DATABASE_URL: `file:${copy}`,
        CURVE_LAB_ROOT: ROOT,
      },
      stdio: ["ignore", "pipe", "pipe"],
    });

    let logs = "";
    server.stdout.on("data", (chunk) => { logs += chunk; });
    server.stderr.on("data", (chunk) => { logs += chunk; });

    const health = await waitForHealth(`http://127.0.0.1:${port}/api/health`);
    console.log(`server ${health.app} · node ${health.node} · astro ${health.astro} · :${port}`);

    const check = spawn(process.execPath, [path.join(APP, "scripts", "check-clicks.mjs")], {
      cwd: ROOT,
      env: { ...process.env, CURVE_LAB_URL: `http://127.0.0.1:${port}` },
      stdio: "inherit",
    });
    code = await new Promise((resolve) => check.on("close", resolve));
    if (code !== 0 && logs.trim()) console.error(`server log:\n${logs.trim()}`);
  } catch (error) {
    console.error(String(error.stack || error));
    code = 1;
  } finally {
    if (server) {
      server.kill("SIGTERM");
      await new Promise((resolve) => {
        const timer = setTimeout(() => { server.kill("SIGKILL"); resolve(); }, 5000);
        server.on("close", () => { clearTimeout(timer); resolve(); });
      });
    }
    restoreExports(backupDir);
    rmSync(scratch, { recursive: true, force: true });
  }

  process.exit(code);
}

main();
