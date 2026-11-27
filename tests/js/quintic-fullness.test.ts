/**
 * The fullness fixture's guard — the rule the extension implements.
 *
 * P_i = (1 - alpha) * L_i + alpha * G_i, endpoints fixed. If alpha 0 is not a
 * straight line, or alpha 1 is not the guide, the fixture cannot be used to
 * check the extension, because a wrong fixture proves nothing.
 *
 * Run: node --test tests/js/quintic-fullness.test.ts
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const DATA = JSON.parse(readFileSync(path.join(ROOT, "workbench", "quintic-fullness.json"), "utf8"));

const close = (a: number, b: number, tol = 1e-6) => Math.abs(a - b) <= tol;
const chordAt = (p0: number[], p5: number[], i: number) => [
  (1 - i / 5) * p0[0] + (i / 5) * p5[0],
  (1 - i / 5) * p0[1] + (i / 5) * p5[1],
];

describe("fullness fixture", () => {
  test("five guides, the alpha ladder, and the rule written down", () => {
    assert.equal(DATA.guides.length, 5);
    assert.deepEqual(DATA.alphas, [0, 0.25, 0.5, 0.75, 1]);
    assert.match(DATA.rule, /P_i = \(1 - alpha\) \* L_i \+ alpha \* G_i/);
  });

  test("alpha 0 is the chord: every point collinear, matching L_i exactly", () => {
    for (const g of DATA.guides) {
      const at0 = g.values.find((v: any) => v.alpha === 0);
      const p0 = at0.points[0];
      const p5 = at0.points[5];
      at0.points.forEach((p: number[], i: number) => {
        const l = chordAt(p0, p5, i);
        assert.ok(close(p[0], l[0]) && close(p[1], l[1]), `${g.uid} alpha 0 point ${i} is off the chord`);
      });
    }
  });

  test("alpha 1 is the guide, point for point", () => {
    for (const g of DATA.guides) {
      const at1 = g.values.find((v: any) => v.alpha === 1);
      assert.deepEqual(at1.points, g.guide, `${g.uid} alpha 1 is not the guide`);
    }
  });

  test("alpha 0.5 is the midpoint of chord and guide", () => {
    for (const g of DATA.guides) {
      const at0 = g.values.find((v: any) => v.alpha === 0);
      const at1 = g.values.find((v: any) => v.alpha === 1);
      const half = g.values.find((v: any) => v.alpha === 0.5);
      for (let i = 0; i < 6; i += 1) {
        const mid = [(at0.points[i][0] + at1.points[i][0]) / 2, (at0.points[i][1] + at1.points[i][1]) / 2];
        assert.ok(
          close(half.points[i][0], mid[0], 1e-5) && close(half.points[i][1], mid[1], 1e-5),
          `${g.uid} point ${i} at alpha 0.5 is not the midpoint`,
        );
      }
    }
  });

  test("the endpoints never move", () => {
    for (const g of DATA.guides) {
      const first = g.values[0].points;
      for (const v of g.values) {
        assert.deepEqual(v.points[0], first[0], `${g.uid} start moved at alpha ${v.alpha}`);
        assert.deepEqual(v.points[5], first[5], `${g.uid} end moved at alpha ${v.alpha}`);
      }
    }
  });
});
