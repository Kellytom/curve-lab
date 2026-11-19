#!/usr/bin/env bash
# Recovery parity: both sessions run this, from the same commands.
#
#   scripts/recover.sh --check              # read only: DB and exports
#   scripts/recover.sh --backup             # snapshot, then check
#   scripts/recover.sh --restore [snapshot] # restore, then check
#
# The rule: a failed read is never a write, and a restore names what it
# overwrites. `--check` touches nothing; `--backup` writes a snapshot; a
# restore copies the current database aside before it replaces it.
set -euo pipefail
cd "$(dirname "$0")/.."

MODE="${1:---check}"

check_db() {
  ( cd app && node scripts/check-db.mjs )
}

check_exports() {
  node --input-type=module -e "
import { readFileSync } from 'node:fs';
const files = [
  ['workbench/curve-notes.json', 'curve-lab.curve-notes/1', 'curves'],
  ['workbench/starred.json', 'starred/1', 'plates'],
  ['workbench/finder-stars.json', 'curve-lab.finder-stars/1', 'curves'],
];
let bad = 0;
for (const [file, format, key] of files) {
  try {
    const data = JSON.parse(readFileSync(file, 'utf8'));
    if (data.format !== format) {
      console.error(file + ': format ' + data.format + ', expected ' + format);
      bad += 1;
      continue;
    }
    if (!Array.isArray(data[key])) {
      console.error(file + ': no ' + key + ' array');
      bad += 1;
      continue;
    }
    console.log(file + ': ' + data[key].length + ' rows');
  } catch (error) {
    console.error(file + ': ' + error.message);
    bad += 1;
  }
}
process.exit(bad ? 1 : 0);
"
}

case "$MODE" in
  --check)
    check_db
    check_exports
    echo "recover --check: ok"
    ;;
  --backup)
    ( cd app && node scripts/backup-db.mjs )
    check_db
    check_exports
    echo "recover --backup: ok"
    ;;
  --restore)
    shift
    echo "restore overwrites app/prisma/dev.db with ${1:-the newest snapshot}"
    ( cd app && node scripts/restore-db.mjs "$@" )
    check_db
    check_exports
    echo "recover --restore: ok"
    ;;
  *)
    echo "usage: scripts/recover.sh [--check|--backup|--restore [snapshot]]" >&2
    exit 2
    ;;
esac
