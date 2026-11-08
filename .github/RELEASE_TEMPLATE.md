# buusdo Graphics Enhancement Tool $VERSION

**Full release** (not preview). **Unsigned · GitHub only** — not App Store / Play Store.
SmartScreen / Gatekeeper warnings are expected.

## Assets

| Platform | Asset | Notes |
|----------|-------|-------|
| Windows | `buusdo-setup-$VERSION.exe` | Inno installer (unsigned) |
| macOS | `buusdo-macos-$VERSION.zip` | `buusdo Graphics Enhancement Tool.app` (unsigned) |
| Linux | `buusdo-linux-$VERSION.tar.gz` + `install_linux.sh` | Onedir and/or wheel helper |
| All | `buusdo-$VERSION-py3-none-any.whl` | Universal pip install |
| Android companion | `buusdo-companion.apk` | Sideload; cleartext LAN HTTP; **not** Play Store |
| iOS companion | — | Source under `mobile/flutter/ios/` (**no IPA** — certs cancelled) |

## Install

- **Windows:** run Setup (SmartScreen may warn).
- **macOS:** unzip → open `buusdo Graphics Enhancement Tool.app` (Gatekeeper may warn; right-click → Open).
- **Linux:** `bash install_linux.sh` next to the wheel, or extract the onedir tarball.
- **Any OS (wheel):** `pip install buusdo-$VERSION-py3-none-any.whl "PySide6-Essentials==6.12.0"` then `python -m buusdo`.
- **Android:** download `buusdo-companion.apk` → sideload. Pair with desktop Companion (LAN URL + code). See [MOBILE.md](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/blob/main/docs/MOBILE.md).

## What's new (1.1.0 track)

- **Hardware honesty** — About / capabilities rows + [HARDWARE_NOTES.md](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/blob/main/docs/HARDWARE_NOTES.md).
- **Mobile companion (not injection)** — Desktop Companion dialog + Flutter client (`mobile/flutter/`, android/ios sources) + GitHub APK.
- Pair + status + optional request_scan only. Cleartext LAN HTTP in v1 (HTTPS deferred).
- Device pair/status user reports welcome on [Issues](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues) (label `companion`).

## Honesty

- Capabilities differ by OS; **macOS is config-only** (no injection).
- Kits (**ReShade** / **OptiScaler**) are **BYO**, not bundled.
- Phone/tablet companion ≠ mobile injection host; no remote install/inject from the phone.
- No Authenticode / notarization in this build.
- No DWM HDR (Phase 3).
- Never claims “ray tracing enabled”.

## Verify

```bash
shasum -a 256 -c SHA256SUMS
shasum -a 256 -c SHA256SUMS-companion-apk.txt
```

Feedback: https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues
