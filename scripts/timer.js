#!/usr/bin/env node
"use strict";
/**
 * scripts/timer.js — a work budget with a floor and a ceiling, and a log.
 *
 * Work at least the floor and no more than the ceiling. The clock writes a
 * marker (.timer.json), chimes softly at the floor ("you may stop") and hard
 * at the ceiling ("stop now"), reports what changed, and clears the marker.
 *
 * Every start, floor, cap and stop is appended to state/timers.jsonl, the
 * same way scripts/ctx.py --log appends to state/sessions.jsonl. That file is
 * the clock's statistics: elapsed wall time per session, against its budget.
 * Set CURVE_LAB_TIMER_LOG to write somewhere else (tests, scratch runs).
 *
 *   node scripts/timer.js --min 20m --max 45m
 *   node scripts/timer.js 1h 2h "the plates"        floor 1 hour, cap 2 hours
 *   node scripts/timer.js --min 20m --no-cap "..."  floor only, no ceiling
 *   node scripts/timer.js --check                    the phase and the times
 *   node scripts/timer.js --stop                     log the elapsed time, clear
 *   node scripts/timer.js --tally                    the last sessions + summary
 *
 * Units: a bare number is minutes; a suffix is m (minutes) or h (hours).
 * Zero dependencies. Start it in the background; do not poll it.
 */
var fs = require("fs");
var path = require("path");
var cp = require("child_process");
var ROOT = path.resolve(__dirname, "..");
var MARK = path.join(ROOT, ".timer.json");
var LOG = process.env.CURVE_LAB_TIMER_LOG || path.join(ROOT, "state", "timers.jsonl");

function mins(s) {
    if (s == null) { return null; }
    var m = String(s).trim().match(/^([\d.]+)\s*([mh]?)$/i);
    if (!m) { return null; }
    var v = parseFloat(m[1]);
    return m[2].toLowerCase() === "h" ? v * 60 : v;
}
function clock(d) { return d.toTimeString().slice(0, 5); }
function chime(msg) { try { cp.execSync('node scripts/notify.js -m ' + JSON.stringify(msg), { cwd: ROOT, stdio: "ignore" }); } catch (e) {} }

function elapsed(m) { return Math.max(0, Math.round((Date.now() - new Date(m.start)) / 600) / 100); }

function log(record) {
    try {
        fs.mkdirSync(path.dirname(LOG), { recursive: true });
        fs.appendFileSync(LOG, JSON.stringify(record) + "\n");
    } catch (e) {
        console.log("timer: could not write " + LOG + ": " + e.message);
    }
}

function readMark() {
    if (!fs.existsSync(MARK)) { return null; }
    try { return JSON.parse(fs.readFileSync(MARK, "utf8")); }
    catch (e) { return null; }
}

function tally() {
    if (!fs.existsSync(LOG)) { console.log("timer: no stats yet at " + LOG); return; }
    var rows = [];
    fs.readFileSync(LOG, "utf8").split("\n").forEach(function (line) {
        if (!line.trim()) { return; }
        try {
            var r = JSON.parse(line);
            if (r.event === "stop" || r.event === "cap") { rows.push(r); }
        } catch (e) { /* a bad line must not stop the tally */ }
    });
    if (!rows.length) { console.log("timer: no completed sessions in " + LOG); return; }
    var last = rows.slice(-10);
    last.forEach(function (r) {
        console.log("timer: " + (r.label || "session") + " | " + r.minutes + "m | " +
            "floor " + r.floor + "m, " + (r.cap == null ? "no cap" : "cap " + r.cap + "m") +
            " | " + (r.reason || r.event) +
            " | " + String(r.at).slice(0, 16).replace("T", " "));
    });
    var all = rows.map(function (r) { return Number(r.minutes) || 0; }).sort(function (a, b) { return a - b; });
    var total = all.reduce(function (a, b) { return a + b; }, 0);
    var mid = all.length % 2 ? all[(all.length - 1) / 2]
        : (all[all.length / 2 - 1] + all[all.length / 2]) / 2;
    console.log("timer: " + all.length + " session(s) · median " + mid.toFixed(1) +
        "m · mean " + (total / all.length).toFixed(1) + "m · total " + total.toFixed(1) + "m");
}

var args = process.argv.slice(2);
if (args[0] === "--check") {
    var m = readMark();
    if (!m) { console.log("timer: none running"); process.exit(0); }
    var now = Date.now();
    var el = elapsed(m);
    var toFloor = Math.round((new Date(m.floor) - now) / 60000);
    var toCap = m.cap ? Math.round((new Date(m.cap) - now) / 60000) : null;
    var phase = (m.cap && now >= new Date(m.cap)) ? "past the cap: stop"
        : (now >= new Date(m.floor) ? "in the window: you may stop" : "before the floor: keep going");
    console.log("timer: " + m.label + " | floor " + m.min + "m, " +
        (m.cap ? "cap " + m.max + "m" : "no cap") + " | " + el + "m elapsed | " +
        (toFloor > 0 ? toFloor + "m to floor" : "past the floor") +
        (toCap == null ? "" : ", " + toCap + "m to cap") + " | " + phase);
    process.exit(0);
}
if (args[0] === "--tally") {
    tally();
    process.exit(0);
}
if (args[0] === "--stop") {
    var done = readMark();
    if (!done) { console.log("timer: none running"); process.exit(0); }
    var minutes = elapsed(done);
    log({
        event: "stop", label: done.label, minutes: minutes,
        floor: done.min, cap: done.max, start: done.start,
        at: new Date().toISOString(), reason: "stop"
    });
    fs.unlinkSync(MARK);
    // stop the background process that owns this marker, so its floor/cap
    // timers cannot fire later against a different session
    if (done.pid) { try { process.kill(done.pid, "SIGTERM"); } catch (e) {} }
    console.log("timer: cleared after " + minutes + "m (" + done.label + ")");
    process.exit(0);
}

var min = null, max = null, run = null, rest = [], i, noCap = false;
for (i = 0; i < args.length; i++) {
    if (args[i] === "--min") { min = mins(args[++i]); }
    else if (args[i] === "--max") { max = mins(args[++i]); }
    else if (args[i] === "--no-cap") { noCap = true; }
    else if (args[i] === "--run") { run = args.slice(i + 1).join(" "); break; }
    else { rest.push(args[i]); }
}
if (min == null && !noCap) { min = mins(rest.shift()); }
if (max == null && !noCap) { max = mins(rest.shift()); }
var label = rest.join(" ") || "work block";
if (min == null) { min = 20; }
if (noCap) { max = null; }
else if (max == null) { max = min; }
if (max != null && max < min) { console.error("timer: the cap (" + max + "m) is under the floor (" + min + "m)"); process.exit(1); }

var start = new Date(), floorAt = new Date(start.getTime() + min * 60000);
var capAt = max == null ? null : new Date(start.getTime() + max * 60000);
var before = cp.execSync("git status --short | wc -l", { cwd: ROOT }).toString().trim();
var ME = process.pid + "-" + start.getTime();
fs.writeFileSync(MARK, JSON.stringify({ id: ME, pid: process.pid, label: label, min: min, max: max, start: start.toISOString(), floor: floorAt.toISOString(), cap: capAt ? capAt.toISOString() : null }));
log({
    event: "start", id: ME, label: label, floor: min, cap: max,
    start: start.toISOString(), at: start.toISOString()
});
console.log("timer: " + label + " | floor " + min + "m (" + clock(floorAt) + "), " +
    (max == null ? "no cap" : "cap " + max + "m (" + clock(capAt) + ")"));

/* with --run, the timer starts the command and the cap stops it: real start and stop */
var child = null;
if (run) {
    child = cp.spawn(run, { cwd: ROOT, shell: true, stdio: "inherit" });
    console.log("timer: running: " + run);
    child.on("exit", function (code) {
        var m2 = readMark();
        if (m2 && m2.id === ME) {
            log({
                event: "stop", label: label, minutes: elapsed(m2 || { start: start.toISOString() }),
                floor: min, cap: max, start: start.toISOString(),
                at: new Date().toISOString(), reason: "command exit " + code
            });
            fs.unlinkSync(MARK);
            console.log("timer: the command finished on its own (exit " + code + "); timer cleared.");
            process.exit(0);
        }
    });
}

setTimeout(function () {
    var now = readMark();
    if (!now || now.id !== ME) { process.exit(0); }
    log({
        event: "floor", label: label, minutes: elapsed(now),
        floor: min, cap: max, start: now.start, at: new Date().toISOString()
    });
    console.log("timer: floor reached (" + min + "m). You may stop, or work on to the cap at " + clock(capAt) + ".");
    chime("Timer floor: " + label + ", " + min + " min, you may stop");
}, min * 60000);

if (max != null) {
setTimeout(function () {
    var now = readMark();
    if (!now || now.id !== ME) { process.exit(0); }
    var after = cp.execSync("git status --short | wc -l", { cwd: ROOT }).toString().trim();
    var last = cp.execSync("git log --oneline -1", { cwd: ROOT }).toString().trim();
    if (now) {
        log({
            event: "cap", label: label, minutes: elapsed(now),
            floor: min, cap: max, start: now.start, at: new Date().toISOString(),
            reason: "cap", before: before, after: after
        });
    }
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
}
