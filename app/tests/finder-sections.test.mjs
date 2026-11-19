import assert from "node:assert/strict";
import test from "node:test";
import { finderSections } from "../src/lib/finder-sections.js";

const curve = (id, name, extra = {}) => ({ id, name, family: "septic", ...extra });

test("a curve that is both mirrored and featured is drawn once", () => {
  const both = curve("a", "mirrored and featured", { featured: true, flags: ["mirror y (gap 0.0000)"] });
  const sections = finderSections([both]);
  const seen = sections.flatMap((section) => section.curves.map((c) => c.id));
  assert.deepEqual(seen, ["a"]);
  assert.equal(sections.find((section) => section.curves.includes(both)).key, "symmetric");
});

test("no curve appears in two sections, whatever its flags", () => {
  const curves = [
    curve("star", "starred one", { flags: ["mirror y (gap 0.0000)"], featured: true }),
    curve("mirror", "mirrored one", { flags: ["mirror y=x (gap 0.0000)"] }),
    curve("best", "featured one", { featured: true }),
    curve("plain", "plain one", { family: "bounded" }),
  ];
  const sections = finderSections(curves, (c) => c.id === "star");
  const ids = sections.flatMap((section) => section.curves.map((c) => c.id));
  assert.equal(new Set(ids).size, ids.length, "a curve is in two sections");
  assert.deepEqual(ids.sort(), ["best", "mirror", "plain", "star"]);
});

test("a starred curve leaves its family section", () => {
  const curves = [curve("a", "one"), curve("b", "two")];
  const sections = finderSections(curves, (c) => c.id === "b");
  const starred = sections.find((section) => section.key === "starred");
  assert.deepEqual(starred.curves.map((c) => c.id), ["b"]);
  const familied = sections.filter((section) => section.key === "septic");
  assert.deepEqual(familied.flatMap((section) => section.curves.map((c) => c.id)), ["a"]);
});
