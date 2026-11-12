/* T1 — the 24 triangles and 25 integer vertices, drawn with d3.
   Data comes from the page as T1: verts, steps, curve, hits, pitch.
   Model y is up; d3's y scale reverses the range, so the flip happens there. */

(function () {
  const W = 1180, H = 780;
  const M = { top: 26, right: 28, bottom: 46, left: 74 };

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
    .call(g => g.selectAll("text").attr("font-size", 11).attr("fill", "#7b6c4e"));
  svg.append("g").attr("transform", `translate(${x(0)},0)`)
    .call(d3.axisLeft(y).tickValues(d3.range(0, 2305, 512))
      .tickFormat(d3.format(",")))
    .call(g => g.selectAll("text").attr("font-size", 11).attr("fill", "#7b6c4e"));

  svg.append("text").attr("x", x(1750) - 4).attr("y", y(0) - 10)
    .attr("font-size", 13).attr("fill", "#2e2413").attr("text-anchor", "end")
    .text("x, cells");

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

  // the 25 integer vertices, each labelled with its pair
  const v = svg.append("g");
  T1.verts.forEach((p, i) => {
    v.append("circle").attr("cx", x(p[0])).attr("cy", y(p[1])).attr("r", 2.8)
      .attr("fill", "#2e2413");
    const right = p[0] >= 0;
    v.append("text")
      .attr("x", x(p[0]) + (right ? 7 : -7))
      .attr("y", y(p[1]) + (i % 2 ? 12 : -6))
      .attr("font-size", 9.5)
      .attr("text-anchor", right ? "start" : "end")
      .attr("fill", "#5c4d33")
      .text(`(${p[0]}, ${p[1]})`);
  });

  // the four parameters where the curve meets the lattice
  const hits = svg.append("g");
  T1.hits.forEach(h => {
    hits.append("circle").attr("cx", x(h[0])).attr("cy", y(h[1])).attr("r", 9)
      .attr("fill", "none").attr("stroke", "#a23b2a").attr("stroke-width", 2);
    const right = h[0] >= 0;
    hits.append("text")
      .attr("x", x(h[0]) + (right ? 13 : -13)).attr("y", y(h[1]) + 22)
      .attr("font-size", 13).attr("font-weight", 600).attr("fill", "#a23b2a")
      .attr("text-anchor", right ? "start" : "end").text(h[2]);
  });

  // legend
  const L = svg.append("g").attr("transform", `translate(${M.left + 10},${H - 34})`);
  const items = [
    ["#7a6a4a", 2.2, "smooth curve"],
    ["#2e2413", 2.4, "chain, 24 sides, 25 integer vertices"],
    ["#9bb7d4", 1.2, "step legs"],
    ["#a23b2a", 2, "curve meets the lattice (A–D)"],
    ["#ddd3b8", 1.2, `grid: one unit = ${P} cells`]
  ];
  items.forEach((it, k) => {
    const o = k * 210;
    L.append("line").attr("x1", o).attr("x2", o + 22).attr("y1", 0).attr("y2", 0)
      .attr("stroke", it[0]).attr("stroke-width", it[1]);
    L.append("text").attr("x", o + 29).attr("y", 4).attr("font-size", 10.5)
      .attr("fill", "#2e2413").text(it[2]);
  });
})();
