import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { writeIfChanged } from "../../scripts/lib/write-if-changed.mjs";

// The fault: the launch agent re-ran the ornament writer every ten seconds, and the
// writer wiped and rewrote 371 files, so the dev server reloaded every open page. An
// unchanged file must keep its inode and mtime.

test("an unchanged file is left exactly as it is", () => {
  const dir = mkdtempSync(path.join(tmpdir(), "write-if-changed-"));
  const file = path.join(dir, "a.svg");
  writeFileSync(file, "same text\n");
  const before = statSync(file);
  const wrote = writeIfChanged(file, "same text\n");
  const after = statSync(file);
  assert.equal(wrote, false, "an unchanged write must report false");
  assert.equal(after.ino, before.ino);
  assert.equal(after.mtimeMs, before.mtimeMs);
});

test("changed text is written, and a missing file is created", () => {
  const dir = mkdtempSync(path.join(tmpdir(), "write-if-changed-"));
  const file = path.join(dir, "b.svg");
  assert.equal(writeIfChanged(file, "first\n"), true);
  assert.equal(readFileSync(file, "utf8"), "first\n");
  assert.equal(writeIfChanged(file, "second\n"), true);
  assert.equal(readFileSync(file, "utf8"), "second\n");
});
