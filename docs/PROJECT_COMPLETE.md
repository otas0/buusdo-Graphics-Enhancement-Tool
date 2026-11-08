# Project complete

**Date:** 2026-11-06  
**Final shelf:** [v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0)

## Verdict

**buusdo Graphics Enhancement Tool** product track is **finished** at the current GitHub shelf:

| Product | Status |
|---------|--------|
| Desktop Windows / macOS / Linux + wheel | Shipped unsigned |
| Android companion APK | Shipped sideload (`buusdo-companion.apk`) |
| iOS companion | Source under `mobile/flutter/ios/` only — **no IPA** (no Apple certs) |
| Codesign / notarization / Authenticode | **Cancelled** — see [CODE_SIGNING.md](CODE_SIGNING.md) |
| Phase 3 DWM HDR | Remains isolated (`phase3/dwm-hdr`); not part of this product |
| App Store / Play Store | Never planned for this track |

MVP in-scope work ([MVP.md](MVP.md)) and the 1.1.0 companion cut
([RELEASE_1.1.0.md](RELEASE_1.1.0.md)) are satisfied without certificates.

## What “complete” means

- No further feature work, certs, store submission, or IPA packaging.
- Optional **fixes-only** patches only if a real user files a `launch` / `scan` /
  `companion` Issue and a maintainer chooses to cut a patch tag.
- Agent holds (LAN HTTPS, phase3 merge, `gh auth refresh`) stay off unless a
  human reopens the track.

## Open feedback (non-blocking)

Post-ship companion reports were welcome but **not** product gates. Closing the
track does not require waiting on them.
