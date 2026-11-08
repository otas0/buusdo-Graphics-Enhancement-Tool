# -*- mode: python ; coding: utf-8 -*-
# PyInstaller onefile (Windows installer payload). icon=logo.ico.
# Usage: pyinstaller packaging/pyinstaller_buusdo.spec
from pathlib import Path

# SPECPATH is the directory containing this .spec (PyInstaller 5/6).
_spec = Path(SPECPATH).resolve()  # noqa: F821
SPEC_DIR = _spec if _spec.is_dir() else _spec.parent
ROOT = SPEC_DIR.parent
ENTRY = ROOT / "buusdo" / "app.py"
ICO = ROOT / "buusdo" / "assets" / "logo.ico"
VERSION = ROOT / "packaging" / "buusdo_win_version.txt"
if not ENTRY.is_file():
    raise SystemExit(f"entry missing: {ENTRY}")

a = Analysis(  # noqa: F821
    [str(ENTRY)],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "buusdo" / "assets"), "buusdo/assets"),  # includes logo_wordmark.png
        (str(ROOT / "buusdo" / "locales"), "buusdo/locales"),
    ],
    hiddenimports=["buusdo"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="buusdo",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICO) if ICO.is_file() else None,
    version=str(VERSION) if VERSION.is_file() else None,
)
