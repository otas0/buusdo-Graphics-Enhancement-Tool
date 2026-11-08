#!/usr/bin/env python3
"""Build buusdo/assets/logo.icns (+ logo_dock.png) from logo.png.

``logo.icns`` is a **full-bleed square** (no pre-baked squircle). macOS Dock /
Finder apply the system mask and inset — pre-rounding makes the tile look too
large or double-masked next to Terminal and other apps.

``logo_dock.png`` keeps a Big Sur–style continuous rounded-rect alpha for tray /
docs previews where Qt cannot rely on the system mask.

Uses PySide6 for the dock PNG mask, then ``sips`` + ``iconutil`` on Darwin. On
other hosts, exits 0 with a skip message so CI elsewhere is not blocked.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "buusdo" / "assets" / "logo.png"
OUT_ICNS = ROOT / "buusdo" / "assets" / "logo.icns"
OUT_DOCK = ROOT / "buusdo" / "assets" / "logo_dock.png"
OUT_DOCK_ICNS = ROOT / "buusdo" / "assets" / "logo_dock.icns"
_BUILD = ROOT / "build"
_ICONSET_DIR = _BUILD / "logo.iconset"
_DOCK_ICONSET_DIR = _BUILD / "logo_dock.iconset"

# Apple HIG app-icon corner radius ≈ 22.37% of the icon side.
_CORNER_RATIO = 0.2237
_DOCK_SIDE = 1024


def _iconset_map() -> list[tuple[int, str]]:
    """iconutil slot names. Build @2x via concat so tooling cannot mangle names."""
    retina = "@" + "2x.png"
    return [
        (16, "icon_16x16.png"),
        (32, "icon_16x16" + retina),
        (32, "icon_32x32.png"),
        (64, "icon_32x32" + retina),
        (128, "icon_128x128.png"),
        (256, "icon_128x128" + retina),
        (256, "icon_256x256.png"),
        (512, "icon_256x256" + retina),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512" + retina),
    ]


def _masked_square(src_path: Path, side: int, inset_ratio: float = 0.0):
    """Squircle-clipped mark. ``inset_ratio`` shrinks the shape inside the canvas.

    ``setApplicationIconImage`` does **not** apply the system Dock mask, so an
    edge-to-edge squircle reads larger than Terminal/Safari. ~12% inset matches
    typical Dock optical size when we must set the tile at runtime.
    """
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QImage, QPainter, QPainterPath

    src = QImage(str(src_path))
    if src.isNull():
        raise RuntimeError(f"failed to load {src_path}")
    margin = max(0, int(round(side * inset_ratio)))
    inner = max(1, side - 2 * margin)
    scaled = src.scaled(
        inner,
        inner,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    out = QImage(side, side, QImage.Format.Format_ARGB32)
    out.fill(0)
    path = QPainterPath()
    r = inner * _CORNER_RATIO
    path.addRoundedRect(QRectF(margin, margin, inner, inner), r, r)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.setClipPath(path)
    painter.drawImage(margin, margin, scaled)
    painter.end()
    return out


# Optical inset so runtime Dock tile matches system-masked neighbors.
_DOCK_RUNTIME_INSET = 0.12


def _save_png(img, path: Path) -> None:
    if not img.save(str(path), "PNG"):
        raise RuntimeError(f"PNG save failed: {path}")


def _sips_resize(src: Path, side: int, dest: Path) -> None:
    """Resize via sips into a plain .png path (never *@2x.png — sips breaks those)."""
    stage = dest.with_name(f".stage_{side}_{dest.stem.replace('.', '_')}.png")
    subprocess.check_call(
        ["sips", "-z", str(side), str(side), str(src), "--out", str(stage)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.check_call(
        [
            "sips",
            "-s",
            "dpiWidth",
            "72",
            "-s",
            "dpiHeight",
            "72",
            str(stage),
            "--out",
            str(stage),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    dest.write_bytes(stage.read_bytes())
    stage.unlink(missing_ok=True)


def main() -> int:
    if not SRC.is_file():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    if sys.platform != "darwin":
        print("skip: logo.icns generation requires macOS (sips + iconutil)")
        return 0
    if not shutil.which("sips") or not shutil.which("iconutil"):
        print("sips/iconutil missing", file=sys.stderr)
        return 1
    try:
        from PySide6.QtGui import QGuiApplication
    except ImportError:
        print("PySide6 required to mask logo.icns", file=sys.stderr)
        return 1

    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication([])

    _BUILD.mkdir(parents=True, exist_ok=True)

    try:
        # Tray/docs: edge squircle. Runtime Dock icns: inset (see below).
        _save_png(_masked_square(SRC, _DOCK_SIDE, inset_ratio=0.0), OUT_DOCK)
        dock_runtime_png = _BUILD / "logo_dock_runtime_1024.png"
        _save_png(
            _masked_square(SRC, _DOCK_SIDE, inset_ratio=_DOCK_RUNTIME_INSET),
            dock_runtime_png,
        )
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    # Full-bleed square master for .icns (system applies Dock squircle + shadow).
    full_bleed = _BUILD / "logo_fullbleed_1024.png"
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QImage

        src_img = QImage(str(SRC))
        if src_img.isNull():
            print(f"failed to load {SRC}", file=sys.stderr)
            return 1
        scaled = src_img.scaled(
            _DOCK_SIDE,
            _DOCK_SIDE,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        # Ensure opaque RGB (no leftover alpha that shrinks visual weight in Dock).
        if scaled.format() != QImage.Format.Format_ARGB32:
            scaled = scaled.convertToFormat(QImage.Format.Format_ARGB32)
        if not scaled.save(str(full_bleed), "PNG"):
            print(f"PNG save failed: {full_bleed}", file=sys.stderr)
            return 1
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    if _ICONSET_DIR.exists():
        shutil.rmtree(_ICONSET_DIR)
    _ICONSET_DIR.mkdir(parents=True)
    for side, name in _iconset_map():
        dest = _ICONSET_DIR / name
        try:
            _sips_resize(full_bleed, side, dest)
        except (RuntimeError, subprocess.CalledProcessError) as exc:
            print(exc, file=sys.stderr)
            return 1
        if not dest.is_file():
            print(f"sips write failed for {name}", file=sys.stderr)
            return 1
    names = sorted(p.name for p in _ICONSET_DIR.iterdir())
    expected = sorted(n for _, n in _iconset_map())
    if names != expected:
        print(f"iconset names mismatch: {names!r}", file=sys.stderr)
        return 1
    tmp_icns = _BUILD / "logo.icns"
    rc = subprocess.call(
        ["iconutil", "-c", "icns", str(_ICONSET_DIR), "-o", str(tmp_icns)]
    )
    if rc != 0 or not tmp_icns.is_file():
        print(
            "iconutil failed (often sandboxed agents). "
            f"logo_dock.png updated; keep existing {OUT_ICNS.name} if present.",
            file=sys.stderr,
        )
        # Leave _ICONSET_DIR for inspection.
        if OUT_DOCK.is_file() and OUT_ICNS.is_file():
            print(f"wrote {OUT_DOCK} ({OUT_DOCK.stat().st_size} bytes)")
            print(f"kept {OUT_ICNS} ({OUT_ICNS.stat().st_size} bytes)")
            return 0
        return 1
    OUT_ICNS.write_bytes(tmp_icns.read_bytes())
    tmp_icns.unlink(missing_ok=True)
    shutil.rmtree(_ICONSET_DIR, ignore_errors=True)

    # Pre-masked + inset icns for NSApplication.setApplicationIconImage_.
    if _DOCK_ICONSET_DIR.exists():
        shutil.rmtree(_DOCK_ICONSET_DIR)
    _DOCK_ICONSET_DIR.mkdir(parents=True)
    dock_runtime_png = _BUILD / "logo_dock_runtime_1024.png"
    for side, name in _iconset_map():
        dest = _DOCK_ICONSET_DIR / name
        try:
            _sips_resize(dock_runtime_png, side, dest)
        except (RuntimeError, subprocess.CalledProcessError) as exc:
            print(exc, file=sys.stderr)
            return 1
    tmp_dock_icns = _BUILD / "logo_dock.icns"
    rc_dock = subprocess.call(
        ["iconutil", "-c", "icns", str(_DOCK_ICONSET_DIR), "-o", str(tmp_dock_icns)]
    )
    if rc_dock != 0 or not tmp_dock_icns.is_file():
        print("iconutil failed for logo_dock.icns", file=sys.stderr)
        return 1
    OUT_DOCK_ICNS.write_bytes(tmp_dock_icns.read_bytes())
    tmp_dock_icns.unlink(missing_ok=True)
    shutil.rmtree(_DOCK_ICONSET_DIR, ignore_errors=True)

    print(f"wrote {OUT_DOCK} ({OUT_DOCK.stat().st_size} bytes)")
    print(f"wrote {OUT_ICNS} ({OUT_ICNS.stat().st_size} bytes)")
    print(f"wrote {OUT_DOCK_ICNS} ({OUT_DOCK_ICNS.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
