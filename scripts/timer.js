#!/usr/bin/env node
"use strict";
/**
 * scripts/timer.js — a work budget with a floor and a ceiling.
 *
 * Work at least the floor and no more than the ceiling. The clock writes a
 * marker (.timer.json), chimes softly at the floor ("you may stop") and hard
 * at the ceiling ("stop now"), reports what changed, and clears the marker.
 *
 *   node scripts/timer.js --min 20m --max 45m
 *   node scripts/timer.js 1h 2h "the plates"        floor 1 hour, cap 2 hours
 *   node scripts/timer.js --check                    the phase and the times
 *   node scripts/timer.js --stop                     clear the marker
 *
 * Units: a bare number is minutes; a suffix is m (minutes) or h (hours).
 * Zero dependencies. Start it in the background; do not poll it.
 */
var fs = require("fs");
var path = require("path");
var cp = require("child_process");
var ROOT = path.resolve(__dirname, "..");
var MARK = path.join(ROOT, ".timer.json");

function mins(s) {
    if (s == null) { return null; }
    var m = String(s).trim().match(/^([\d.]+)\s*([mh]?)$/i);
    if (!m) { return null; }
    var v = parseFloat(m[1]);
    return m[2].toLowerCase() === "h" ? v * 60 : v;
}
function clock(d) { return d.toTimeString().slice(0, 5); }
function chime(msg) { try { cp.execSync('node scripts/notify.js -m ' + JSON.stringify(msg), { cwd: ROOT, stdio: "ignore" }); } catch (e) {} }

var args = process.argv.slice(2);
if (args[0] === "--check") {
    if (!fs.existsSync(MARK)) { console.log("timer: none running"); process.exit(0); }
    var m = JSON.parse(fs.readFileSync(MARK, "utf8")), now = Date.now();
    var el = Math.round((now - new Date(m.start)) / 60000);
    var toFloor = Math.round((new Date(m.floor) - now) / 60000);
    var toCap = Math.round((new Date(m.cap) - now) / 60000);
    var phase = now >= new Date(m.cap) ? "past the cap: stop" : (now >= new Date(m.floor) ? "in the window: you may stop" : "before the floor: keep going");
    console.log("timer: " + m.label + " | floor " + m.min + "m, cap " + m.max + "m | " + el + "m elapsed | " +
        (toFloor > 0 ? toFloor + "m to floor, " : "") + toCap + "m to cap | " + phase);
    process.exit(0);
}
if (args[0] === "--stop") {
    if (fs.existsSync(MARK)) { fs.unlinkSync(MARK); console.log("timer: cleared"); }
    else { console.log("timer: none running"); }
    process.exit(0);
}

var min = null, max = null, run = null, rest = [], i;
for (i = 0; i < args.length; i++) {
    if (args[i] === "--min") { min = mins(args[++i]); }
    else if (args[i] === "--max") { max = mins(args[++i]); }
    else if (args[i] === "--run") { run = args.slice(i + 1).join(" "); break; }
    else { rest.push(args[i]); }
}
if (min == null) { min = mins(rest.shift()); }
if (max == null) { max = mins(rest.shift()); }
var label = rest.join(" ") || "work block";
if (min == null) { min = 20; }
if (max == null) { max = min; }
if (max < min) { console.error("timer: the cap (" + max + "m) is under the floor (" + min + "m)"); process.exit(1); }

var start = new Date(), floorAt = new Date(start.getTime() + min * 60000), capAt = new Date(start.getTime() + max * 60000);
var before = cp.execSync("git status --short | wc -l", { cwd: ROOT }).toString().trim();
fs.writeFileSync(MARK, JSON.stringify({ label: label, min: min, max: max, start: start.toISOString(), floor: floorAt.toISOString(), cap: capAt.toISOString() }));
console.log("timer: " + label + " | floor " + min + "m (" + clock(floorAt) + "), cap " + max + "m (" + clock(capAt) + ")");

/* with --run, the timer starts the command and the cap stops it: real start and stop */
var child = null;
if (run) {
    child = cp.spawn(run, { cwd: ROOT, shell: true, stdio: "inherit" });
    console.log("timer: running: " + run);
    child.on("exit", function (code) {
        if (fs.existsSync(MARK)) {
            console.log("timer: the command finished on its own (exit " + code + "); timer cleared.");
            fs.unlinkSync(MARK); process.exit(0);
        }
    });
}

setTimeout(function () {
    console.log("timer: floor reached (" + min + "m). You may stop, or work on to the cap at " + clock(capAt) + ".");
    chime("Timer floor: " + label + ", " + min + " min, you may stop");
}, min * 60000);

setTimeout(function () {
    var after = cp.execSync("git status --short | wc -l", { cwd: ROOT }).toString().trim();
    var last = cp.execSync("git log --oneline -1", { cwd: ROOT }).toString().trim();
    if (fs.existsSync(MARK)) { fs.unlinkSync(MARK); }
    if (child && child.exitCode === null && !child.killed) {
        console.log("timer: cap reached (" + max + "m). Stopping the command.");
        child.kill("SIGTERM");
        setTimeout(function () { try { child.kill("SIGKILL"); } catch (e) {} }, 4000);
    } else {
        console.log("timer: cap reached (" + max + "m). Stop. uncommitted files: " + before + " to " + after + ". last commit: " + last);
    }
    chime("Timer cap: " + label + ", " + max + " min, stop now");
    setTimeout(function () { process.exit(0); }, child ? 5000 : 0);
}, max * 60000);
