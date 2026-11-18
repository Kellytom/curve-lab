import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { readNotes, saveNotes } from "../src/lib/curve-notes.js";

test("a note is saved by uid and merged with the others", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "curve-notes-"));
  await saveNotes({ curves: [{ uid: "c-0001", name: "swan-line", importance: 6 }] }, root);
  await saveNotes({ curves: [{ uid: "c-0002", importance: 3 }] }, root);
  await saveNotes({ curves: [{ uid: "c-0001", importance: 9 }] }, root);
  const notes = readNotes(root).curves;
  assert.deepEqual(notes.map((n) => n.uid).sort(), ["c-0001", "c-0002"]);
  assert.equal(notes.find((n) => n.uid === "c-0001").importance, 9);
  assert.equal(notes.find((n) => n.uid === "c-0001").name, "swan-line");
  await rm(root, { recursive: true, force: true });
});

test("an empty save cannot wipe the notes", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "curve-notes-"));
  await saveNotes({ curves: [{ uid: "c-0001" }] }, root);
  await assert.rejects(() => saveNotes({ curves: [] }, root), /refusing to empty/);
  assert.equal(readNotes(root).curves.length, 1);
  await rm(root, { recursive: true, force: true });
});

test("a bad uid or importance is refused", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "curve-notes-"));
  await assert.rejects(() => saveNotes({ curves: [{ uid: "nope" }] }, root));
  await assert.rejects(() => saveNotes({ curves: [{ uid: "c-0001", importance: 11 }] }, root));
  await rm(root, { recursive: true, force: true });
});

test("the previous notes are kept as a backup", async () => {
  const { readdir } = await import("node:fs/promises");
  const root = await mkdtemp(path.join(tmpdir(), "curve-notes-"));
  await saveNotes({ curves: [{ uid: "c-0001", importance: 5 }] }, root);
  await saveNotes({ curves: [{ uid: "c-0001", importance: 7 }] }, root);
  const names = await readdir(path.join(root, "workbench", "backups"));
  const text = await readFile(path.join(root, "workbench", "backups", names[0]), "utf8");
  assert.match(text, /"importance": 5/);
  await rm(root, { recursive: true, force: true });
});
