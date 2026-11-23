// One render at a time: a lock directory, so two saves cannot rewrite the same index.
//
//   await withLock(lockDir, async () => { ... })
//
// `print_plates.mjs --only` and `curve_pngs.mjs --only` merge their indexes; two of them at once
// read the same file, each writes its own list, and one list is lost — the fault register 29
// records. A save now renders in a detached child, so two quick saves can overlap. mkdir is
// atomic, so a directory is the lock.

import { mkdirSync, rmSync } from "node:fs";

export async function withLock(lockDir, work, { waitMs = 60000, stepMs = 200 } = {}) {
  const started = Date.now();
  for (;;) {
    try {
      mkdirSync(lockDir);
      break;
    } catch (error) {
      if (error.code !== "EEXIST") throw error;
      if (Date.now() - started > waitMs) throw new Error(`render lock is still held: ${lockDir}`);
      await new Promise((resolve) => setTimeout(resolve, stepMs));
    }
  }
  try {
    return await work();
  } finally {
    rmSync(lockDir, { recursive: true, force: true });
  }
}
