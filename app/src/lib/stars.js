// Saving the lab's stars, in plain Node so any server can call it.
//
// Astro's route is a thin adapter here; a Next route handler or a Hono route
// calls the same function. The payload is validated with zod before anything
// touches the disk, and the write is atomic (temp file + rename).

import { mkdir, rename, writeFile } from "node:fs/promises";
import path from "node:path";
import { z } from "zod";

const NAME = /^([a-z0-9][a-z0-9-]*)-([0-9]+)-t-exp-c-([0-9]{4})$/;

const Plate = z.object({
  id: z.string().regex(NAME, "bad id"),
  descriptor: z.string().min(1),
  variant: z.number().int(),
  form: z.string().min(1),
  curve: z.string().min(1),
}).passthrough();

const Payload = z.object({
  format: z.string().optional(),
  plates: z.array(Plate),
}).superRefine((payload, ctx) => {
  const ids = new Set();
  for (const plate of payload.plates) {
    const match = NAME.exec(plate.id);
    if (match[1] !== plate.descriptor || Number(match[2]) !== plate.variant) {
      ctx.addIssue({ code: z.ZodIssueCode.custom,
        message: `the id and the fields disagree: ${plate.id}` });
    }
    if (ids.has(plate.id)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom,
        message: `duplicate id: ${plate.id}` });
    }
    ids.add(plate.id);
  }
});

export function validatePlates(payload) {
  if (!payload || !Array.isArray(payload.plates)) {
    throw new Error("expected { plates: [...] }");
  }
  return Payload.parse(payload).plates;
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
