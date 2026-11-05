#!/usr/bin/env node
/**
 * scripts/notify.js
 * Zero-dependency Node.js Audio & Visual Notifier for macOS
 */

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

function appleScriptQuote(text) {
    return '"' + String(text).replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"';
}

const args = process.argv.slice(2);
let message = "Task completed! Ready for review.";
let sound = "Glass";

for (let i = 0; i < args.length; i++) {
    if (args[i] === '-m' || args[i] === '--message') {
        message = args[i + 1] || message;
        i++;
    } else if (args[i] === '--sound') {
        sound = args[i + 1] || sound;
        i++;
    }
}

// 1. Play audible sound via CoreAudio
const soundPath = `/System/Library/Sounds/${sound}.aiff`;
if (fs.existsSync(soundPath)) {
    const played = spawnSync('afplay', [soundPath], { stdio: 'ignore' });
    if (played.error || played.status !== 0) {
        console.log(`🔔 Sound failed (${sound}): ${played.error ? played.error.code : 'afplay exit ' + played.status}`);
    } else {
        console.log(`🔔 Chimed: ${sound}`);
    }
} else {
    process.stdout.write('\x07');
    console.log(`🔔 No ${sound}.aiff in /System/Library/Sounds; fell back to the terminal bell`);
}

// 2. Notification Center banner (args-array spawn: no shell, injection-safe)
const script = `display notification ${appleScriptQuote(message)} with title ${appleScriptQuote('AlphaGamma Curves')}`;
const posted = spawnSync('osascript', ['-e', script], { stdio: 'ignore' });
if (posted.error || posted.status !== 0) {
    console.log(`[ALERT] AlphaGamma Curves: ${message}`);
}
