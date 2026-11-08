#!/usr/bin/env python3
"""Fail packaging/CI if a macOS release zip cannot launch cleanly.

Checks (no GUI required — agent/CI safe):
  - Zip top-level is ``{PRODUCT_NAME}.app``
  - Info.plist CFBundleName / CFBundleDisplayName == PRODUCT_NAME
  - CFBundleIconFile resource exists under Contents/Resources
  - ``codesign --verify --deep --strict`` succeeds (ad-hoc OK)

Optional: set BUUSDO_SMOKE_OPEN=1 on a real Mac GUI session to also ``open``
the bundle briefly (not used in CI by default).
"""

from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def _die(msg: str) -> None:
    print(f"FATAL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    from buusdo import PRODUCT_NAME

    if len(argv) < 2:
        _die(f"usage: {argv[0]} path/to/buusdo-macos-*.zip")

    zip_path = Path(argv[1]).resolve()
    if not zip_path.is_file():
        _die(f"missing zip: {zip_path}")

    expected_app = f"{PRODUCT_NAME}.app"
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        if not names:
            _die("empty zip")
        top = names[0].split("/", 1)[0]
        if top != expected_app:
            _die(
                f"zip top-level is {top!r}, expected {expected_app!r} "
                "(full product name for Dock/Finder)"
            )

    with tempfile.TemporaryDirectory(prefix="buusdo-macos-smoke-") as tmp:
        tmp_path = Path(tmp)
        # Prefer ditto so nested codesign survives (matches packaging).
        if shutil.which("ditto"):
            rc = subprocess.run(
                ["ditto", "-x", "-k", str(zip_path), str(tmp_path)],
                capture_output=True,
                text=True,
            )
            if rc.returncode != 0:
                _die(f"ditto extract failed: {rc.stderr.strip() or rc.stdout.strip()}")
        else:
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(tmp_path)

        app = tmp_path / expected_app
        if not app.is_dir():
            # ditto --keepParent may nest as basename under tmp
            nested = list(tmp_path.glob(f"**/{expected_app}"))
            if len(nested) == 1:
                app = nested[0]
            else:
                _die(f"extracted bundle missing: {app}")

        plist_path = app / "Contents" / "Info.plist"
        if not plist_path.is_file():
            _die(f"missing Info.plist in {app}")
        with plist_path.open("rb") as fh:
            pl = plistlib.load(fh)

        for key in ("CFBundleName", "CFBundleDisplayName"):
            val = pl.get(key)
            if val != PRODUCT_NAME:
                _die(f"{key}={val!r}, expected {PRODUCT_NAME!r}")

        icon_key = str(pl.get("CFBundleIconFile") or "").strip()
        if not icon_key:
            _die("CFBundleIconFile missing")
        # macOS accepts with or without .icns suffix
        candidates = [
            app / "Contents" / "Resources" / icon_key,
            app / "Contents" / "Resources" / f"{icon_key}.icns",
        ]
        if not any(p.is_file() for p in candidates):
            _die(f"icon resource missing for CFBundleIconFile={icon_key!r}")
        import hashlib

        def _sha(p: Path) -> str:
            return hashlib.sha256(p.read_bytes()).hexdigest()

        # PyInstaller default floppy+Python must not remain as icon-windowed.icns
        windowed = app / "Contents" / "Resources" / "icon-windowed.icns"
        branded = app / "Contents" / "Resources" / "AppIcon.icns"
        if windowed.is_file() and branded.is_file() and _sha(windowed) != _sha(branded):
            _die(
                "icon-windowed.icns is not the branded AppIcon.icns "
                "(PyInstaller default would show in Dock)"
            )
        dock_icns = app / "Contents" / "Resources" / "AppIconDock.icns"
        if not dock_icns.is_file():
            _die("AppIconDock.icns missing (pre-masked runtime Dock tile)")
        if not branded.is_file():
            _die("AppIcon.icns missing (full-bleed CFBundleIconFile)")
        # Full-bleed AppIcon vs inset AppIconDock must differ (size strategy).
        if _sha(branded) == _sha(dock_icns):
            _die(
                "AppIcon.icns and AppIconDock.icns are identical — "
                "expected full-bleed vs inset (~12%) Dock assets"
            )
        if branded.stat().st_size == dock_icns.stat().st_size:
            _die(
                "AppIcon.icns and AppIconDock.icns have the same byte size — "
                "expected distinct full-bleed vs inset assets"
            )

        exe_name = pl.get("CFBundleExecutable")
        exe = app / "Contents" / "MacOS" / str(exe_name)
        if not exe.is_file():
            _die(f"CFBundleExecutable missing: {exe}")

        # Custom Finder stamp (Icon\r + resource fork) → hard oversized Dock square.
        custom_icon = app / "Icon\r"
        if custom_icon.exists():
            _die(
                "bundle has Finder custom icon (Icon\\r) — "
                "clear with clear_bundle_finder_icon; Path A is CFBundleIconFile only"
            )

        if not shutil.which("codesign"):
            _die("codesign not available (required after plist stamp)")
        verify = subprocess.run(
            ["codesign", "--verify", "--deep", "--strict", str(app)],
            capture_output=True,
            text=True,
        )
        if verify.returncode != 0:
            _die(
                "codesign --verify failed (plist/resources changed after sign?). "
                f"stderr={verify.stderr.strip() or verify.stdout.strip()}"
            )

        if os.environ.get("BUUSDO_SMOKE_OPEN") == "1":
            # Best-effort LaunchServices open; do not require the process to stay
            # up in headless/agent contexts.
            open_rc = subprocess.run(["open", str(app)], capture_output=True, text=True)
            if open_rc.returncode != 0:
                _die(f"open failed: {open_rc.stderr.strip() or open_rc.stdout.strip()}")

    print(f"OK  smoke_macos_zip: {zip_path.name} name+icon+codesign")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
