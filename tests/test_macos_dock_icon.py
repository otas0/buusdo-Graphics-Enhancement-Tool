"""Dock icon helper must not raise without a GUI session."""

from __future__ import annotations

from buusdo.macos_dock_icon import apply_dock_icon, branded_icns_path


def test_branded_icns_path_finds_repo_asset() -> None:
    path = branded_icns_path()
    assert path is not None
    assert path.name in {"logo_dock.icns", "logo.icns", "AppIconDock.icns"}
    assert path.is_file()


def test_apply_dock_icon_returns_bool() -> None:
    # On Linux CI this is False; on macOS agent it may succeed or fail soft.
    assert apply_dock_icon() in (True, False)
