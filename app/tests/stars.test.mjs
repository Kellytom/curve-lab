import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { saveStars, validatePlates } from "../src/lib/stars.js";

const good = {
  plates: [{
    id: "u-bowl-arch-1-t-exp-c-0301",
    descriptor: "u-bowl-arch",
    variant: 1,
    kind: "star",
    form: "arch",
    curve: "u-bowl",
    serial: 301,
  }],
};

test("a valid payload is written atomically", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "stars-"));
  const result = await saveStars(good, root);
  assert.equal(result.saved, 1);
  const written = JSON.parse(
    await readFile(path.join(root, "workbench", "starred.json"), "utf8"));
  assert.equal(written.format, "starred/1");
  assert.equal(written.plates[0].id, "u-bowl-arch-1-t-exp-c-0301");
  await rm(root, { recursive: true, force: true });
});

test("a bad id is refused", () => {
  assert.throws(() => validatePlates({ plates: [{ id: "bad" }] }), /bad id/);
});

test("a duplicate id is refused", () => {
  assert.throws(() => validatePlates({ plates: [good.plates[0], good.plates[0]] }),
    /duplicate id/);
});

test("a payload without plates is refused", () => {
  assert.throws(() => validatePlates({}), /expected/);
});
