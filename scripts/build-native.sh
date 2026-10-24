#!/bin/bash
# scripts/build-native.sh — build libclothoidlab.dylib from the vendored Clothoids.
#
# No CMake. The vendored tree is CMake 3.x era and the installed CMake is 4,
# which rejects the old minimum versions; the sources compile cleanly with the
# system clang, so the build is one compile per file and one link.
#
# DEVELOPER_DIR is set because xcode-select on this machine points at a path
# that does not resolve, and every compiler call fails without it.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CL="$ROOT/vendor/Clothoids"
BUILD="$ROOT/build"
OBJ="$BUILD/obj"

CXX="${CXX:-/usr/bin/clang++}"
export DEVELOPER_DIR="${DEVELOPER_DIR:-/Library/Developer/CommandLineTools}"

if [ ! -d "$CL/src/Clothoids" ]; then
  echo "vendor/Clothoids is missing. Run: git submodule update --init --recursive" >&2
  exit 1
fi

INCLUDES=(
  "-I$CL/src"
  "-I$CL/submodules/UtilsLite/src"
  "-I$CL/submodules/UtilsLite/ThirdParties/Eigen"
  "-I$CL/submodules/GenericContainer/include"
  "-I$CL/submodules/quarticRootsFlocke/src"
)

INC="${INCLUDES[*]}"
export INC

mkdir -p "$OBJ"

SOURCES=()
while IFS= read -r f; do SOURCES+=("$f"); done < <(
  ls "$CL"/src/*.cc
  ls "$CL"/submodules/UtilsLite/src/*.cc
  # Support.cc pulls the JSON, TOML and YAML readers, which this build does not
  # need and does not carry. Nothing in the geometry path calls into it.
  ls "$CL"/submodules/GenericContainer/src/*.cc | grep -v GenericContainerSupport
  ls "$CL"/submodules/quarticRootsFlocke/src/*.cc
  ls "$ROOT"/csrc/*.cpp
)

echo "compiling ${#SOURCES[@]} sources with $($CXX --version | head -1)"

compile_one() {
  local f="$1"
  local name
  name="$(echo "${f#"$ROOT"/}" | tr '/' '_' | sed 's/\.cc$/.o/; s/\.cpp$/.o/')"
  # Resumable: an object that is already there is not rebuilt, so a fix to one
  # file does not cost the whole tree. Delete build/obj to force a full build.
  [ -f "$OBJ/$name" ] && return 0
  # shellcheck disable=SC2086
  "$CXX" -std=c++17 -O3 -fPIC -w $INC -c "$f" -o "$OBJ/$name"
}
export -f compile_one
export CXX OBJ

printf '%s\n' "${SOURCES[@]}" | xargs -P 4 -I{} bash -c 'compile_one "$@"' _ {}

echo "linking"
"$CXX" -std=c++17 -O3 -dynamiclib -o "$BUILD/libclothoidlab.dylib" \
  -install_name @rpath/libclothoidlab.dylib "$OBJ"/*.o

echo "built $BUILD/libclothoidlab.dylib"
