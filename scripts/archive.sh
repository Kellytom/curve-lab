#!/bin/sh
# One free, durable snapshot: the records, the data export, the plates and the words.
#
#   scripts/archive.sh            # writes dist/curve-lab-<date>.zip
#
# The zip is what you deposit (Zenodo, the Internet Archive) or copy to a disk. It needs no
# service to read: plain files, and a manifest that says what is inside.
set -eu
cd "$(dirname "$0")/.."
STAMP=$(date -u +%Y-%m-%d)
OUT="dist/curve-lab-$STAMP.zip"
mkdir -p dist
TMP="dist/.snapshot-$STAMP"
rm -rf "$TMP"; mkdir -p "$TMP"

cp -R workbench/curve-registry.json workbench/curve-notes.json "$TMP"/
cp -R data "$TMP"/data
cp -R book/print "$TMP"/plates
cp -R book/old-plates.json "$TMP"/old-plates.json
cp -R state/GRAPHICSPEC-int.md state/DATA-int.md state/PRESERVATION-int.md "$TMP"/
cp -R scripts/print_plates.mjs scripts/old_plates_export.mjs "$TMP"/
cp README.md LICENSE "$TMP"/

cat > "$TMP/MANIFEST.txt" <<TXT
curve-lab snapshot $STAMP

curve-notes.json     the notes as exported (names, importance, rotation)
curve-registry.json  every curve: uid, name, rows or path, formula, transform
data/                one JSON file per database table, with schema and manifest
plates/              every print plate: PNG at 300 dpi and its SVG, one per uid
GRAPHICSPEC-int.md   how a plate is drawn, and by which module
DATA-int.md          every dataset, its format, and who writes it
PRESERVATION-int.md  how this archive is meant to be kept
README.md, LICENSE   what the project is, and the terms

To read a plate without any software beyond a browser: open plates/<uid>.png.
To rebuild the database: see DATA-int.md (prisma db push, then the migration).
TXT

( cd "$TMP" && zip -qr "../curve-lab-$STAMP.zip" . )
rm -rf "$TMP"
printf 'wrote %s (%s files, %s)\n' "$OUT" \
  "$(ls book/print | wc -l | tr -d ' ')" "$(du -h "$OUT" | cut -f1)"
