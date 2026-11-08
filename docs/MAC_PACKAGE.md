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
4. **Do not** stamp a full-bleed `NSWorkspace.setIcon` (Dock shows a hard
   oversized square). Clear any custom Finder stamp; Path A = `CFBundleIconFile`
   only. Then **ad-hoc `codesign`** after every plist/resource/icon change.
5. Pack with `ditto -c -k` (not plain `zip` — preserves nested signatures).
6. Run `scripts/smoke_macos_zip.py` (name + icons + codesign + AppIcon ≠ AppIconDock).

Still **not** notarized — Gatekeeper warnings remain expected. Holds: no
Developer ID / notarization / Authenticode / IPA unless explicitly requested.

## Dock / Finder smoke (manual)

1. `bash scripts/package_macos_bundle.sh`
2. Unzip `dist/buusdo-macos-*.zip`; confirm **full** product folder name.
3. **Replace** any older copy in Applications with this unzipped `.app` (delete the
   old folder first). Do **not** mix a new zip with a leftover Applications
   install — stale `Icon\r` custom stamps / old UI chrome will confuse Dock and
   brand-row checks.
4. Finder: bundle icon is the logo (not blank document / floppy). Confirm no
   `Icon\r` next to `Contents` (`ls -la@` on the `.app`).
5. `open` the app; Dock size should match neighbors; hover name = full product name.
6. If floppy returns: `BUUSDO_FORCE_DOCK_ICON=1 open "/Applications/….app"`.
7. Do **not** judge Dock chrome from a venv / `python -c` launch.

Holds unchanged: no Authenticode / Developer ID notarization / IPA unless a
human explicitly reopens signing.

## Refresh published zip

Use this when a **mac-only** fix must land on an existing GitHub tag (e.g. `v1.1.0`)
without cutting a new version:

1. On a Mac with the fix on `main`: `bash scripts/package_macos_bundle.sh`
2. Confirm `scripts/smoke_macos_zip.py dist/buusdo-macos-*.zip` (includes no `Icon\r`).
3. `git push` the fix commit if it is not on `origin` yet.
4. Overwrite the release asset (example for `v1.1.0`):

```bash
NEW=$(shasum -a 256 dist/buusdo-macos-1.1.0.zip | awk '{print $1}')
# Edit SHA256SUMS: replace the buusdo-macos-1.1.0.zip line with $NEW, keep others.
gh release upload v1.1.0 dist/buusdo-macos-1.1.0.zip SHA256SUMS \
  --repo otas0/buusdo-Graphics-Enhancement-Tool --clobber
```

5. Add a one-liner to the release notes (e.g. `mac zip refreshed YYYY-MM-DD`).
6. Re-download the asset, **delete** any older Applications copy, `ditto` the new
   `.app` in, confirm no `Icon\r`, then `open` and check Dock vs Terminal.
7. Comment on the tracking Issue (e.g. #46) with the new SHA256.

Do **not** stamp `NSWorkspace.setIcon` with a full-bleed icns as part of refresh.
Signing holds stay: no Authenticode / notarization / IPA.

## Non-goals (still)

- No notarization / Gatekeeper blessing required for this config-only track
- Do not block Windows Inno on Mac packaging
- Windows Setup PE `ProductName` ships on the **next** `release.yml` CI run
  (`packaging/buusdo_win_version.txt` already has the full name; no Authenticode)
