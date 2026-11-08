# Code signing

**Status (2026-11-06): cancelled — will not ship.**

Product decision: no Apple Developer ID / notarization / staple, and no Windows
Authenticode, for any buusdo release. The GitHub shelf stays **unsigned** forever
for this project track. SmartScreen / Gatekeeper warnings are expected and
documented in the [user guide](user-guide/README.md).

Historical prep notes below are **archived** for reference only. Do not buy
certs, do not dry-run `signtool` / `notarytool` for ship, and do not attach
signed Setup / `.app` artifacts.

## Why unsigned is enough

- MVP and [RELEASE_1.1.0.md](RELEASE_1.1.0.md) listed codesign as non-blocking.
- v1.1.0 published desktop + companion APK without signing.
- Project track is **complete** at that shelf; signing is out of scope permanently.

## Archived: Windows (Authenticode) — do not run for ship

```bat
signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 /a dist\buusdo.exe
signtool verify /pa dist\buusdo.exe
```

## Archived: macOS (Developer ID) — do not run for ship

```bash
bash scripts/sign_and_notarize_macos.sh
```

CI `installer.yml` Authenticode inputs remain fail-closed defaults (`false`).
Leave them off.

## Optional: end-user / maintainer self-sign (not ship)

If **you** already have a Developer ID, you may re-sign a **local** `.app` for
your own machines or your own redistribution. That does **not** bless the public
GitHub zip for everyone else. Steps and caveats:
[MAC_PACKAGE.md — Optional: re-sign with your own Developer ID](MAC_PACKAGE.md).

## Related

- Project complete: [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)
- Honesty / unsigned UX: [user-guide/en.md](user-guide/en.md)
- macOS package / Dock: [MAC_PACKAGE.md](MAC_PACKAGE.md)
