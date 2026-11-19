// The corner rule as a number: for swan and one 135° curve, print the ink in
// each 150×150 corner region for A and C.
//
//   node app/scripts/check-corners.mjs

import { chromium } from "playwright-core";
import { readFileSync } from "node:fs";
import { figureFor, svgForFigure } from "../src/lib/bordered.js";

const frames = JSON.parse(
  readFileSync(new URL("../../workbench/frames.json", import.meta.url), "utf8"),
);
const registry = JSON.parse(
  readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"),
);
const byUid = new Map(registry.curves.map((curve) => [curve.uid, curve]));
const rows = frames.curves || [];
const swan = rows.find((row) => row.name === "swan" && row.variant === "A");
const stop = rows.find(
  (row) => row.variant === "A" && row.cornerRule === "stop" && row.delta >= 130 && row.delta <= 140,
);

const browser = await chromium.launch({
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
});
const page = await browser.newPage({ viewport: { width: 600, height: 600 } });

async function corners(row) {
  const curve = byUid.get(row.uid);
  const figure = figureFor({ ...curve, ...row }, {}, null);
  const svg = svgForFigure(figure, `${row.illus}`);
  const url = `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;
  await page.setContent(
    `<body style="margin:0"><img src="${url}" style="width:600px;height:600px;display:block"></body>`,
  );
  const data = await page.evaluate(async ({ src, size }) => {
    const image = document.createElement("img");
    await new Promise((resolve, reject) => {
      image.onload = resolve;
      image.onerror = reject;
      image.src = src;
    });
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const context = canvas.getContext("2d");
    context.drawImage(image, 0, 0, size, size);
    return [...context.getImageData(0, 0, size, size).data];
  }, { src: url, size: 600 });

  const ink = (x0, y0, x1, y1) => {
    let count = 0;
    for (let y = y0; y < y1; y += 1) {
      for (let x = x0; x < x1; x += 1) {
        const i = (y * 600 + x) * 4;
        if (data[i] < 250 || data[i + 1] < 250 || data[i + 2] < 250) count += 1;
      }
    }
    return count;
  };
  const edge = 60;
  return {
    tl: ink(0, 0, edge, edge),
    tr: ink(600 - edge, 0, 600, edge),
    bl: ink(0, 600 - edge, edge, 600),
    br: ink(600 - edge, 600 - edge, 600, 600),
  };
}

for (const label of ["swan", "stop"]) {
  const base = label === "swan" ? swan : stop;
  if (!base) {
    console.error(`missing ${label} row`);
    continue;
  }
  for (const variant of ["A", "C"]) {
    const row = rows.find((r) => r.uid === base.uid && r.variant === variant);
    if (!row) continue;
    const c = await corners(row);
    console.log(`${row.name} ${variant}: corners tl ${c.tl} tr ${c.tr} bl ${c.bl} br ${c.br}`);
  }
}

await browser.close();
