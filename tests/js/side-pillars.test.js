// The side pillar: the twelve rules from state/SPEC-side-pillars-int.md, and
// the six controls that must each move a printed number.
// Run: node --test tests/js/side-pillars.test.js
const { test } = require("node:test");
const assert = require("node:assert/strict");
const SP = require("../../workbench/side_pillars.js");

const sweep = (key, values) => values.map((v) => SP.model({ [key]: v }));
const range = (lo, hi, step) => {
  const out = [];
  for (let n = lo; n <= hi; n += step) out.push(n);
  return out;
};

test("thin: the foot is at most 1/24 of the height at every setting", () => {
  for (const m of sweep("diameters", range(24, 96, 1))) {
    assert.ok(m.d0 / SP.H <= 1 / 24 + 1e-12, `diameters ${m.c.diameters}`);
  }
  assert.equal(SP.model({}).c.diameters, 48);
});

test("taper: the top is at least 5/100 thinner than the foot", () => {
  for (const m of sweep("ratio", range(70, 95, 1))) {
    assert.ok(m.dt <= m.x0 * 2 * 0.95 + 1e-12, `ratio ${m.c.ratio}`);
    assert.ok(SP.checks({ ratio: m.c.ratio }).taper);
  }
});

test("entasis: the shaft is above the taper line at the chosen station", () => {
  for (const station of range(25, 50, 1)) {
    for (const swell of range(0, 6, 1)) {
      const m = SP.model({ station, swell });
      const k = SP.checks({ station, swell });
      if (swell === 0) {
        assert.ok(Math.abs(m.control.x - m.mid) < 1e-12);
      } else {
        assert.ok(k.swellAboveLine, `station ${station}, swell ${swell}`);
      }
      // the station is where the model says it is: y(1/2) = station share
      assert.ok(Math.abs(SP.shaftY(m, 0.5) - (SP.H * station) / 100) < 1e-9);
      // the measured swell is the control's own share of the foot half-width
      const above = SP.shaftX(m, 0.5) - SP.shaftLineX(m, 0.5);
      assert.ok(Math.abs(above - m.swellHalf) < 1e-9);
      assert.ok(above <= (m.x0 * 6) / 100 + 1e-12);
    }
  }
});

test("foot widest: no station of the shaft is wider than the foot", () => {
  for (const ratio of range(70, 95, 5)) {
    const ceiling = SP.swellCeiling(ratio);
    for (const swell of range(0, ceiling, 1)) {
      const m = SP.model({ ratio, swell });
      assert.ok(SP.checks({ ratio, swell }).footWidest, `ratio ${ratio}, swell ${swell}`);
      for (let i = 0; i <= 100; i += 1) {
        assert.ok(SP.shaftX(m, i / 100) <= m.x0 + 1e-9);
      }
    }
  }
});

test("the swell ceiling tightens as the taper lightens", () => {
  assert.equal(SP.swellCeiling(82), 4);
  assert.equal(SP.swellCeiling(70), 7);
  assert.equal(SP.swellCeiling(95), 1);
  // above the ceiling the control is clamped, so the foot stays widest
  const m = SP.model({ ratio: 95, swell: 9 });
  assert.equal(m.c.swell, 1);
});

test("base and capital stand proud of the shaft", () => {
  for (const m of sweep("base", range(100, 300, 10))) {
    const k = SP.checks({ base: m.c.base });
    assert.ok(k.baseStandsProud);
    assert.ok(k.capitalStandsProud);
  }
});

test("one line per pillar, open, with nothing to fill", () => {
  const svg = SP.svgMarkup({});
  const paths = svg.match(/<path class="pillar" d="[^"]+"[^>]*>/g) || [];
  assert.equal(paths.length, 2);
  // the group carries fill="none": a line has nothing to fill
  const group = svg.match(/<g [^>]*fill="none"[^>]*>/);
  assert.ok(group, "the line group sets fill none");
  for (const p of paths) {
    assert.ok(!/fill="/.test(p), "no path paints a fill of its own");
    assert.ok(!/Z/.test(p));
    assert.equal((p.match(/M /g) || []).length, 1);
  }
});

test("the outside edge: right on the right, left on the left", () => {
  const svg = SP.svgMarkup({});
  const paths = [...svg.matchAll(/<path class="pillar" d="([^"]+)"/g)].map((m) => m[1]);
  const xs = (d) => [...d.matchAll(/(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/g)].map((m) => Number(m[1]));
  const right = xs(paths[0]);
  const left = xs(paths[1]);
  // each line stays within one foot width of its own axis: a control point
  // pulled to the centre bows the shaft across the page (seen 2026-11-23)
  const m = SP.model({});
  const foot = m.d0;
  for (const x of right) assert.ok(x > 150 - foot && x < 150 + foot, `right x ${x}`);
  for (const x of left) assert.ok(x > -150 - foot && x < -150 + foot, `left x ${x}`);
});

test("the labels sit in the empty field, clear of each other", () => {
  for (const c of [{}, { diameters: 24 }, { diameters: 96 }, { station: 25 }, { station: 50 }]) {
    const marks = SP.labels(SP.model(c));
    assert.equal(marks.length, 5);
    // in the empty field, inside the right pillar and clear of the centre
    const m = SP.model(c);
    for (const l of marks) {
      assert.ok(l.x > 0 && l.x < 150 - m.d0, `label ${l.text} at x ${l.x}`);
    }
    for (let i = 0; i < marks.length; i += 1) {
      for (let j = i + 1; j < marks.length; j += 1) {
        assert.ok(Math.abs(marks[i].y - marks[j].y) >= 12,
          `${marks[i].text} and ${marks[j].text} are ${Math.abs(marks[i].y - marks[j].y)} apart`);
      }
    }
  }
});

test("nothing is cut by the frame, at the extremes", () => {
  const cases = [
    { diameters: 24, ratio: 95, base: 300, capital: 300 },
    { diameters: 96, ratio: 70, base: 100, capital: 100 },
    { diameters: 24, ratio: 70, base: 100, capital: 300 },
  ];
  for (const c of cases) {
    const k = SP.checks(c);
    assert.ok(k.insideBox, JSON.stringify(c));
  }
});

test("the shaft is a Q command, not a chain of L steps", () => {
  const d = SP.pillarPath(SP.model({}), 150);
  assert.equal((d.match(/Q /g) || []).length, 1);
  // M, plinth step, torus step, foot, Q, echinus step, abacus step
  assert.equal((d.match(/L /g) || []).length, 5);
});

test("every printed number says its unit", () => {
  const rows = SP.readout({});
  assert.equal(rows.length, 9);
  for (const r of rows) {
    assert.match(r.label, /share|foot widths|foot|height|station|point/);
    assert.ok(r.value.length > 0);
  }
  const values = Object.fromEntries(rows.map((r) => [r.key, r.value]));
  assert.equal(values.foot, "1/48 H");
  assert.equal(values.height, "48");
});

test("fractions, not decimals, wherever a value is exact", () => {
  const values = SP.readout({ ratio: 82, swell: 2, base: 150 }).map((r) => r.value);
  assert.ok(values.includes("41/50"));
  assert.ok(values.includes("1/50"));
  assert.ok(values.includes("3/2"));
  for (const v of values) assert.ok(!/0\.\d/.test(v), `${v} is a decimal where a fraction exists`);
});

test("each of the six controls moves a printed number", () => {
  const base = SP.readout({});
  const moved = {
    diameters: SP.readout({ diameters: 30 }),
    ratio: SP.readout({ ratio: 80 }),
    swell: SP.readout({ swell: 4 }),
    station: SP.readout({ station: 40 }),
    base: SP.readout({ base: 200 }),
    capital: SP.readout({ capital: 250 }),
  };
  for (const key of Object.keys(moved)) {
    const changed = moved[key].some((r, i) => r.value !== base[i].value);
    assert.ok(changed, `control ${key} leaves every number unchanged`);
  }
});
