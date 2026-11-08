#!/usr/bin/env bash
# Build an unsigned macOS .app zip via PyInstaller (self-contained).
# Gatekeeper will warn — expected without Developer ID / notarization.
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

rm -rf "${WORK}" "${APP_DIR}"
mkdir -p "${WORK}" "${APP_DIR}"

uv run pyinstaller \
  --noconfirm --clean --windowed --onedir \
  --name Buusdo \
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
if [[ -f "${PLIST}" ]]; then
  /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName ${DISPLAY_NAME}" "${PLIST}" 2>/dev/null \
    || /usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string ${DISPLAY_NAME}" "${PLIST}"
  /usr/libexec/PlistBuddy -c "Set :CFBundleName ${DISPLAY_NAME}" "${PLIST}" 2>/dev/null \
    || /usr/libexec/PlistBuddy -c "Add :CFBundleName string ${DISPLAY_NAME}" "${PLIST}"
  echo "OK  CFBundleName/DisplayName=${DISPLAY_NAME}"
fi
TARGET_BUNDLE="${APP_DIR}/${DISPLAY_NAME}.app"
if [[ "${BUNDLE}" != "${TARGET_BUNDLE}" ]]; then
  rm -rf "${TARGET_BUNDLE}"
  mv "${BUNDLE}" "${TARGET_BUNDLE}"
  BUNDLE="${TARGET_BUNDLE}"
  echo "OK  renamed bundle → $(basename "${BUNDLE}")"
fi

rm -f "${OUT}/${ZIP_NAME}"
(
  cd "${APP_DIR}"
  zip -qry "${OUT}/${ZIP_NAME}" "$(basename "${BUNDLE}")"
)
echo "OK  ${OUT}/${ZIP_NAME}"
ls -la "${OUT}/${ZIP_NAME}"
