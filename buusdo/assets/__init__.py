"""Bundled static assets (logo, icons)."""

from __future__ import annotations

from pathlib import Path


def asset_path(name: str) -> Path:
    return Path(__file__).resolve().parent / name


def logo_path() -> Path:
    """App / tray / PE icon source (square mark). Prefer logo.png."""
    logo = asset_path("logo.png")
    if logo.is_file():
        return logo
    mark = asset_path("brand_mark.png")
    if mark.is_file():
        return mark
    return logo


def logo_dock_path() -> Path:
    """Dock / window icon with macOS squircle alpha. Prefer logo_dock.png."""
    dock = asset_path("logo_dock.png")
    if dock.is_file():
        return dock
    return logo_path()


def logo_wordmark_path() -> Path:
    """Horizontal UI wordmark. Prefer logo_wordmark.png; fall back to logo.png."""
    wordmark = asset_path("logo_wordmark.png")
    if wordmark.is_file():
        return wordmark
    return logo_path()


def logo_svg_path() -> Path:
    """Vector wordmark for UI chrome (themeable fills). Generated from wordmark crop."""
    return asset_path("logo.svg")


def brand_mark_path() -> Path:
    """Legacy pixel mark — keep on disk for fallback; do not use in share/UI surfaces."""
    return asset_path("brand_mark.png")


def logo_ico_path() -> Path:
    """Windows .ico derived from logo.png (generated on demand if missing)."""
    return asset_path("logo.ico")


def logo_icns_path() -> Path:
    """macOS .icns derived from logo.png (Mac package track / Finder)."""
    return asset_path("logo.icns")


def logo_dock_icns_path() -> Path:
    """Pre-masked squircle .icns for runtime Dock (setApplicationIconImage)."""
    return asset_path("logo_dock.icns")
