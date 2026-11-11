// ph-families-app.js — generated into workbench/ by scripts/ph_families.py.
// Source: scripts/ph_families_app.js. Do not edit the workbench copy.
//
// The interactive explainer for the PH family page. Everything the readout
// claims is computed here: the curve from the generators, the exact milestone
// scale in BigInt rationals, the rational PH normal, a fitted normal, and the
// speed identity that "break PH" destroys.
(function () {
  "use strict";
  var PRESETS = window.PH_PRESETS || [];
  var $ = function (id) { return document.getElementById(id); };

  // ---------------------------------------------------------------- rationals
  var B = BigInt;
  function gcd(a, b) {
    a = a < 0n ? -a : a; b = b < 0n ? -b : b;
    while (b) { var t = a % b; a = b; b = t; }
    return a;
  }
  function rnorm(n, d) {
    if (d < 0n) { n = -n; d = -d; }
    var g = gcd(n, d) || 1n;
    return { n: n / g, d: d / g };
  }
  function radd(a, b) { return rnorm(a.n * b.d + b.n * a.d, a.d * b.d); }
  function rmul(a, b) { return rnorm(a.n * b.n, a.d * b.d); }
  function binomBig(n, k) {
    var r = 1n;
    for (var i = 1n; i <= B(k); i++) r = r * (B(n) - B(k) + i) / i;
    return r;
  }
  function ipow(m, k) {
    var r = 1n;
    for (var i = 0; i < k; i++) r *= B(m);
    return r;
  }
  function conv(a, b) {
    var out = new Array(a.length + b.length - 1).fill(0);
    for (var i = 0; i < a.length; i++)
      for (var j = 0; j < b.length; j++) out[i + j] += a[i] * b[j];
    return out;
  }

  // Control points of z, exactly: hodograph power basis → integrate → Bernstein.
  // Returns { n, cp: [[{n,d},{n,d}], ...] } with BigInt rationals.
  function controlPoints(h, u, v) {
    var n = (h.length - 1) + 2 * (Math.max(u.length, v.length) - 1) + 1;
    var uu = conv(u, u), vv = conv(v, v), uv = conv(u, v);
    var width = Math.max(uu.length, vv.length);
    var xd = [], yd = [], i;
    for (i = 0; i < width; i++) {
      xd.push((uu[i] || 0) - (vv[i] || 0));
      yd.push(2 * (uv[i] || 0));
    }
    var hx = conv(h, xd), hy = conv(h, yd);
    var cp = [];
    for (i = 0; i <= n; i++) {
      var sx = { n: 0n, d: 1n }, sy = { n: 0n, d: 1n };
      for (var j = 0; j <= i; j++) {
        var f = rnorm(binomBig(i, j), binomBig(n, j));
        if (j > 0) {
          sx = radd(sx, rmul(f, { n: B(hx[j - 1] || 0), d: B(j) }));
          sy = radd(sy, rmul(f, { n: B(hy[j - 1] || 0), d: B(j) }));
        }
      }
      cp.push([sx, sy]);
    }
    return { n: n, cp: cp };
  }

  function milestones(cp, n, m) {
    var mpow = ipow(m, n), out = [], k, i;
    for (k = 0; k <= m; k++) {
      var sx = { n: 0n, d: 1n }, sy = { n: 0n, d: 1n };
      for (i = 0; i <= n; i++) {
        var w = { n: binomBig(n, i) * ipow(k, i) * ipow(m - k, n - i), d: mpow };
        sx = radd(sx, rmul(w, cp[i][0]));
        sy = radd(sy, rmul(w, cp[i][1]));
      }
      out.push([sx, sy]);
    }
    return out;
  }

  // The least common scale that puts every control point and milestone on ℤ.
  function scaleAndHits(h, u, v, m) {
    var got = controlPoints(h, u, v);
    var vals = [], i, k;
    for (i = 0; i < got.cp.length; i++) { vals.push(got.cp[i][0], got.cp[i][1]); }
    var ms = milestones(got.cp, got.n, m);
    for (k = 0; k < ms.length; k++) { vals.push(ms[k][0], ms[k][1]); }
    var L = 1n;
    for (i = 0; i < vals.length; i++) L = L / gcd(L, vals[i].d) * vals[i].d;
    var g = 0n;
    for (i = 0; i < vals.length; i++) g = gcd(g, vals[i].n * (L / vals[i].d));
    var scale = L / (g || 1n);
    var seen = {};
    for (k = 0; k < ms.length; k++) {
      seen[String(ms[k][0].n * scale / ms[k][0].d) + "," +
           String(ms[k][1].n * scale / ms[k][1].d)] = true;
    }
    return { n: got.n, scale: scale, hits: Object.keys(seen).length, cp: got.cp };
  }

  // ------------------------------------------------------------------ geometry
  function num(r) { return Number(r.n) / Number(r.d); }
  function floatCp(got) { return got.cp.map(function (p) { return [num(p[0]), num(p[1])]; }); }

  function evalCp(cp, t) {
    // de Casteljau
    var pts = cp.slice(), n = pts.length - 1;
    for (var r = 1; r <= n; r++)
      for (var i = 0; i <= n - r; i++)
        pts[i] = [pts[i][0] * (1 - t) + pts[i + 1][0] * t,
                  pts[i][1] * (1 - t) + pts[i + 1][1] * t];
    return pts[0];
  }
  function polyAt(coeffs, t) {
    var s = 0;
    for (var i = coeffs.length - 1; i >= 0; i--) s = s * t + coeffs[i];
    return s;
  }

  function samplePath(cp, t0, t1, steps) {
    var out = [];
    for (var i = 0; i <= steps; i++) {
      var t = t0 + (t1 - t0) * i / steps;
      out.push({ t: t, p: evalCp(cp, t) });
    }
    return out;
  }

  function exactOffset(cp, u, v, d, t0, t1, steps) {
    var out = [];
    for (var i = 0; i <= steps; i++) {
      var t = t0 + (t1 - t0) * i / steps;
      var p = evalCp(cp, t);
      var uu = polyAt(u, t), vv = polyAt(v, t);
      var den = uu * uu + vv * vv;
      var nx = -2 * uu * vv / den, ny = (uu * uu - vv * vv) / den;
      out.push([p[0] + d * nx, p[1] + d * ny]);
    }
    return out;
  }

  // A fitted offset: the normals come from the sampled polyline, not the
  // hodograph. This is the honest "non-PH" route and it ripples where the
  // curvature is high.
  function fittedOffset(samples, d) {
    var segs = [];
    for (var i = 0; i + 1 < samples.length; i++) {
      var a = samples[i].p, b = samples[i + 1].p;
      var dx = b[0] - a[0], dy = b[1] - a[1];
      var len = Math.hypot(dx, dy) || 1;
      segs.push([-dy / len, dx / len]);
    }
    var out = [];
    for (i = 0; i < samples.length; i++) {
      var n1 = segs[Math.max(0, i - 1)], n2 = segs[Math.min(segs.length - 1, i)];
      var nx = n1[0] + n2[0], ny = n1[1] + n2[1];
      var nn = Math.hypot(nx, ny) || 1;
      out.push([samples[i].p[0] + d * nx / nn, samples[i].p[1] + d * ny / nn]);
    }
    return out;
  }

  // |z'|² from the drawn control points vs the polynomial σ = h (u² + v²).
  function speedResidual(cp, h, u, v, t0, t1) {
    var n = cp.length - 1, worst = 0;
    for (var i = 1; i < 40; i++) {
      var t = t0 + (t1 - t0) * i / 40;
      // derivative control points of a Bézier
      var dcp = [];
      for (var k = 0; k < n; k++)
        dcp.push([n * (cp[k + 1][0] - cp[k][0]), n * (cp[k + 1][1] - cp[k][1])]);
      var d = evalCp(dcp, t);
      var uu = polyAt(u, t), vv = polyAt(v, t);
      var sigma = polyAt(h, t) * (uu * uu + vv * vv);
      var lhs = d[0] * d[0] + d[1] * d[1];
      var err = Math.abs(lhs - sigma * sigma) / Math.max(1e-12, Math.abs(sigma * sigma));
      if (err > worst) worst = err;
    }
    return worst;
  }

  // -------------------------------------------------------------------- drawing
  var W = 560, H = 420, PADL = 46, PADR = 14, PADT = 42, PADB = 34;

  function niceStep(span) {
    var steps = [0.1, 0.2, 0.25, 0.5, 1, 2, 5, 10, 20, 50];
    for (var i = 0; i < steps.length; i++) if (span / steps[i] <= 9) return steps[i];
    return 100;
  }

  function draw(state) {
    var quad = state.quad, paths = [], xs = [], ys = [], q, i;
    for (q = 0; q < quad.length; q++) {
      for (i = 0; i < quad[q].pts.length; i++) { xs.push(quad[q].pts[i][0]); ys.push(quad[q].pts[i][1]); }
      for (i = 0; i < (quad[q].offs || []).length; i++) { xs.push(quad[q].offs[i][0]); ys.push(quad[q].offs[i][1]); }
    }
    if (!xs.length) { return "<p>nothing selected</p>"; }
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
    var y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
    var pad = 0.08 * Math.max(x1 - x0, y1 - y0, 1e-6);
    x0 -= pad; x1 += pad; y0 -= pad; y1 += pad;
    var s = Math.min((W - PADL - PADR) / (x1 - x0), (H - PADT - PADB) / (y1 - y0));
    var ox = (W - (x1 - x0) * s) / 2 - x0 * s;
    var oy = (H - (y1 - y0) * s) / 2 + y1 * s;   // +y up in model, flipped here
    var F = function (p) { return [ox + p[0] * s, oy - p[1] * s]; };

    var step = niceStep(Math.max(x1 - x0, y1 - y0));
    var grid = [], g;
    for (g = Math.floor(x0 / step) * step; g <= x1; g += step) {
      var a = F([g, y0]), b = F([g, y1]);
      grid.push('<line x1="' + a[0].toFixed(1) + '" y1="' + a[1].toFixed(1) +
                '" x2="' + b[0].toFixed(1) + '" y2="' + b[1].toFixed(1) +
                '" stroke="#d8ccae" stroke-width="0.6"/>');
    }
    for (g = Math.floor(y0 / step) * step; g <= y1; g += step) {
      a = F([x0, g]); b = F([x1, g]);
      grid.push('<line x1="' + a[0].toFixed(1) + '" y1="' + a[1].toFixed(1) +
                '" x2="' + b[0].toFixed(1) + '" y2="' + b[1].toFixed(1) +
                '" stroke="#d8ccae" stroke-width="0.6"/>');
    }
    var ym = (y0 <= 0 && y1 >= 0) ? 0 : y0;
    var xm = (x0 <= 0 && x1 >= 0) ? 0 : x0;
    var ax = F([x0, ym]), bx = F([x1, ym]), ay = F([xm, y0]), by = F([xm, y1]);
    var axes = '<line x1="' + ax[0].toFixed(1) + '" y1="' + ax[1].toFixed(1) +
               '" x2="' + bx[0].toFixed(1) + '" y2="' + bx[1].toFixed(1) +
               '" stroke="#1f5fa8" stroke-width="0.9"/>' +
               '<text x="' + (bx[0] - 10).toFixed(1) + '" y="' + (bx[1] - 4).toFixed(1) +
               '" font-size="10" fill="#1f5fa8">x</text>' +
               '<line x1="' + ay[0].toFixed(1) + '" y1="' + ay[1].toFixed(1) +
               '" x2="' + by[0].toFixed(1) + '" y2="' + by[1].toFixed(1) +
               '" stroke="#1f5fa8" stroke-width="0.9"/>' +
               '<text x="' + (by[0] + 5).toFixed(1) + '" y="' + (by[1] + 10).toFixed(1) +
               '" font-size="10" fill="#1f5fa8">y</text>';

    function pathOf(pts, stroke, width, dash) {
      var d = [];
      for (var i = 0; i < pts.length; i++) {
        var p = F(pts[i]);
        d.push((i ? "L" : "M") + p[0].toFixed(2) + "," + p[1].toFixed(2));
      }
      return '<path d="' + d.join(" ") + '" fill="none" stroke="' + stroke +
             '" stroke-width="' + width + '"' + (dash ? ' stroke-dasharray="' + dash + '"' : "") + '/>';
    }

    for (q = 0; q < quad.length; q++) {
      var fade = quad[q].primary ? 1 : 0.45;
      paths.push('<g opacity="' + fade + '">' + pathOf(quad[q].pts, "#2e2413", quad[q].primary ? 2.2 : 1.2) + '</g>');
      if (quad[q].offs && quad[q].offs.length)
        paths.push('<g opacity="' + fade + '">' + pathOf(quad[q].offs, "#c9a441", 1.6, "5 4") + '</g>');
      if (quad[q].fit && quad[q].fit.length)
        paths.push('<g opacity="' + fade + '">' + pathOf(quad[q].fit, "#a23b2a", 1.4, "2 3") + '</g>');
    }

    var dots = "";
    if (state.dots && state.dots.length) {
      for (var k = 0; k < state.dots.length; k++) {
        var dp = F(state.dots[k]);
        dots += '<circle cx="' + dp[0].toFixed(1) + '" cy="' + dp[1].toFixed(1) +
                '" r="2.6" fill="#1f5fa8"/>';
      }
    }

    var text = '<text x="10" y="17" font-family="ui-sans-serif,system-ui,sans-serif" font-size="12" font-weight="600" fill="#2e2413">' +
      state.title + '</text>' +
      '<text x="10" y="31" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="#7b6c4e">' +
      state.sub + '</text>' +
      '<text x="10" y="' + (H - 20) + '" font-family="ui-sans-serif,system-ui,sans-serif" font-size="9" fill="#7b6c4e">' +
      'legend: black PH curve · gold dashed exact PH offset · red dotted fitted offset</text>' +
      '<text x="10" y="' + (H - 8) + '" font-family="ui-monospace,Menlo,monospace" font-size="8.6" fill="#7b6c4e">' +
      'x ' + x0.toFixed(2) + '…' + x1.toFixed(2) + ' · y ' + y0.toFixed(2) + '…' + y1.toFixed(2) + ' · +y up</text>';

    return '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" role="img" aria-label="PH sliders">' +
      '<rect width="' + W + '" height="' + H + '" fill="#fbf7ec"/>' +
      grid.join("") + axes + paths.join("") + dots + text + '</svg>';
  }

  // --------------------------------------------------------------------- state
  var state = { preset: null, m: 4, d: 0.25, qx: true, qy: true, brk: false, co: null };

  function readCoeffs() {
    var p = state.preset, u = [], v = [], i;
    for (i = 0; i < 4; i++) {
      u.push(i < p.u.length ? Number($("u" + i).value) : 0);
      v.push(i < p.v.length ? Number($("v" + i).value) : 0);
    }
    return { h: p.h.slice(), u: u, v: v };
  }

  function zeroTail(a) {
    var out = a.slice();
    while (out.length > 1 && out[out.length - 1] === 0) out.pop();
    return out;
  }

  function update() {
    var p = state.preset;
    var got = readCoeffs();
    var h = zeroTail(got.h), u = zeroTail(got.u), v = zeroTail(got.v);
    if (u.length === 1 && v.length === 1) { $("readout").textContent = "u and v are both constant: a straight line, not a curve."; return; }
    var exact = scaleAndHits(h, u, v, state.m);
    var cp = floatCp(exact);
    if (state.brk) {
      // a declared perturbation: 12% of the bounding size, so the identity
      // breaks by a number the reader can see without the curve running away
      var xsB = cp.map(function (q) { return q[0]; });
      var ysB = cp.map(function (q) { return q[1]; });
      var span = Math.max(Math.max.apply(null, xsB) - Math.min.apply(null, xsB),
                          Math.max.apply(null, ysB) - Math.min.apply(null, ysB), 1e-6);
      var mid = Math.floor(cp.length / 2);
      cp[mid] = [cp[mid][0] + 0.12 * span, cp[mid][1] - 0.09 * span];
    }
    var samples = samplePath(cp, p.t0, p.t1, 160);
    var pts = samples.map(function (s) { return s.p; });
    var offs = state.d > 0 && !state.brk ? exactOffset(cp, u, v, state.d, p.t0, p.t1, 160) : [];
    var fit = state.d > 0 ? fittedOffset(samples, state.d) : [];
    var quad = [];
    var mirrors = [[1, 1, true], [-1, 1, false], [1, -1, false], [-1, -1, false]];
    for (var i = 0; i < mirrors.length; i++) {
      var sx = mirrors[i][0], sy = mirrors[i][1];
      if (sx < 0 && !state.qx) continue;
      if (sy < 0 && !state.qy) continue;
      quad.push({
        primary: i === 0,
        pts: pts.map(function (q) { return [sx * q[0], sy * q[1]]; }),
        offs: offs.map(function (q) { return [sx * q[0], sy * q[1]]; }),
        fit: fit.map(function (q) { return [sx * q[0], sy * q[1]]; })
      });
    }
    var residual = speedResidual(cp, h, u, v, p.t0, p.t1);
    var sub = "n=" + exact.n + " · h=(" + h.join(",") + ") · u=(" + u.join(",") + ") · v=(" + v.join(",") + ")";
    var dots = [];
    for (var m = 0; m <= state.m; m++) {
      var t = p.t0 + (p.t1 - p.t0) * m / state.m;
      dots.push(evalCp(cp, t));
    }
    $("stage").innerHTML = draw({
      title: p.name + " · scale " + exact.scale.toString() + " at m=" + state.m,
      sub: sub, quad: quad, dots: dots
    });
    var ident = state.brk
      ? "<b>speed identity broken</b>: |z'|² ≠ σ² by " + (residual * 100).toFixed(2) + "%"
      : "speed identity exact";
    $("readout").innerHTML =
      "hits <b>" + exact.hits + "</b> at m=" + state.m +
      " · scale <b>" + exact.scale.toString() + "</b>" +
      " · d=" + state.d.toFixed(2) +
      " · " + ident +
      (state.d > 0 && !state.brk ? " · exact offset: gold dashed, fitted: red dotted" : "");
  }

  function syncLabels() {
    ["m", "d", "u0", "u1", "u2", "u3", "v0", "v1", "v2", "v3"].forEach(function (k) {
      var el = $(k), lab = $(k + "v");
      if (el && lab) lab.textContent = el.value;
    });
  }

  function loadPreset(key) {
    var p = PRESETS.filter(function (x) { return x.key === key; })[0] || PRESETS[0];
    state.preset = p;
    for (var i = 0; i < 4; i++) {
      var ui = $("u" + i), vi = $("v" + i);
      var uv = i < p.u.length ? p.u[i] : 0;
      var vv = i < p.v.length ? p.v[i] : 0;
      ui.value = uv; ui.disabled = i >= p.u.length;
      vi.value = vv; vi.disabled = i >= p.v.length;
    }
    syncLabels();
  }

  function init() {
    var sel = $("preset");
    PRESETS.forEach(function (p) {
      var o = document.createElement("option");
      o.value = p.key; o.textContent = p.name;
      sel.appendChild(o);
    });
    sel.addEventListener("change", function () { loadPreset(sel.value); update(); });
    ["m", "d", "u0", "u1", "u2", "u3", "v0", "v1", "v2", "v3"].forEach(function (k) {
      var el = $(k);
      if (el) el.addEventListener("input", function () {
        if (k === "m") state.m = Number(el.value);
        else if (k === "d") state.d = Number(el.value);
        syncLabels(); update();
      });
    });
    $("qx").addEventListener("change", function () { state.qx = this.checked; update(); });
    $("qy").addEventListener("change", function () { state.qy = this.checked; update(); });
    $("brk").addEventListener("change", function () { state.brk = this.checked; update(); });
    loadPreset(PRESETS[0].key);
    update();
  }

  // exposed for the browser check and for a node test
  window.PH_APP = { controlPoints: controlPoints, scaleAndHits: scaleAndHits,
                    speedResidual: speedResidual, state: state, update: update,
                    loadPreset: loadPreset };

  if (window.PH_NO_INIT) return;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
