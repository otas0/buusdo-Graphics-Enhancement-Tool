# macOS package track (config-only)

macOS is a **supported** platform with a config-only enhancement path (C5 — no
injection). This note is the Dock/Finder icon checklist for the Mac `.app`
package track.

## Icon assets

| File | Role |
|------|------|
| `buusdo/assets/logo.png` | Source square mark (UI / Windows ICO) |
| `buusdo/assets/logo.icns` | **Full-bleed** square for `CFBundleIconFile` / Finder |
| `buusdo/assets/logo_dock.png` | Edge squircle PNG (tray / docs) |
| `buusdo/assets/logo_dock.icns` | **Inset (~12%)** pre-masked squircle for runtime AppKit |

Regenerate on macOS: `uv run python scripts/generate_logo_icns.py`.

## Two Dock paths (size strategy)

**Path A — default (preferred): CFBundleIconFile**

1. Bundle stamps full-bleed `AppIcon.icns` (+ overwrite PyInstaller `icon-windowed.icns`).
2. `Info.plist` `CFBundleIconFile` / `CFBundleIconName` = `AppIcon`.
3. At runtime **do not** call Qt `setWindowIcon` and **do not** call
   `setApplicationIconImage` (clear any stale override).
4. Dock applies the **system** squircle + optical size → matches Terminal/Safari.

**Path B — fallback: inset AppKit override**

Use only if Path A still shows the PyInstaller floppy+Python tile while running:

1. Ship inset `AppIconDock.icns` / `logo_dock.icns` in `Contents/Resources`.
2. Set env `BUUSDO_FORCE_DOCK_ICON=1` before launch, or call
   `buusdo.macos_dock_icon.apply_dock_icon()`.
3. That uses `NSApplication.setApplicationIconImage_` with the **inset** mask.
   Edge-to-edge masks look oversized next to other Dock apps; full-bleed without
   a mask becomes a hard square.

Never use Qt `setWindowIcon` on macOS for Dock chrome.

## Packaging (PyInstaller zip)

`scripts/package_macos_bundle.sh` must:

1. Pass `--icon buusdo/assets/logo.icns`; stamp `CFBundleIconFile=AppIcon`.
2. Copy full-bleed → `AppIcon.icns` / `icon-windowed.icns`; copy inset →
   `AppIconDock.icns`.
3. Set `CFBundleName` / `CFBundleDisplayName` to `PRODUCT_NAME`, rename `.app`
   folder to the full product name.
4. Optionally `NSWorkspace.setIcon:forFile:` (needs a live AppKit session on the
   builder); then **ad-hoc `codesign`** after every plist/resource/icon change.
5. Pack with `ditto -c -k` (not plain `zip` — preserves nested signatures).
6. Run `scripts/smoke_macos_zip.py` (name + icons + codesign + AppIcon ≠ AppIconDock).

Still **not** notarized — Gatekeeper warnings remain expected. Holds: no
Developer ID / notarization / Authenticode / IPA unless explicitly requested.

## Dock / Finder smoke (manual)

1. `bash scripts/package_macos_bundle.sh`
2. Unzip `dist/buusdo-macos-*.zip`; confirm **full** product folder name.
3. Finder: bundle icon is the logo (not blank document / floppy).
4. `open` the app; Dock size should match neighbors; hover name = full product name.
5. If floppy returns: `BUUSDO_FORCE_DOCK_ICON=1 open "/Applications/….app"`.
6. Do **not** judge Dock chrome from a venv / `python -c` launch.

## Non-goals (still)

- No notarization / Gatekeeper blessing required for this config-only track
- Do not block Windows Inno on Mac packaging
- Windows Setup PE `ProductName` ships on the **next** `release.yml` CI run
  (`packaging/buusdo_win_version.txt` already has the full name; no Authenticode)
