import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { readFinderStars, saveFinderStars } from "../src/lib/finder-stars.js";

test("a save keeps the previous list as a backup", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "finder-stars-"));
  await saveFinderStars({ curves: [{ name: "loop t=1/4,3/4" }] }, root);
  await saveFinderStars({ curves: [{ name: "cross+45deg at t=1/4" }] }, root);
  const backup = JSON.parse(await readFile(path.join(root, "workbench", "finder-stars.backup.json"), "utf8"));
  assert.equal(backup.curves[0].name, "loop t=1/4,3/4");
  const live = JSON.parse(await readFile(path.join(root, "workbench", "finder-stars.json"), "utf8"));
  assert.equal(live.curves[0].name, "cross+45deg at t=1/4");
  await rm(root, { recursive: true, force: true });
});

test("a damaged list is repaired from the backup, not read as empty", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "finder-stars-"));
  await saveFinderStars({ curves: [{ name: "a" }] }, root);
  await saveFinderStars({ curves: [{ name: "b" }] }, root);
  await writeFile(path.join(root, "workbench", "finder-stars.json"), "{ not json", "utf8");
  const read = readFinderStars(root);
  assert.equal(read.source, "backup");
  assert.deepEqual(read.curves.map((c) => c.name), ["a"]);
  await rm(root, { recursive: true, force: true });
});

test("a malformed payload is refused before anything is written", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "finder-stars-"));
  await assert.rejects(() => saveFinderStars({ curves: [{ name: "" }] }, root));
  assert.equal(readFinderStars(root).source, "none");
  await rm(root, { recursive: true, force: true });
});
