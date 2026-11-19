import assert from "node:assert/strict";
import test from "node:test";
import { validateNotes } from "../src/lib/curve-notes.js";

test("a bad uid or importance is refused before the database sees it", () => {
  assert.throws(() => validateNotes({ curves: [{ uid: "nope" }] }), /uid/);
  assert.throws(() => validateNotes({ curves: [{ uid: "c-0001", importance: 11 }] }), /importance|number/i);
  assert.throws(() => validateNotes({ curves: [{ uid: "c-0001", pieces: 3 }] }));
});

test("a good note passes and keeps its fields", () => {
  const [note] = validateNotes({ curves: [{ uid: "c-0001", name: "swan-line", importance: 7, rotation: 90, pieces: 2 }] });
  assert.equal(note.uid, "c-0001");
  assert.equal(note.name, "swan-line");
  assert.equal(note.rotation, 90);
  assert.equal(note.pieces, 2);
});

test("a curve can be set aside for the notes pool, and only with a real flag", () => {
  const [note] = validateNotes({ curves: [{ uid: "c-0001", candidate: true }] });
  assert.equal(note.candidate, true);
  assert.throws(() => validateNotes({ curves: [{ uid: "c-0001", candidate: "yes" }] }));
});
