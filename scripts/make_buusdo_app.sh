#!/usr/bin/env bash
# Minimal macOS .app wrapper so Dock / Computer Use can resolve Buusdo.
# Dev-only — not a notarized installer.
#
# After git pull / uv sync: re-run this script so Contents/MacOS/Buusdo points at
# the current checkout .venv (stale wrappers keep launching old trees).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="${ROOT}/dist/Buusdo.app"
MACOS="${APP}/Contents/MacOS"
RES="${APP}/Contents/Resources"
PY="${ROOT}/.venv/bin/python"
ICNS="${ROOT}/buusdo/assets/logo.icns"
STUB_SRC="${ROOT}/build/buusdo_launcher.c"
STUB_BIN="${MACOS}/Buusdo"

if [[ ! -x "${PY}" ]]; then
  echo "Missing ${PY} — run: uv sync --extra ui" >&2
  exit 1
fi

echo "NOTE: rebuild after pull — this refreshes ${APP} → ${PY}"

rm -rf "${APP}"
mkdir -p "${MACOS}" "${RES}" "${ROOT}/build"

# Mach-O stub — LaunchServices rejects shell-script executables with
# kLSNoExecutableErr on recent macOS; a tiny execv stub is accepted.
cat > "${STUB_SRC}" <<EOF
#include <unistd.h>
#include <stdio.h>
int main(int argc, char **argv) {
  /* Re-exec venv python -m buusdo with passthrough args. */
  char *py = "${PY}";
  char *mod = "-m";
  char *pkg = "buusdo";
  char **args = malloc((size_t)(argc + 3) * sizeof(char *));
  if (!args) return 127;
  args[0] = py;
  args[1] = mod;
  args[2] = pkg;
  for (int i = 1; i < argc; i++) args[i + 2] = argv[i];
  args[argc + 2] = NULL;
  if (chdir("${ROOT}") != 0) {
    perror("chdir");
    return 126;
  }
  execv(py, args);
  perror("execv");
  return 127;
}
EOF
# malloc needs stdlib.h
cat > "${STUB_SRC}" <<EOF
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(int argc, char **argv) {
  char *py = "${PY}";
  char **args = calloc((size_t)argc + 3, sizeof(char *));
  if (!args) return 127;
  args[0] = py;
  args[1] = "-m";
  args[2] = "buusdo";
  for (int i = 1; i < argc; i++) args[i + 2] = argv[i];
  if (chdir("${ROOT}") != 0) { perror("chdir"); return 126; }
  execv(py, args);
  perror("execv");
  return 127;
}
EOF

if ! cc -O2 -o "${STUB_BIN}" "${STUB_SRC}" 2>/tmp/buusdo-stub-cc.err; then
  echo "cc stub failed; falling back to sh launcher:" >&2
  cat /tmp/buusdo-stub-cc.err >&2 || true
  cat > "${STUB_BIN}" <<EOF
#!/bin/sh
cd "${ROOT}" || exit 1
exec "${PY}" -m buusdo "\$@"
EOF
  chmod +x "${STUB_BIN}"
fi
chmod +x "${STUB_BIN}"

# PkgInfo expected by LaunchServices for APPL bundles.
printf 'APPL????' > "${APP}/Contents/PkgInfo"

ICON_XML=""
if [[ -f "${ICNS}" ]]; then
  cp "${ICNS}" "${RES}/AppIcon.icns"
  ICON_XML="  <key>CFBundleIconFile</key>
  <string>AppIcon</string>"
fi

cat > "${APP}/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>Buusdo</string>
  <key>CFBundleIdentifier</key>
  <string>app.buusdo.dev</string>
  <key>CFBundleName</key>
  <string>buusdo Graphics Enhancement Tool</string>
  <key>CFBundleDisplayName</key>
  <string>buusdo Graphics Enhancement Tool</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>0.1.0</string>
  <key>LSMinimumSystemVersion</key>
  <string>12.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
${ICON_XML}
</dict>
</plist>
PLIST

xattr -cr "${APP}" 2>/dev/null || true
# Ad-hoc sign so LaunchServices accepts the local stub (unsigned → kLSNoExecutableErr).
if command -v codesign >/dev/null 2>&1; then
  codesign --force --deep -s - "${APP}" >/dev/null 2>&1 || true
fi

echo "OK  ${APP}"
echo "Launch: open ${APP}"
echo "Tip: after every git pull, re-run: bash scripts/make_buusdo_app.sh"
