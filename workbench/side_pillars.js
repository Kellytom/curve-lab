// The side pillar's maths: a thin border pillar, one line per side.
//
// This is the one implementation. It loads as a plain script
// (globalThis.SidePillars) or through require from Node, so the page, the
// figure and the tests share it.
//
// The model is a page of height H with a pillar at each side. Each pillar is
// ONE polyline: the outside edge. The line steps in at the top of the base,
// runs up the shaft with the entasis (a quadratic Bézier), and steps out again
// at the capital. Positive y points up; the SVG flips y once, in this file.
//
// Every number is a ratio of whole numbers: the controls are integer counts of
// hundredths, and the readout prints them as fractions with the decimal only
// as a secondary form.
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.SidePillars = factory();
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const H = 480;              // page height, model units
  const HALF_PAGE = 180;      // model x runs -180 .. 180
  const AXIS_X = 150;         // each pillar's axis, model units
  const PLINTH_SHARE = 0.8;   // plinth and abacus half-width, in foot widths
  const TORUS_SHARE = 0.7;    // torus step at the top of the base
  const ECHINUS_SHARE = 0.65; // echinus step under the abacus

  const DEFAULTS = {
    diameters: 48,   // height in foot widths
    ratio: 82,       // top width, hundredths of the foot
    swell: 3,        // bulge at the station, hundredths of the foot width
    station: 33,     // swell station, hundredths of the height
    base: 150,       // base height, hundredths of a foot width
    capital: 200,    // capital height, hundredths of a foot width
  };

  const LIMITS = {
    diameters: [24, 96],
    ratio: [70, 95],
    station: [25, 50],
    base: [100, 300],
    capital: [100, 300],
  };

  const gcd = (a, b) => (b ? gcd(b, a % b) : Math.abs(a));

  // An integer count of hundredths, printed as a reduced fraction.
  function hundredths(n) {
    const d = 100;
    const g = gcd(n, d) || 1;
    const sign = n < 0 ? "-" : "";
    const whole = d / g;
    return sign + Math.abs(n) / g + (whole === 1 ? "" : "/" + whole);
  }

  function clamp(n, lo, hi) {
    return Math.min(hi, Math.max(lo, n));
  }

  // The swell can never lift the control point outside the foot half-width:
  // a quadratic that starts moving outward at the foot loses "the foot is the
  // widest point". Writing the foot as d0 and the top as r*d0, the control
  // point stays inside when the bulge s/100 of d0 obeys s <= (100 - ratio)/4.
  function swellCeiling(ratio) {
    return Math.max(0, Math.floor((100 - ratio) / 4));
  }

  function controls(raw) {
    const c = Object.assign({}, DEFAULTS, raw || {});
    for (const key of Object.keys(LIMITS)) {
      c[key] = clamp(Math.round(c[key]), LIMITS[key][0], LIMITS[key][1]);
    }
    c.swell = clamp(c.swell, 0, swellCeiling(c.ratio));
    return c;
  }

  // Widths and stations, all in model units.
  function model(raw) {
    const c = controls(raw);
    const d0 = H / c.diameters;             // foot width
    const dt = (d0 * c.ratio) / 100;        // top width
    const x0 = d0 / 2;                      // foot half-width
    const x2 = dt / 2;                      // top half-width
    const baseH = (d0 * c.base) / 100;
    const capH = (d0 * c.capital) / 100;
    const y0 = baseH;                       // shaft foot
    const y2 = H - capH;                    // shaft top
    const stationY = (H * c.station) / 100;
    // the bulge is a share of the whole foot width, so half of it is added
    // to each side of the taper line
    const swellHalf = (d0 * c.swell) / 200;

    const mid = (x0 + x2) / 2;
    const control = {
      x: mid + 2 * swellHalf,
      y: 2 * stationY - (y0 + y2) / 2,
    };

    return { c, d0, dt, x0, x2, baseH, capH, y0, y2, stationY, swellHalf, mid, control };
  }

  // The quadratic Bézier, sampled for the checks (never used to draw: the
  // drawing is the exact Q command).
  function shaftX(m, t) {
    const one = 1 - t;
    return one * one * m.x0 + 2 * t * one * m.control.x + t * t * m.x2;
  }

  function shaftY(m, t) {
    const one = 1 - t;
    return one * one * m.y0 + 2 * t * one * m.control.y + t * t * m.y2;
  }

  function shaftLineX(m, t) {
    return (1 - t) * m.x0 + t * m.x2;
  }

  // The points the one line passes through for the pillar whose axis is
  // `axisX`: widths grow away from the axis, so the right pillar's line is on
  // the right and the left pillar's on the left.
  function stations(m, axisX) {
    const s = axisX < 0 ? -1 : 1;
    const plinth = PLINTH_SHARE * m.d0;
    const torus = TORUS_SHARE * m.d0;
    const echinus = ECHINUS_SHARE * m.d0;
    const abacus = PLINTH_SHARE * m.d0;
    const at = (w, y) => [axisX + s * w, y];
    return {
      ground: at(plinth, 0),
      plinthTop: at(plinth, 0.6 * m.baseH),
      torusTop: at(torus, m.baseH),
      foot: at(m.x0, m.y0),
      top: at(m.x2, m.y2),
      echinusTop: at(echinus, m.y2 + m.capH / 2),
      abacusTop: at(abacus, H),
    };
  }

  // One path command string per pillar: M, three L steps, the Q shaft, two L
  // steps. No Z: the line is open, and there is nothing to fill.
  function pillarPath(m, axisX) {
    const s = axisX < 0 ? -1 : 1;
    const p = stations(m, axisX);
    const f = (n) => Number(n.toFixed(4));
    const pt = (q) => f(q[0]) + " " + f(q[1]);
    return [
      "M " + pt(p.ground),
      "L " + pt(p.plinthTop),
      "L " + pt(p.torusTop),
      "L " + pt(p.foot),
      "Q " + f(axisX + s * m.control.x) + " " + f(m.control.y) + " " + pt(p.top),
      "L " + pt(p.echinusTop),
      "L " + pt(p.abacusTop),
    ].join(" ");
  }

  function bbox(m) {
    const xs = [];
    const ys = [];
    for (const axisX of [AXIS_X, -AXIS_X]) {
      const p = stations(m, axisX);
      for (const key of Object.keys(p)) {
        xs.push(p[key][0]);
        ys.push(p[key][1]);
      }
    }
    xs.push(AXIS_X + m.control.x, -AXIS_X - m.control.x);
    ys.push(m.control.y);
    return {
      left: Math.min.apply(null, xs),
      right: Math.max.apply(null, xs),
      bottom: Math.min.apply(null, ys),
      top: Math.max.apply(null, ys),
    };
  }

  // The labels the figure carries, in model units: all in the empty field
  // between the pillars, anchored to the right of that field so no label sits
  // on a line. `x` is the right end of the text.
  function labels(m) {
    const x = AXIS_X - PLINTH_SHARE * m.d0 - 6;
    return [
      { x, y: 7, text: `base ${hundredths(m.c.base)} foot widths`, colour: "muted" },
      { x, y: Math.max(m.y0 + 12, 21), text: `foot 1/${m.c.diameters} of H`, colour: "muted" },
      { x, y: m.stationY, text: `swell +${hundredths(m.c.swell)} of the foot`, colour: "gold" },
      { x, y: m.y2 - 14, text: `top ${hundredths(m.c.ratio)} of the foot`, colour: "muted" },
      { x, y: m.y2 + m.capH / 2, text: `capital ${hundredths(m.c.capital)} foot widths`, colour: "muted" },
    ];
  }

  // The whole figure, as an SVG string in model units with y flipped once.
  function svgMarkup(raw) {
    const m = model(raw);
    const TOP_MARGIN = 70;
    const BOTTOM_MARGIN = 40;
    const svgY = (y) => (H + TOP_MARGIN - y).toFixed(2);
    const svgX = (x) => (x + HALF_PAGE).toFixed(2);
    const box = { w: 2 * HALF_PAGE, h: H + TOP_MARGIN + BOTTOM_MARGIN };

    const ink = "#2e2413";
    const muted = "#7b6c4e";
    const gold = "#c9a441";
    const guide = "#e8dfc9";
    const paper = "#fffdf7";

    const right = pillarPath(m, AXIS_X);
    const left = pillarPath(m, -AXIS_X);

    // the straight taper each shaft swells against, drawn so the swell has
    // something to be measured from
    const taper = (axisX) => {
      const s = axisX < 0 ? -1 : 1;
      return `M ${(axisX + s * m.x0).toFixed(2)} ${m.y0.toFixed(2)} ` +
             `L ${(axisX + s * m.x2).toFixed(2)} ${m.y2.toFixed(2)}`;
    };

    const text = (x, y, body, size, colour, anchor) =>
      `<text x="${svgX(x)}" y="${svgY(y)}" font-size="${size}" fill="${colour}" ` +
      `text-anchor="${anchor || "start"}" font-family="Georgia,serif">${body}</text>`;

    const marks = labels(m).map((l) =>
      text(l.x, l.y, l.text, 9.5, l.colour === "gold" ? gold : muted, "end")).join("");

    return (
      `<svg class="sp-figure" viewBox="0 0 ${box.w} ${box.h}" ` +
      `xmlns="http://www.w3.org/2000/svg" role="img" ` +
      `aria-label="Two thin border pillars, one line each, with a base, a swelling shaft and a capital">` +
      `<rect x="0" y="0" width="${box.w}" height="${box.h}" fill="${paper}"/>` +
      // model axes: the ground and the centre line, as guides only
      `<line class="guide" x1="${svgX(-HALF_PAGE + 10)}" y1="${svgY(0)}" ` +
      `x2="${svgX(HALF_PAGE - 10)}" y2="${svgY(0)}" stroke="${guide}" stroke-width="1"/>` +
      `<line class="guide" x1="${svgX(0)}" y1="${svgY(0)}" x2="${svgX(0)}" y2="${svgY(H)}" ` +
      `stroke="${guide}" stroke-width="1" stroke-dasharray="3 5"/>` +
      // the glue-connected top border, shown as a context dash
      `<line class="border" x1="${svgX(-PLINTH_SHARE * m.d0 - AXIS_X)}" y1="${svgY(H)}" ` +
      `x2="${svgX(AXIS_X - PLINTH_SHARE * m.d0)}" y2="${svgY(H)}" ` +
      `stroke="${gold}" stroke-width="1.4" stroke-dasharray="7 5"/>` +
      `<circle cx="${svgX(AXIS_X - PLINTH_SHARE * m.d0)}" cy="${svgY(H)}" r="2" fill="${gold}"/>` +
      `<circle cx="${svgX(-AXIS_X + PLINTH_SHARE * m.d0)}" cy="${svgY(H)}" r="2" fill="${gold}"/>` +
      // the one place y is flipped: model units (y up) to SVG units (y down)
      `<g transform="translate(${HALF_PAGE} ${H + TOP_MARGIN}) scale(1 -1)" ` +
      `fill="none" stroke-linejoin="round">` +
      `<path class="taper" d="${taper(AXIS_X)}" stroke="${guide}" stroke-width="1" stroke-dasharray="2 3"/>` +
      `<path class="taper" d="${taper(-AXIS_X)}" stroke="${guide}" stroke-width="1" stroke-dasharray="2 3"/>` +
      `<path class="pillar" d="${right}" stroke="${ink}" stroke-width="1.8"/>` +
      `<path class="pillar" d="${left}" stroke="${ink}" stroke-width="1.8"/>` +
      `<line class="setback" x1="${AXIS_X + m.x0}" y1="${m.y0}" x2="${-AXIS_X - m.x0}" y2="${m.y0}" ` +
      `stroke="${guide}" stroke-width="0.8" stroke-dasharray="1 4"/>` +
      `</g>` +
      marks +
      text(-HALF_PAGE + 12, H + 52, "Fig. P1 — the side pillar, one line each", 11, ink) +
      text(-HALF_PAGE + 12, H + 36, "dashed: the glue-connected run. dotted: the straight taper the shaft swells against", 8.5, muted) +
      text(HALF_PAGE - 12, -18, "x", 10, muted, "end") +
      text(5, H + 4, "y", 10, muted) +
      `</svg>`
    );
  }

  // Every printed number, with the words that say what it measures.
  function readout(raw) {
    const m = model(raw);
    const c = m.c;
    return [
      { key: "height", label: "height in foot widths (diameters)", value: String(c.diameters) },
      { key: "foot", label: "foot width, as a share of the height", value: `1/${c.diameters} H` },
      { key: "top", label: "top width, as a share of the foot", value: hundredths(c.ratio) },
      {
        key: "topwidth",
        label: "top width, as a fraction of the height (model units)",
        value: `${hundredths(c.ratio)} × 1/${c.diameters} H`,
      },
      {
        key: "swell",
        label: "swell above the taper line, as a share of the foot",
        value: hundredths(c.swell),
      },
      { key: "station", label: "swell station, as a share of the height", value: hundredths(c.station) },
      { key: "base", label: "base height, in foot widths", value: hundredths(c.base) },
      { key: "capital", label: "capital height, in foot widths", value: hundredths(c.capital) },
      {
        key: "widest",
        label: "widest point of the shaft",
        value: "the foot (checked at every station)",
      },
    ];
  }

  // The twelve rules that can fail, measured on the model.
  function checks(raw) {
    const m = model(raw);
    const samples = 200;
    let footWidest = true;
    let swellSeen = -Infinity;
    for (let i = 0; i <= samples; i += 1) {
      const t = i / samples;
      const x = shaftX(m, t);
      if (x > m.x0 + 1e-9) footWidest = false;
      const above = x - shaftLineX(m, t);
      if (above > swellSeen) swellSeen = above;
    }
    const b = bbox(m);
    return {
      thin: m.d0 / H <= 1 / 24 + 1e-12,
      taper: m.dt <= m.x0 * 2 * 0.95 + 1e-12,
      swellAboveLine: swellSeen > 0,
      swellAtMostSix: m.c.swell <= 6,
      footWidest,
      baseStandsProud: PLINTH_SHARE * m.d0 > m.x0,
      capitalStandsProud: PLINTH_SHARE * m.d0 > m.x2,
      insideBox: b.left > -HALF_PAGE + 2 && b.right < HALF_PAGE - 2 && b.top <= H && b.bottom >= 0,
      swellCeiling: swellCeiling(m.c.ratio),
    };
  }

  // Wire the six controls to the figure and the readout. One line of maths per
  // control: the value goes into the model and every number is recomputed.
  function mount(doc) {
    const ids = ["diameters", "ratio", "swell", "station", "base", "capital"];
    const input = {};
    for (const id of ids) input[id] = doc.getElementById("sp-" + id);
    const figure = doc.getElementById("sp-figure");
    const rows = doc.getElementById("sp-readout");
    const notes = doc.getElementById("sp-notes");

    function draw() {
      const raw = {};
      for (const id of ids) raw[id] = Number(input[id].value);
      const c = controls(raw);
      input.swell.max = String(swellCeiling(c.ratio));
      if (Number(input.swell.value) > Number(input.swell.max)) {
        input.swell.value = input.swell.max;
        c.swell = Number(input.swell.max);
      }
      for (const id of ids) {
        const out = doc.getElementById("sp-" + id + "-val");
        if (out) out.textContent = id === "diameters" ? String(c[id]) : hundredths(c[id]);
      }
      figure.innerHTML = svgMarkup(c);
      rows.innerHTML = readout(c)
        .map((r) => `<tr><th>${r.label}</th><td>${r.value}</td></tr>`)
        .join("");
      const k = checks(c);
      notes.textContent =
        `swell ceiling ${k.swellCeiling}/100 of the foot at this taper ` +
        `(a quadratic that swells further would make the foot no longer the widest point)`;
    }

    for (const id of ids) input[id].addEventListener("input", draw);
    draw();
    return draw;
  }

  return {
    H,
    DEFAULTS,
    LIMITS,
    controls,
    model,
    stations,
    shaftX,
    shaftY,
    shaftLineX,
    pillarPath,
    bbox,
    svgMarkup,
    labels,
    readout,
    checks,
    swellCeiling,
    hundredths,
    mount,
  };
});
