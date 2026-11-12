/* T1 — the 24 triangles and 25 integer vertices, drawn with d3.
   Data comes from the page as T1: verts, steps, curve, hits, pitch.
   Model y is up; d3's y scale reverses the range, so the flip happens there.

   Labels: each vertex label sits in a left or right column (the side away from
   the loop; the two tips label inward, because the outer edge is the page
   edge), then a one-dimensional spread keeps every pair of boxes apart inside
   its column. A displaced label gets a leader line back to its vertex.
   `audit_t1.mjs` measures the rendered boxes and counts overlaps. */

(function () {
  const W = 980, H = 820;
  const M = { top: 46, right: 31, bottom: 74, left: 74 };

  // 0.25 px per cell on both axes, so the drawing is not stretched.
  const x = d3.scaleLinear().domain([-1750, 1750])
    .range([M.left, W - M.right]);
  const y = d3.scaleLinear().domain([-250, 2550])
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
  svg.append("text").attr("x", M.left).attr("y", 24)
    .attr("font-size", 15).attr("font-weight", 600).attr("fill", "#2e2413")
    .text("Fig. T1 — the Tschirnhausen cubic: 24 triangles, 25 integer vertices, "
      + `pitch ${P} cells per unit`);

  // grid: every unit, pale, and the axes themselves
  const gx = d3.range(-6, 7).map(k => k * P);
  const gy = d3.range(0, 10).map(k => k * P);

  svg.append("g").selectAll("line").data(gx).enter().append("line")
    .attr("x1", d => x(d)).attr("x2", d => x(d))
    .attr("y1", y(-250)).attr("y2", y(2550))
    .attr("stroke", "#ddd3b8").attr("stroke-width", 1);
  svg.append("g").selectAll("line").data(gy).enter().append("line")
    .attr("y1", d => y(d)).attr("y2", d => y(d))
    .attr("x1", x(-1750)).attr("x2", x(1750))
    .attr("stroke", "#ddd3b8").attr("stroke-width", 1);

  // axes in cells
  svg.append("g").attr("transform", `translate(0,${y(0)})`)
    .call(d3.axisBottom(x).tickValues(d3.range(-1536, 1537, 512))
      .tickFormat(d3.format(",")))
    .call(g => g.selectAll("text").attr("font-size", 12).attr("fill", "#7b6c4e"));
  svg.append("g").attr("transform", `translate(${x(0)},0)`)
    .call(d3.axisLeft(y).tickValues(d3.range(0, 2305, 512))
      .tickFormat(d3.format(",")))
    .call(g => g.selectAll("text").attr("font-size", 12).attr("fill", "#7b6c4e"));

  svg.append("text").attr("x", x(1750) - 4).attr("y", y(0) - 10)
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

  // the 25 integer vertices, each labelled with its pair.
  // side +1 puts the label right of the point, -1 left of it.
  const labels = T1.verts.map((p, i) => {
    const side = i === 0 ? -1 : i === 24 ? 1 : i === 12 ? 1 : (p[0] > 0 ? 1 : -1);
    return { i, p, side, px: x(p[0]), py: y(p[1]), text: `(${p[0]}, ${p[1]})` };
  });

  const leaders = svg.append("g").attr("class", "leaders");
  const vg = svg.append("g").attr("class", "vlabels");
  labels.forEach(L => {
    L.base = L.py;
    L.node = vg.append("text")
      .attr("class", "vlabel")
      .attr("data-i", L.i)
      .attr("x", L.px + L.side * 7)
      .attr("y", L.py)
      .attr("font-size", 10)
      .attr("dominant-baseline", "middle")
      .attr("text-anchor", L.side > 0 ? "start" : "end")
      .attr("fill", "#5c4d33")
      .attr("paint-order", "stroke")
      .attr("stroke", "#fbf7ec")
      .attr("stroke-width", 2.4)
      .attr("stroke-linejoin", "round")
      .text(L.text);
    L.box = L.node.node().getBBox();
  });

  // one-dimensional spread: no two boxes in a column may share a row
  const GAP = 2;
  function spread(items) {
    items.sort((a, b) => a.box.y - b.box.y);
    let floor = -Infinity;
    items.forEach(it => {
      const top = Math.max(it.box.y, floor + GAP);
      it.shift = top - it.box.y;
      floor = top + it.box.height;
    });
  }
  spread(labels.filter(L => L.side > 0));
  spread(labels.filter(L => L.side < 0));

  labels.forEach(L => {
    if (L.shift > 0.5) {
      L.node.attr("y", L.base + L.shift);
      leaders.append("line")
        .attr("x1", L.px + L.side * 3).attr("y1", L.base)
        .attr("x2", L.px + L.side * 5).attr("y2", L.base + L.shift)
        .attr("stroke", "#b9a67f").attr("stroke-width", 0.7)
        .attr("stroke-dasharray", "2 2");
    }
  });

  // the four parameters where the curve meets the lattice.
  // The letter sits clear of the ring, with a halo so it stays legible.
  const up = { A: 24, B: 22, C: 22, D: 22 };
  const hits = svg.append("g");
  T1.hits.forEach(h => {
    hits.append("circle").attr("class", "hitring")
      .attr("cx", x(h[0])).attr("cy", y(h[1])).attr("r", 9)
      .attr("fill", "none").attr("stroke", "#a23b2a").attr("stroke-width", 2);
    hits.append("text").attr("class", "hitlabel")
      .attr("x", x(h[0])).attr("y", y(h[1]) - up[h[2]])
      .attr("font-size", 14).attr("font-weight", 600).attr("fill", "#a23b2a")
      .attr("text-anchor", "middle").attr("paint-order", "stroke")
      .attr("stroke", "#fbf7ec").attr("stroke-width", 3).text(h[2]);
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
    const o = row === 0 ? [0, 250, 620][col] : [0, 300][col];
    const L = svg.append("g")
      .attr("transform", `translate(${M.left + 10 + o},${H - 48 + row * 26})`);
    L.append("line").attr("x1", 0).attr("x2", 22).attr("y1", 0).attr("y2", 0)
      .attr("stroke", it[0]).attr("stroke-width", it[1]);
    L.append("text").attr("x", 29).attr("y", 5).attr("font-size", 15)
      .attr("fill", "#2e2413").text(it[2]);
  });
})();
