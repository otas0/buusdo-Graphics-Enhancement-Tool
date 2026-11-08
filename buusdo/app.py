"""Application entrypoint."""

from __future__ import annotations

import sys

from buusdo import PRODUCT_NAME, PRODUCT_NAME_SHORT
from buusdo.backends import get_backend
from buusdo.core.crash_report import capture_exception
from buusdo.core.errors import BuusdoError
from buusdo.macos_name import ensure_process_name


def main(argv: list[str] | None = None) -> int:
    # Before Qt (dev/venv only): Dock/menu should not say "Python".
    # Frozen .app skips re-exec; CFBundleName / DisplayName own the chrome.
    ensure_process_name(PRODUCT_NAME_SHORT)

    argv = list(sys.argv if argv is None else argv)
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print(
            "PySide6 is required to launch the UI. Install with: pip install 'buusdo[ui]'",
            file=sys.stderr,
        )
        return 1

    from buusdo.core.config_store import load_settings
    from buusdo.ui.main_window import MainWindow
    from buusdo.ui.theme import ThemeName, apply_theme
    from buusdo.ui.tray_icon import app_icon

    app = QApplication(argv)
    # Short id for settings paths; full official name for user-visible chrome.
    app.setApplicationName(PRODUCT_NAME_SHORT)
    app.setApplicationDisplayName(PRODUCT_NAME)
    app.setOrganizationName(PRODUCT_NAME_SHORT)
    app.setOrganizationDomain("buusdo.app")

    settings = load_settings()
    mode: ThemeName = "dark" if settings.get("ui_theme") == "dark" else "light"
    apply_theme(app, mode)

    # Windows/Linux: Qt owns the window/taskbar icon.
    # macOS: never Qt setWindowIcon. Default = CFBundleIconFile full-bleed AppIcon
    # (system Dock mask ⇒ same optical size as Terminal). Clear any stale
    # setApplicationIconImage from older builds. Set BUUSDO_FORCE_DOCK_ICON=1 to
    # force inset AppIconDock via AppKit if the PyInstaller floppy returns.
    if sys.platform != "darwin":
        app.setWindowIcon(app_icon())

    try:
        backend = get_backend()
    except BuusdoError as exc:
        capture_exception(exc, context={"op": "startup"})
        print(exc, file=sys.stderr)
        return 1
    window = MainWindow(backend=backend)
    window.show()
    if sys.platform == "darwin":
        import os

        from PySide6.QtCore import QTimer

        from buusdo.macos_dock_icon import apply_dock_icon, clear_dock_icon_override

        if os.environ.get("BUUSDO_FORCE_DOCK_ICON") == "1":
            apply_dock_icon()
            QTimer.singleShot(0, apply_dock_icon)
            QTimer.singleShot(250, apply_dock_icon)
        else:
            clear_dock_icon_override()
            QTimer.singleShot(0, clear_dock_icon_override)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
