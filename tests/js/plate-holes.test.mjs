import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import P from "../../workbench/plate_math.js";
import { rowFor, symmetricStrength } from "../../scripts/lib/plate-row.mjs";

// The operator, 2026-11-23: remove the inside cap and the roundSpikes bevel, "letting each
// rail cross itself at a tight turn, marking every crossing with a red dot, hiding the small
// loop as an invisible span", and record the spans in book/print/rail-holes.json.
//
// The three curves are the handoff's own probe: c-0046 three crossings a side, c-0065 fifteen
// and twelve, c-0273 two and one. The counts grew with the cap removed, so this file checks the
// law and the artefact, not the counts.

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const HOLES = new URL("../../book/print/rail-holes.json", import.meta.url);

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
const exported = JSON.parse(readFileSync(new URL("../../data/curves.json", import.meta.url)));
const noteOf = new Map((exported.rows || []).map((row) => [row.uid, row.note || {}]));
const deskFile = JSON.parse(readFileSync(new URL("../../data/sandbox-curves.json", import.meta.url)));
const deskOf = new Map((deskFile.rows || []).map((row) => [row.name, row]));

// The same construction the plate makes: path curves through pathGroup, row curves through
// group, both at the plate's own preset width and one strength for both sides.
const railsFor = (uid) => {
  const record = registry.curves.find((row) => row.uid === uid);
  const row = rowFor(record, { note: noteOf.get(uid) || {}, desk: deskOf.get(uid) || {} });
  const strength = symmetricStrength(row.character.plus, row.character.minus);
  const group = Array.isArray(record.path) && record.path.length > 2
    ? P.pathGroup(record.path, {
        widthPercent: row.width.percent, plus: strength, minus: strength,
        profile: row.character.profile,
      })
    : P.group({ ...row, character: { ...row.character, plus: strength, minus: strength } });
  return { record, group, rails: group.paths.slice(1, 3) };
};

const arcOf = (rail) => {
  const arc = [0];
  for (let i = 1; i < rail.length; i += 1) {
    arc.push(arc[i - 1] + Math.hypot(rail[i][0] - rail[i - 1][0], rail[i][1] - rail[i - 1][1]));
  }
  return arc;
};

// The artefact is generated, and book/print is rebuilt from the records: regenerate these three
// plates and compare the result with the file in git, so a law change that forgets the export
// fails here instead of shipping a stale record.
const before = JSON.parse(readFileSync(HOLES, "utf8"));
const run = spawnSync(process.execPath,
  ["scripts/print_plates.mjs", "--only", "c-0046,c-0065,c-0273", "--svg-only"],
  { cwd: ROOT, encoding: "utf8" });
// compare before the assertions below use it
const after = JSON.parse(readFileSync(HOLES, "utf8"));

for (const uid of ["c-0046", "c-0065", "c-0273"]) {
  test(`${uid}: both rails are drawn whole, and a rail crosses itself`, () => {
    const { group, rails } = railsFor(uid);
    assert.ok(group && rails.length === 2, `${uid}: a rail is missing`);
    // No inside cap: the rail is the asked offset at every station. Both rails reach the
    // asked width, which is what the withdrawn cap used to prevent.
    assert.ok(Math.abs(group.width - group.asked) < 0.6,
      `${uid}: drew ${group.width} %, asked ${group.asked} %`);
    const infos = rails.map((rail) => P.railHoles(rail));
    assert.ok(infos.some((info) => info.crossings.length > 0), `${uid}: no self-crossing found`);
  });

  test(`${uid}: the loop between two passes is a span, and it is short`, () => {
    const { rails } = railsFor(uid);
    const infos = rails.map((rail) => P.railHoles(rail));
    assert.ok(infos.some((info) => info.spans.length > 0), `${uid}: no hidden span`);
    rails.forEach((rail, side) => {
      const arc = arcOf(rail);
      const total = arc[arc.length - 1] || 1;
      for (const span of infos[side].spans) {
        // The stated rule: only the loop is hidden, never the long way round the rail.
        assert.ok(span.from < span.to, `${uid} rail ${side}: span runs backward`);
        assert.ok(span.to - span.from >= 1, `${uid} rail ${side}: a span is one station`);
        assert.ok(span.length <= 0.35 * total + 1e-9,
          `${uid} rail ${side}: a ${(span.length / total * 100).toFixed(0)} % span is hidden`);
      }
    });
  });

  test(`${uid}: the plate dots every crossing and records the span`, () => {
    assert.equal(run.status, 0, `the plate export failed: ${run.stderr || run.stdout}`);
    const { rails } = railsFor(uid);
    const crossings = rails.reduce((count, rail) => count + P.railHoles(rail).crossings.length, 0);
    const entry = after.curves.find((row) => row.uid === uid);
    assert.ok(entry, `${uid} is not in book/print/rail-holes.json`);
    const spans = entry.rails.reduce((count, rail) => count + rail.spans.length, 0);
    assert.ok(spans > 0, `${uid}: no invisible span recorded`);
    const recorded = entry.rails.reduce((count, rail) => count + rail.crossings.length, 0);
    assert.ok(recorded > 0, `${uid}: the recorded crossings are empty`);
    assert.ok(crossings > 0);
    // the export, this code and the file in git must agree
    const committed = before.curves.find((row) => row.uid === uid);
    assert.ok(committed, `${uid} was missing from the committed record`);
    assert.deepEqual(committed, entry,
      `${uid}: book/print/rail-holes.json is stale — rerun the plate export`);
    const svg = readFileSync(new URL(`../../book/print/${uid}.svg`, import.meta.url), "utf8");
    const dots = (svg.match(/fill="#b03a2e"/g) || []).length;
    assert.equal(dots, recorded, `${uid}: ${dots} dots drawn, ${recorded} recorded`);
  });
}

test("the record is well formed, with no broken row", () => {
  assert.equal(after.format, "curve-lab.rail-holes/1");
  for (const entry of after.curves) {
    for (const rail of entry.rails) {
      assert.ok(rail.rail === "plus" || rail.rail === "minus", `${entry.uid}: unknown rail name`);
      for (const span of rail.spans) {
        assert.ok(Number.isFinite(span.from) && Number.isFinite(span.to), `${entry.uid}: bad index`);
        assert.ok(Array.isArray(span.start) && Array.isArray(span.end), `${entry.uid}: bad point`);
      }
    }
  }
});
