---
name: Bug report
about: Report a problem with buusdo (MVP / preview)
title: ""
labels: bug
assignees: ""
---

> **Labels:** post-install / missing icon / won't start → `launch`; Steam library scan failures → `scan`.

**Platform**
- OS / version:
- buusdo version / commit / wheel filename:
- Backend shown in UI (windows / linux / macos):

**macOS display / launch** (skip if not macOS)
- App won't open / Gatekeeper / `kLSNoExecutableErr`? (yes/no):
- Menu bar name wrong (short "Buusdo" / "Python" instead of full product name)? (yes/no):
- Dock icon blank document / wrong tile? (yes/no):
- How you launched (Finder `.app` / Terminal `open` / venv `python -m`):

**What you did**
1.
2.

**What you expected**

**What happened**
(paste status line / traceback; redact personal paths if needed)

**Kits**
- ReShade kit path set? (yes/no — do not paste proprietary binaries)
- OptiScaler kit path set? (yes/no)

**MVP notes**
- Supported preview targets: Windows, Linux, and macOS (capabilities differ; macOS is config-only).
- DWM HDR injection is Phase 3 and should stay unavailable.
- Startup / missing app icon after install → add label `launch`.
- Library scan problems → add label `scan`.
- `0.1.1` is fixes-only after real `launch`/`scan` Issues; no feature requests here.
