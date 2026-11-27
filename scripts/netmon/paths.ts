/**
 * Where netmon keeps its files.
 *
 * The logs live outside the repo on purpose: they are this machine's network
 * history, and the repository is public. `NETMON_DIR` moves them, which the
 * tests use so they never touch the real log.
 */
import { homedir } from "node:os";
import path from "node:path";

export const LOG_DIR = process.env.NETMON_DIR ?? path.join(homedir(), ".local", "share", "netmon");
export const SPEED_LOG = path.join(LOG_DIR, "speed.jsonl");
export const PROBE_LOG = path.join(LOG_DIR, "probe.jsonl");
export const EVENT_LOG = path.join(LOG_DIR, "events.jsonl");
export const STATE_FILE = path.join(LOG_DIR, "state.json");
export const LAUNCH_LABEL = "local.netmon";
