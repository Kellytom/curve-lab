/**
 * Install (or remove) the monitor as a LaunchAgent.
 *
 *   ~/node24/bin/node scripts/netmon/install.ts
 *   ~/node24/bin/node scripts/netmon/install.ts --remove
 *
 * One agent, `local.netmon`, KeepAlive, started at login. The logs stay in
 * ~/.local/share/netmon and never enter the repo.
 */
import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { LAUNCH_LABEL, LOG_DIR } from "./paths.ts";

const remove = process.argv.includes("--remove");
const plistPath = path.join(homedir(), "Library", "LaunchAgents", `${LAUNCH_LABEL}.plist`);
const uid = String(process.getuid?.() ?? 501);

function xml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function unload(): void {
  try {
    execFileSync("launchctl", ["bootout", `gui/${uid}`, plistPath], { stdio: "ignore" });
  } catch {
    // not loaded; nothing to stop
  }
}

if (remove) {
  unload();
  rmSync(plistPath, { force: true });
  console.log(`Removed ${LAUNCH_LABEL}. The logs in ${LOG_DIR} are kept.`);
  process.exit(0);
}

const script = path.resolve(import.meta.dirname, "daemon.ts");
const node = process.execPath;
mkdirSync(LOG_DIR, { recursive: true });
mkdirSync(path.dirname(plistPath), { recursive: true });

const plist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${LAUNCH_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${xml(node)}</string>
    <string>${xml(script)}</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>WorkingDirectory</key><string>${xml(path.dirname(script))}</string>
  <key>StandardOutPath</key><string>${xml(path.join(LOG_DIR, "launchd.out.log"))}</string>
  <key>StandardErrorPath</key><string>${xml(path.join(LOG_DIR, "launchd.err.log"))}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>NETMON_HOST</key><string>opencode.ai</string>
  </dict>
</dict>
</plist>
`;

writeFileSync(plistPath, plist);
unload();

try {
  execFileSync("launchctl", ["bootstrap", `gui/${uid}`, plistPath], { stdio: "pipe" });
} catch (error) {
  const detail = error instanceof Error ? error.message : String(error);
  console.error(`bootstrap failed: ${detail.split("\n")[0]}`);
  console.error("Falling back to launchctl load -w");
  execFileSync("launchctl", ["load", "-w", plistPath], { stdio: "inherit" });
}

console.log(`Installed ${LAUNCH_LABEL}. It is running now and starts at login.`);
console.log(`  status: launchctl list | grep ${LAUNCH_LABEL}`);
console.log(`  report: ${node} ${path.resolve(import.meta.dirname, "report.ts")}`);
console.log(`  logs:   ${LOG_DIR}`);
