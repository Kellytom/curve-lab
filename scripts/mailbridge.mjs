// The mailbox bridge: push, not poll.
//
// Watches the two mailbox files. When DeepSeek1 appends a job, it posts a
// "mail" prompt into the DeepSeek2 session over the OpenCode API. When
// DeepSeek2 appends a reply, it raises a macOS notification for the operator.
// Nobody has to type /mail for the other side to notice.
//
//   node scripts/mailbridge.mjs            # run in the foreground
//   node scripts/mailbridge.mjs --dry-run  # print what it would deliver
//   node scripts/mailbridge.mjs --once     # check once and exit
//
// It remembers what it delivered in state/mail-state.json, so a restart does
// not replay history. The LaunchAgent runs it with KeepAlive.

import { execFile } from "node:child_process";
import { existsSync, readFileSync, watchFile, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const NOTES = path.join(ROOT, "archive", "notes");
const TO_SIDE = path.join(NOTES, "deep-to-side.md");
const TO_DEEP = path.join(NOTES, "side-to-deep.md");
const STATE = path.join(ROOT, "state", "mail-state.json");
const SESSION = process.env.SIDE_CHAT_SESSION || "ses-sidechat";
const OPENCODE = process.env.OPENCODE_BIN || path.join(process.env.HOME, ".opencode", "bin", "opencode");
const DRY = process.argv.includes("--dry-run");
const ONCE = process.argv.includes("--once");

const HEADER = /^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) — (.+)$/;

function newestEntry(file) {
  if (!existsSync(file)) return null;
  let found = null;
  for (const line of readFileSync(file, "utf8").split("\n")) {
    const match = HEADER.exec(line);
    if (match) found = { stamp: match[1], subject: match[2].trim() };
  }
  return found;
}

const state = existsSync(STATE) ? JSON.parse(readFileSync(STATE, "utf8")) : {};
const seen = {
  deep: state.deep || null,
  side: state.side || null,
};
if (!state.deep) seen.deep = newestEntry(TO_SIDE)?.stamp || null;
if (!state.side) seen.side = newestEntry(TO_DEEP)?.stamp || null;

function save() {
  writeFileSync(STATE, JSON.stringify(seen, null, 1) + "\n");
}

function notify(title, message) {
  if (DRY) { console.log(`[notify] ${title}: ${message}`); return; }
  execFile("osascript", ["-e", `display notification ${JSON.stringify(message)} with title ${JSON.stringify(title)}`],
    () => {});
}

function promptSide(text) {
  if (DRY) { console.log(`[prompt ${SESSION}] ${text}`); return; }
  const body = JSON.stringify({ text });
  execFile(OPENCODE, ["api", "post", `/api/session/${SESSION}/prompt`, "--data", body],
    { cwd: ROOT, env: { ...process.env, PATH: `${process.env.HOME}/node24/bin:${process.env.PATH}` } },
    (error, stdout, stderr) => {
      const line = error ? `prompt failed: ${stderr || error.message}` : `prompted ${SESSION}`;
      console.log(`${new Date().toISOString()} ${line}`);
    });
}

function check() {
  const job = newestEntry(TO_SIDE);
  if (job && job.stamp !== seen.deep) {
    seen.deep = job.stamp;
    save();
    console.log(`${new Date().toISOString()} job ${job.stamp}: ${job.subject}`);
    promptSide(
      `mail — a new job is waiting in archive/notes/deep-to-side.md: "${job.subject}" (${job.stamp}). ` +
      "Run `.venv/bin/python scripts/mailbox.py --read 1`, do it, and reply in side-to-deep.md.",
    );
  }

  const reply = newestEntry(TO_DEEP);
  if (reply && reply.stamp !== seen.side) {
    seen.side = reply.stamp;
    save();
    console.log(`${new Date().toISOString()} reply ${reply.stamp}: ${reply.subject}`);
    notify("DeepSeek2 replied", reply.subject);
  }
}

save();
check();
if (!ONCE) {
  // watchFile polls the stat, not the inode: a rewritten file is still seen.
  watchFile(TO_SIDE, { interval: 2000 }, check);
  watchFile(TO_DEEP, { interval: 2000 }, check);
  console.log(`mailbridge watching ${NOTES} for ${SESSION}`);
}
