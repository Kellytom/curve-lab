import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readdir, readFile, rm, writeFile } from "node:fs/promises";
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

test("a stale write is refused, and old versions are kept", async () => {
  const { fileHash } = await import("../src/lib/finder-stars.js");
  const root = await mkdtemp(path.join(tmpdir(), "finder-stars-"));
  await saveFinderStars({ curves: [{ name: "a" }] }, root);
  const livePath = path.join(root, "workbench", "finder-stars.json");
  const seen = fileHash(await readFile(livePath, "utf8"));
  await saveFinderStars({ curves: [{ name: "b" }] }, root);
  await assert.rejects(
    () => saveFinderStars({ baseHash: seen, curves: [{ name: "c" }] }, root),
    /changed since it was read/);
  const backups = await readdir(path.join(root, "workbench", "backups"));
  assert.ok(backups.length >= 1, "no timestamped backup kept");
  await rm(root, { recursive: true, force: true });
});

test("an empty save cannot wipe a non-empty list", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "finder-stars-"));
  await saveFinderStars({ curves: [{ name: "a" }, { name: "b" }] }, root);
  await assert.rejects(() => saveFinderStars({ curves: [] }, root), /refusing to empty/);
  const live = JSON.parse(await readFile(path.join(root, "workbench", "finder-stars.json"), "utf8"));
  assert.equal(live.curves.length, 2);
  await rm(root, { recursive: true, force: true });
});

test("an empty save is allowed when it is said out loud", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "finder-stars-"));
  await saveFinderStars({ curves: [{ name: "a" }] }, root);
  const result = await saveFinderStars({ curves: [], allowEmpty: true }, root);
  assert.equal(result.saved, 0);
  await rm(root, { recursive: true, force: true });
});

test("a save reports the hash of what it wrote, and that hash is accepted", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "finder-stars-"));
  const first = await saveFinderStars({ curves: [{ name: "a" }] }, root);
  assert.match(first.hash, /^[0-9a-f]{12}$/);
  const second = await saveFinderStars({ baseHash: first.hash, curves: [{ name: "a" }, { name: "b" }] }, root);
  assert.equal(second.saved, 2);
  await rm(root, { recursive: true, force: true });
});

test("the state reader returns the list and its hash", async () => {
  const { finderStarsState } = await import("../src/lib/finder-stars.js");
  const root = await mkdtemp(path.join(tmpdir(), "finder-stars-"));
  await saveFinderStars({ curves: [{ name: "a" }] }, root);
  const state = finderStarsState(root);
  assert.equal(state.source, "live");
  assert.deepEqual(state.curves.map((c) => c.name), ["a"]);
  assert.match(state.hash, /^[0-9a-f]{12}$/);
  await rm(root, { recursive: true, force: true });
});

test("the same curve twice is merged, not refused", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "finder-stars-"));
  const result = await saveFinderStars({
    curves: [
      { name: "loop t=1/2,3/4" },
      { name: "loop t=1/2,3/4", id: "loop-t-1-2-3-4" },
      { name: "cross+45deg at t=1/4" },
    ],
  }, root);
  assert.equal(result.saved, 2);
  const live = JSON.parse(await readFile(path.join(root, "workbench", "finder-stars.json"), "utf8"));
  assert.deepEqual(live.curves.map((c) => c.name), ["loop t=1/2,3/4", "cross+45deg at t=1/4"]);
  await rm(root, { recursive: true, force: true });
});
