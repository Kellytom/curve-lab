// Render one figure at 600 px and check the ink: all four edges are reached,
// and the central region is not empty.
//
//   node app/scripts/check-figures.mjs
//
// The screenshot is /tmp/leaf.png so a person can look. The figure is the same
// leaf the unit test uses: one curve, pieces = 1, so the central design is the
// curve and its mirror.

import { chromium } from "playwright-core";
import { figureFor, svgForFigure } from "../src/lib/bordered.js";

const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const W = 600;

const leaf = {
  uid: "c-9999",
  name: "leaf-test",
  path: [[0, 0], [10, 20], [30, 40], [50, 40], [70, 20], [80, 0]],
  pieces: 1,
  rotation: 0,
};

const figure = figureFor(leaf, {}, null);
const svg = svgForFigure(figure, "leaf-test");
const dataUrl = `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;

const browser = await chromium.launch({ executablePath: EXE });
const page = await browser.newPage({ viewport: { width: W, height: W } });
await page.setContent(`<body style="margin:0"><img src="${dataUrl}" style="width:${W}px;height:${W}px;display:block"></body>`);
await page.screenshot({ path: "/tmp/leaf.png" });

const data = await page.evaluate(async ({ url, size }) => {
  const image = document.createElement("img");
  await new Promise((resolve, reject) => {
    image.onload = resolve;
    image.onerror = reject;
    image.src = url;
  });
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d");
  context.drawImage(image, 0, 0, size, size);
  return [...context.getImageData(0, 0, size, size).data];
}, { url: dataUrl, size: W });
await browser.close();

const ink = (x, y) => {
  const i = (y * W + x) * 4;
  return data[i] < 250 || data[i + 1] < 250 || data[i + 2] < 250;
};

function count(predicate) {
  let n = 0;
  for (let y = 0; y < W; y += 1) {
    for (let x = 0; x < W; x += 1) if (predicate(x, y)) n += 1;
  }
  return n;
}

// The figure is drawn with a 4% pad, so the frame edge is at `pad`, not at 0.
const pad = Math.round(W * 0.04);
const band = 3;
const edges = {
  left: count((x, y) => Math.abs(x - pad) <= band && ink(x, y)),
  right: count((x, y) => Math.abs(x - (W - pad)) <= band && ink(x, y)),
  top: count((x, y) => Math.abs(y - pad) <= band && ink(x, y)),
  bottom: count((x, y) => Math.abs(y - (W - pad)) <= band && ink(x, y)),
};
const central = count((x, y) => x >= W / 4 && x < (3 * W) / 4 && y >= W / 4 && y < (3 * W) / 4 && ink(x, y));

console.log(`edges: left ${edges.left} right ${edges.right} top ${edges.top} bottom ${edges.bottom}`);
console.log(`central ink: ${central}`);

const failures = [];
for (const [edge, n] of Object.entries(edges)) if (!n) failures.push(`${edge} edge has no ink`);
if (!central) failures.push("the central region is empty");
if (failures.length) {
  console.error(failures.map((line) => `FAIL ${line}`).join("\n"));
  process.exit(1);
}
console.log("ok — ink reaches all four edges and the centre is not empty");
