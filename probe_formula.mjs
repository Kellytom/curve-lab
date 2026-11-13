import { chromium } from "playwright-core";
const b = await chromium.connectOverCDP("http://127.0.0.1:9223");
const p = await b.contexts()[0].newPage();
await p.setViewportSize({ width: 1200, height: 1100 });
p.on("pageerror", e => console.log("pageerror:", e.message));
await p.goto("http://127.0.0.1:8003/workbench/ph-septic-sandbox.html?v=" + Date.now(), { waitUntil: "load" });
console.log(await p.evaluate(() => document.getElementById("b-formula").textContent));
