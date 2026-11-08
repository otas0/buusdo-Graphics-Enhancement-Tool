#!/usr/bin/env bash
# Build a macOS .app zip via PyInstaller (self-contained).
# Ad-hoc codesign after Info.plist stamps so Gatekeeper can launch locally.
# Notarization / Developer ID still out of scope (unsigned release track).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

if command -v uv >/dev/null 2>&1; then
  RUN_PY=(uv run python)
  uv sync --extra ui >/dev/null
  uv pip install -q pyinstaller
else
  RUN_PY=(python3)
fi

VER="$("${RUN_PY[@]}" -c "from buusdo import __version__; print(__version__)")"
OUT="${ROOT}/dist"
WORK="${OUT}/.pyi-macos"
APP_DIR="${OUT}/macos"
ZIP_NAME="buusdo-macos-${VER}.zip"
ICNS="${ROOT}/buusdo/assets/logo.icns"
DOCK_ICNS="${ROOT}/buusdo/assets/logo_dock.icns"

if [[ ! -f "${ICNS}" || ! -f "${DOCK_ICNS}" ]]; then
  echo "Generating logo.icns + logo_dock.icns…"
  "${RUN_PY[@]}" "${ROOT}/scripts/generate_logo_icns.py"
fi
if [[ ! -f "${ICNS}" ]]; then
  echo "FATAL: missing Finder icon ${ICNS}" >&2
  exit 1
fi
if [[ ! -f "${DOCK_ICNS}" ]]; then
  echo "FATAL: missing pre-masked Dock icon ${DOCK_ICNS}" >&2
  exit 1
fi

rm -rf "${WORK}" "${APP_DIR}"
mkdir -p "${WORK}" "${APP_DIR}"

uv run pyinstaller \
  --noconfirm --clean --windowed --onedir \
  --name Buusdo \
  --icon "${ICNS}" \
  --distpath "${APP_DIR}" \
  --workpath "${WORK}" \
  --specpath "${WORK}" \
  --add-data "${ROOT}/buusdo/assets:buusdo/assets" \
  --add-data "${ROOT}/buusdo/locales:buusdo/locales" \
  --hidden-import buusdo \
  "${ROOT}/buusdo/app.py"

# Prefer .app bundle if PyInstaller produced one; else wrap onedir.
if [[ -d "${APP_DIR}/Buusdo.app" ]]; then
  BUNDLE="${APP_DIR}/Buusdo.app"
elif [[ -d "${APP_DIR}/buusdo.app" ]]; then
  BUNDLE="${APP_DIR}/buusdo.app"
else
  echo "FATAL: no .app bundle under ${APP_DIR}" >&2
  ls -la "${APP_DIR}" >&2 || true
  exit 1
fi

if ! "${RUN_PY[@]}" "${ROOT}/scripts/check_pyinstaller_datas.py" "${BUNDLE}"; then
  if [[ "$(find "${BUNDLE}" -name 'logo_wordmark.png' | wc -l | tr -d ' ')" -lt 1 ]]; then
    echo "FATAL: logo_wordmark.png missing in ${BUNDLE}" >&2
    exit 1
  fi
  if [[ "$(find "${BUNDLE}" -path '*/locales/*.json' | wc -l | tr -d ' ')" -lt 12 ]]; then
    echo "FATAL: locales missing in ${BUNDLE}" >&2
    exit 1
  fi
  echo "OK  ${BUNDLE}: datas present (find)"
fi

# User-visible Dock / Finder / menu-bar name must be the official full product
# name (other buusdo product-line apps share the short brand). macOS menu bar
# uses CFBundleName; Dock/Launchpad use CFBundleDisplayName — set both.
# Also rename Buusdo.app → "${PRODUCT_NAME}.app" so Finder filename matches.
DISPLAY_NAME="$("${RUN_PY[@]}" -c "from buusdo import PRODUCT_NAME; print(PRODUCT_NAME)")"
PLIST="${BUNDLE}/Contents/Info.plist"
RES="${BUNDLE}/Contents/Resources"
mkdir -p "${RES}"
# Finder / LS / PyInstaller: full-bleed AppIcon (system applies Dock mask + size).
# Runtime AppKit override: inset pre-masked AppIconDock (no system mask on that API).
for _icon_name in AppIcon.icns logo.icns icon-windowed.icns Buusdo.icns; do
  cp -f "${ICNS}" "${RES}/${_icon_name}"
done
cp -f "${DOCK_ICNS}" "${RES}/AppIconDock.icns"
cp -f "${DOCK_ICNS}" "${RES}/logo_dock.icns"
mkdir -p "${RES}/buusdo/assets"
cp -f "${ICNS}" "${RES}/buusdo/assets/logo.icns"
cp -f "${DOCK_ICNS}" "${RES}/buusdo/assets/logo_dock.icns"
cp -f "${ROOT}/buusdo/assets/logo_dock.png" "${RES}/buusdo/assets/logo_dock.png" 2>/dev/null || true
if [[ -f "${PLIST}" ]]; then
  /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName ${DISPLAY_NAME}" "${PLIST}" 2>/dev/null \
    || /usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string ${DISPLAY_NAME}" "${PLIST}"
  /usr/libexec/PlistBuddy -c "Set :CFBundleName ${DISPLAY_NAME}" "${PLIST}" 2>/dev/null \
    || /usr/libexec/PlistBuddy -c "Add :CFBundleName string ${DISPLAY_NAME}" "${PLIST}"
  /usr/libexec/PlistBuddy -c "Set :CFBundleIconFile AppIcon" "${PLIST}" 2>/dev/null \
    || /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string AppIcon" "${PLIST}"
  /usr/libexec/PlistBuddy -c "Set :CFBundleIconName AppIcon" "${PLIST}" 2>/dev/null \
    || /usr/libexec/PlistBuddy -c "Add :CFBundleIconName string AppIcon" "${PLIST}"
  echo "OK  CFBundleName/DisplayName=${DISPLAY_NAME} icon=AppIcon.icns dock=AppIconDock.icns"
fi
TARGET_BUNDLE="${APP_DIR}/${DISPLAY_NAME}.app"
if [[ "${BUNDLE}" != "${TARGET_BUNDLE}" ]]; then
  rm -rf "${TARGET_BUNDLE}"
  mv "${BUNDLE}" "${TARGET_BUNDLE}"
  BUNDLE="${TARGET_BUNDLE}"
  echo "OK  renamed bundle → $(basename "${BUNDLE}")"
fi

# NSWorkspace custom icon (helps AutoFill/helper tiles). Needs a live AppKit
# GUI session on the builder; soft-fail on headless CI is OK — CFBundleIconFile
# + runtime Path A/B still cover Dock.
"${RUN_PY[@]}" - <<PY
from pathlib import Path
from buusdo.macos_dock_icon import set_bundle_finder_icon
app = Path(r"""${BUNDLE}""")
# Full-bleed for Finder custom icon (system still masks when Path A applies).
icns = Path(r"""${ICNS}""")
ok = set_bundle_finder_icon(app, icns)
print("OK  NSWorkspace.setIcon" if ok else "WARN NSWorkspace.setIcon skipped (no GUI AppKit session)")
PY

# MUST codesign after any Info.plist / Resources / icon change.
if ! command -v codesign >/dev/null 2>&1; then
  echo "FATAL: codesign required after plist stamp" >&2
  exit 1
fi
codesign --force --deep --sign - "${BUNDLE}"
codesign --verify --deep --strict --verbose=2 "${BUNDLE}"
echo "OK  ad-hoc codesign verified"

# Use ditto (not zip CLI): plain zip strips nested framework signatures and
# LaunchServices then sees invalid/unsigned subcomponents after unzip.
rm -f "${OUT}/${ZIP_NAME}"
ditto -c -k --keepParent "${BUNDLE}" "${OUT}/${ZIP_NAME}"
echo "OK  ${OUT}/${ZIP_NAME}"
ls -la "${OUT}/${ZIP_NAME}"

# Fail the package job if the zip would not open cleanly for users.
"${RUN_PY[@]}" "${ROOT}/scripts/smoke_macos_zip.py" "${OUT}/${ZIP_NAME}"
