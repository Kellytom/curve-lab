// Saving the lab's stars, in plain Node so any server can call it.
//
// Astro's route is a thin adapter here; a Next route handler or a Hono route
// calls the same function. The write is atomic (temp file + rename) and the
// payload is validated before anything touches the disk.

import { mkdir, rename, writeFile } from "node:fs/promises";
import path from "node:path";

const NAME = /^([a-z0-9][a-z0-9-]*)-([0-9]+)-t-exp-c-([0-9]{4})$/;

export function validatePlates(payload) {
  if (!payload || !Array.isArray(payload.plates)) {
    throw new Error("expected { plates: [...] }");
  }
  const ids = new Set();
  payload.plates.forEach((plate) => {
    const match = NAME.exec(plate.id || "");
    if (!match) throw new Error(`bad id: ${plate.id}`);
    if (match[1] !== plate.descriptor || Number(match[2]) !== Number(plate.variant)) {
      throw new Error(`the id and the fields disagree: ${plate.id}`);
    }
    if (ids.has(plate.id)) throw new Error(`duplicate id: ${plate.id}`);
    if (!plate.form || !plate.curve) throw new Error(`missing form or curve: ${plate.id}`);
    ids.add(plate.id);
  });
  return payload.plates;
}

export async function saveStars(payload, root) {
  const plates = validatePlates(payload);
  const dir = path.join(path.resolve(root), "workbench");
  await mkdir(dir, { recursive: true });
  const target = path.join(dir, "starred.json");
  const temp = `${target}.tmp`;
  await writeFile(temp, JSON.stringify({ format: "starred/1", plates }, null, 1) + "\n");
  await rename(temp, target);
  return { saved: plates.length, path: target };
}
