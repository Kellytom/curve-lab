/* T1 — the 24 triangles and 25 integer vertices, drawn with d3.
   Data comes from the page as T1: verts, steps, curve, hits, pitch.
   Model y is up; d3's y scale reverses the range, so the flip happens there.

   The curve is in the algebraic orientation: the node at the origin, the loop
   along +x, the arms to the right. So the labels sit above the upper arm and
   below the lower arm. Where the vertices crowd near the nose a label steps
   outward a row at a time until its measured box is clear of every other text
   box in the figure, and a leader line ties it back to its vertex.
   `audit_t1.mjs` measures the rendered boxes and counts overlaps. */

(function () {
  const W = 729, H = 982;
  const M = { top: 56, right: 31, bottom: 86, left: 74 };

  // 0.24 px per cell on both axes, so the drawing is not stretched.
  const x = d3.scaleLinear().domain([-200, 2400])
    .range([M.left, W - M.right]);
  const y = d3.scaleLinear().domain([-1750, 1750])
    .range([H - M.bottom, M.top]);

  const svg = d3.select("#t1").append("svg")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .attr("width", "100%")
    .attr("role", "img")
    .attr("aria-label", "the trapezoid chain on the integer grid, cells")
    .style("background", "#fbf7ec")
    .style("border", "1px solid #d8ccae")
    .style("font-family", "Georgia, serif");

  const P = T1.pitch;                       // 256 cells per unit

  // title, inside the figure
  svg.append("text").attr("x", M.left).attr("y", 22)
    .attr("font-size", 14).attr("font-weight", 600).attr("fill", "#2e2413")
    .text("Fig. T1 — the Tschirnhausen cubic: 24 triangles, 25 integer vertices");
  svg.append("text").attr("x", M.left).attr("y", 40)
    .attr("font-size", 12).attr("fill", "#7b6c4e")
    .text(`9y² = x(x−3)² · pitch ${P} cells per unit · the loop lies along +x`);

  // grid: every unit, pale, and the axes themselves
  const gx = d3.range(0, 10).map(k => k * P);
  const gy = d3.range(-6, 7).map(k => k * P);

  svg.append("g").selectAll("line").data(gx).enter().append("line")
    .attr("x1", d => x(d)).attr("x2", d => x(d))
    .attr("y1", y(-1750)).attr("y2", y(1750))
    .attr("stroke", "#ddd3b8").attr("stroke-width", 1);
  svg.append("g").selectAll("line").data(gy).enter().append("line")
    .attr("y1", d => y(d)).attr("y2", d => y(d))
    .attr("x1", x(-200)).attr("x2", x(2400))
    .attr("stroke", "#ddd3b8").attr("stroke-width", 1);

  // axes in cells: x along the bottom, y up the x = 0 line
  svg.append("g").attr("transform", `translate(0,${y(-1750)})`)
    .call(d3.axisBottom(x).tickValues(d3.range(0, 2305, 512))
      .tickFormat(d3.format(",")))
    .call(g => g.selectAll("text").attr("font-size", 12).attr("fill", "#7b6c4e"));
  svg.append("g").attr("transform", `translate(${x(0)},0)`)
    .call(d3.axisLeft(y).tickValues(d3.range(-1536, 1537, 512))
      .tickFormat(d3.format(",")))
    .call(g => g.selectAll("text").attr("font-size", 12).attr("fill", "#7b6c4e"));

  svg.append("text").attr("x", x(2400) - 4).attr("y", y(-1750) - 10)
    .attr("font-size", 13).attr("fill", "#2e2413").attr("text-anchor", "end")
    .text("x, cells");
  svg.append("text").attr("transform", `translate(30,${(M.top + H - M.bottom) / 2}) rotate(-90)`)
    .attr("font-size", 13).attr("fill", "#2e2413").attr("text-anchor", "middle")
    .text("y, cells");

  // step legs: an L from each vertex to the next
  const legs = svg.append("g");
  T1.steps.forEach((st, i) => {
    const a = T1.verts[i], b = T1.verts[i + 1];
    legs.append("polyline")
      .attr("points", `${x(a[0])},${y(a[1])} ${x(b[0])},${y(a[1])} ${x(b[0])},${y(b[1])}`)
      .attr("fill", "none").attr("stroke", "#9bb7d4").attr("stroke-width", 0.9);
  });

  const line = d3.line().x(d => x(d[0])).y(d => y(d[1]));

  svg.append("path").attr("d", line(T1.curve))
    .attr("fill", "none").attr("stroke", "#7a6a4a").attr("stroke-width", 2.2);

  svg.append("path").attr("d", line(T1.verts))
    .attr("fill", "none").attr("stroke", "#2e2413").attr("stroke-width", 2.4);

  // ---- geometry helpers, in SVG user units --------------------------------
  const root = svg.node();
  const ROOT_CTM = root.getScreenCTM();
  function rootBox(el) {
    const b = el.getBBox();
    // getScreenCTM is in CSS px; the difference is the user-unit matrix.
    const m = ROOT_CTM.inverse().multiply(el.getScreenCTM());
    const pts = [
      [b.x, b.y], [b.x + b.width, b.y],
      [b.x, b.y + b.height], [b.x + b.width, b.y + b.height],
    ].map(([px, py]) => new DOMPoint(px, py).matrixTransform(m));
    const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
    return { x: Math.min(...xs), y: Math.min(...ys),
             w: Math.max(...xs) - Math.min(...xs),
             h: Math.max(...ys) - Math.min(...ys) };
  }
  const overlap = (a, b) =>
    Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x) > 0 &&
    Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y) > 0;

  // everything already drawn is an obstacle: title, ticks, axis labels, legend
  const obstacles = [...root.querySelectorAll("text")].map(rootBox);

  // the 25 integer vertices. up = label above, down = below, left = nose.
  const labels = T1.verts.map((p, i) => {
    const side = i === 12 ? "left" : p[1] > 0 ? "up" : "down";
    return { i, p, side, px: x(p[0]), py: y(p[1]),
             text: `(${p[0]}, ${p[1]})` };
  });

  const leaders = svg.append("g").attr("class", "leaders");
  const vg = svg.append("g").attr("class", "vlabels");
  labels.forEach(L => {
    L.node = vg.append("text")
      .attr("class", "vlabel")
      .attr("data-i", L.i)
      .attr("x", 0).attr("y", 0)
      .attr("font-size", 10)
      .attr("dominant-baseline", "middle")
      .attr("fill", "#5c4d33")
      .attr("paint-order", "stroke")
      .attr("stroke", "#fbf7ec")
      .attr("stroke-width", 2.4)
      .attr("stroke-linejoin", "round")
      .text(L.text);
    const b = rootBox(L.node.node());
    L.w = b.w;
    L.h = b.h;
  });

  const placed = [];
  function clear(box) {
    if (box.x < 4 || box.x + box.w > W - 4) return false;
    if (box.y < 6 || box.y + box.h > y(-1750) - 2) return false;
    if (obstacles.some(o => overlap(box, o))) return false;
    return !placed.some(o => overlap(box, o));
  }

  labels.forEach(L => {
    let found = null;
    for (let k = 0; k < 80 && !found; k++) {
      let cx, cy, box, anchor;
      if (L.side === "up") {
        cx = L.px; cy = L.py - 10 - 13 * k; anchor = "middle";
        box = { x: cx - L.w / 2, y: cy - L.h / 2, w: L.w, h: L.h };
      } else if (L.side === "down") {
        cx = L.px; cy = L.py + 10 + 13 * k; anchor = "middle";
        box = { x: cx - L.w / 2, y: cy - L.h / 2, w: L.w, h: L.h };
      } else {
        cx = L.px - 7 - 9 * k; cy = L.py; anchor = "end";
        box = { x: cx - L.w, y: cy - L.h / 2, w: L.w, h: L.h };
      }
      if (clear(box)) found = { cx, cy, box, anchor, k };
    }
    if (!found) {                                  // never in practice; keep it visible
      const cx = L.px, cy = L.side === "up" ? L.py - 10 : L.py + 10;
      found = { cx, cy, anchor: "middle", k: 0,
                box: { x: cx - L.w / 2, y: cy - L.h / 2, w: L.w, h: L.h } };
    }
    L.node.attr("x", found.cx).attr("y", found.cy)
      .attr("text-anchor", found.anchor);
    placed.push(found.box);
    if (found.k > 0) {
      const bx = found.box;
      const ex = found.anchor === "end" ? bx.x + bx.w : bx.x + bx.w / 2;
      const ey = found.anchor === "end" ? bx.y + bx.h / 2
        : L.side === "up" ? bx.y + bx.h : bx.y;
      leaders.append("line")
        .attr("x1", L.px).attr("y1", L.py)
        .attr("x2", ex).attr("y2", ey)
        .attr("stroke", "#b9a67f").attr("stroke-width", 0.7)
        .attr("stroke-dasharray", "2 2");
    }
  });

  // the four parameters where the curve meets the lattice. The letter sits
  // clear of its ring and of every text box, with a halo for legibility.
  const RINGS = T1.hits.map(h => ({
    x: x(h[0]) - 10, y: y(h[1]) - 10, w: 20, h: 20,
  }));
  const CAND = [[0, -26], [0, 26], [-26, 0], [26, 0],
                [-26, -20], [-26, 20], [26, -20], [26, 20]];
  const hits = svg.append("g");
  T1.hits.forEach(h => {
    const cx = x(h[0]), cy = y(h[1]);
    hits.append("circle").attr("class", "hitring")
      .attr("cx", cx).attr("cy", cy).attr("r", 9)
      .attr("fill", "none").attr("stroke", "#a23b2a").attr("stroke-width", 2);
    const node = hits.append("text").attr("class", "hitlabel")
      .attr("x", cx).attr("y", cy)
      .attr("font-size", 14).attr("font-weight", 600).attr("fill", "#a23b2a")
      .attr("paint-order", "stroke")
      .attr("stroke", "#fbf7ec").attr("stroke-width", 3).text(h[2]);
    const b = rootBox(node.node());
    const boxAt = (dx, dy) => ({
      x: cx + dx - b.w / 2, y: cy + dy - b.h / 2, w: b.w, h: b.h,
    });
    const ok = ([dx, dy]) =>
      !RINGS.some(r => overlap(boxAt(dx, dy), r)) &&
      !obstacles.some(o => overlap(boxAt(dx, dy), o)) &&
      !placed.some(o => overlap(boxAt(dx, dy), o));
    const pick = CAND.find(ok) || CAND[0];
    node.attr("x", cx + pick[0]).attr("y", cy + pick[1])
      .attr("text-anchor", "middle");
    placed.push(boxAt(...pick));
  });

  // legend, two rows at 15px so it stays readable at full width
  const items = [
    ["#7a6a4a", 2.2, "smooth curve"],
    ["#2e2413", 2.4, "chain, 24 sides, 25 integer vertices"],
    ["#9bb7d4", 1.2, "step legs"],
    ["#a23b2a", 2, "curve meets the lattice (A–D)"],
    ["#ddd3b8", 1.2, `grid: one unit = ${P} cells`],
  ];
  items.forEach((it, k) => {
    const row = k < 3 ? 0 : 1;
    const col = row === 0 ? k : k - 3;
    const o = row === 0 ? [0, 130, 410][col] : [0, 260][col];
    const L = svg.append("g")
      .attr("transform", `translate(${M.left + 10 + o},${H - 48 + row * 26})`);
    L.append("line").attr("x1", 0).attr("x2", 22).attr("y1", 0).attr("y2", 0)
      .attr("stroke", it[0]).attr("stroke-width", it[1]);
    L.append("text").attr("x", 29).attr("y", 5).attr("font-size", 15)
      .attr("fill", "#2e2413").text(it[2]);
  });
})();
