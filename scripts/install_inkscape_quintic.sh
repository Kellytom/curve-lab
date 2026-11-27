#!/bin/sh
# Install (or re-install) the two Inkscape extensions from this repository.
#
#   sh scripts/install_inkscape_quintic.sh
#
# They appear under Extensions -> Curve Lab. The maths is read from the
# repository at run time, so editing inkscape/quintic_math.py needs no re-install;
# editing the .py glue or the .inx does, and this script is the one-liner for it.
set -e
here=$(cd "$(dirname "$0")/.." && pwd)
target="$HOME/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions"
mkdir -p "$target"
cp "$here/inkscape/quintic-guide.inx" "$here/inkscape/quintic_guide.py" \
   "$here/inkscape/quintic-sheet.inx" "$here/inkscape/quintic_sheet.py" \
   "$target/"
echo "installed to $target"
echo "restart Inkscape, then: Extensions -> Curve Lab"
