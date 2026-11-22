import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { isKept } from "../src/lib/provenance.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const manifest = JSON.parse(readFileSync(path.join(ROOT, "book", "kept.json"), "utf8"));
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8")).curves;
const exported = JSON.parse(readFileSync(path.join(ROOT, "data", "curves.json"), "utf8")).rows;

function keptNow() {
  const byUid = new Map(registry.map((record) => [record.uid, { ...record }]));
  for (const row of exported) {
    const base = byUid.get(row.uid) || {};
    byUid.set(row.uid, {
      ...base, ...row,
      stars: row.stars ?? row.note?.importance ?? 0,
      note: row.note?.note || "",
      params: base.params ?? row.note?.params ?? row.params,
    });
  }
  return [...byUid.values()].filter((curve) => isKept(curve, byUid)).map((curve) => curve.uid).sort();
}

test("the manifest is exactly the kept set, no more and no less", () => {
  const wanted = keptNow();
  const listed = manifest.rows.map((row) => row.uid).sort();
  assert.deepEqual(listed, wanted);
  assert.equal(manifest.count, wanted.length);
  assert.equal(new Set(listed).size, listed.length, "a curve appears twice");
});

test("every kept curve has its plate, its web copy and its figure", () => {
  assert.deepEqual(manifest.missing, []);
  for (const row of manifest.rows) {
    for (const [key, file] of Object.entries(row.files)) {
      assert.ok(existsSync(path.join(ROOT, file)), `${row.uid}:${key} is missing (${file})`);
    }
  }
});

test("every row carries its provenance", () => {
  for (const row of manifest.rows) {
    assert.match(row.provenance, /\S/, `${row.uid} has no provenance sentence`);
  }
});
