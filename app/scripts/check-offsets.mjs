// One curve, A and B: print the ink coverage of each so the difference is a
// number, not an opinion. A is the stored offsets; B forces them on, filled.
//
//   node app/scripts/check-offsets.mjs

import { chromium } from "playwright-core";
import { readFileSync } from "node:fs";
import { figureFor, svgForFigure } from "../src/lib/bordered.js";

const registry = JSON.parse(
  readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"),
);
const record = registry.curves.find((curve) => curve.speedX && curve.speedY);
const a = figureFor({ ...record, offsets: 0 }, {}, null);
const b = figureFor({ ...record, offsets: 1 }, {}, null);
const svgA = svgForFigure(a, "A");
const svgB = svgForFigure(b, "B");
const dataUrl = (svg) => `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;

const browser = await chromium.launch({
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
});
const page = await browser.newPage({ viewport: { width: 600, height: 600 } });

async function ink(svg) {
  const url = dataUrl(svg);
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
  let count = 0;
  for (let i = 0; i < data.length; i += 4) {
    if (data[i] < 250 || data[i + 1] < 250 || data[i + 2] < 250) count += 1;
  }
  return count;
}

const inkA = await ink(svgA);
const inkB = await ink(svgB);
await browser.close();

console.log(`${record.uid} ${record.name}: A ink ${inkA}, B ink ${inkB}, delta ${inkB - inkA}`);
console.log("the difference is printed; A and B are different drawings, not a quality score");
