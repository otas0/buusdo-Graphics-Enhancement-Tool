"""Brand-row chips share box metrics; line/surface contrast stays visible."""

from __future__ import annotations

import os
import re

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_backend_and_header_chip_share_padding_border() -> None:
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication, QPushButton

    from buusdo.ui.theme import apply_theme, header_chip_height, style_brand_chip

    app = QApplication.instance() or QApplication([])
    apply_theme(app, "dark")
    ss = app.styleSheet()

    # Rule must appear after generic QPushButton and fully specify box metrics.
    btn_pos = ss.find("QPushButton {")
    chip_pos = ss.rfind("QPushButton#headerChip {")
    assert chip_pos > btn_pos >= 0
    block = re.search(
        r"QPushButton#headerChip\s*\{([^}]+)\}",
        ss[chip_pos:],
        flags=re.S,
    )
    assert block, "headerChip box rule missing"
    body = block.group(1)
    assert "padding: 0px 10px" in body
    assert "font-size: 10px" in body
    assert "min-height" not in body
    assert "max-height" not in body

    backend = QPushButton("backend · macos")
    theme = QPushButton("Light")
    lang = QPushButton("English")
    for w in (backend, theme, lang):
        style_brand_chip(w)
        w.ensurePolished()
    h = header_chip_height()
    assert backend.height() == theme.height() == lang.height() == h
    assert backend.minimumHeight() == backend.maximumHeight() == h

    # Theme swap must keep identical heights after re-style (mirrors MainWindow).
    apply_theme(app, "light")
    for w in (backend, theme, lang):
        style_brand_chip(w)
        w.ensurePolished()
    assert backend.height() == theme.height() == lang.height() == header_chip_height()
    app.processEvents()


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_line_surface_contrast_visible(mode: str) -> None:
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from buusdo.ui import theme as theme_mod
    from buusdo.ui.theme import apply_theme, contrast_ratio

    app = QApplication.instance() or QApplication([])
    apply_theme(app, mode)  # type: ignore[arg-type]
    ratio = contrast_ratio(theme_mod.COLOR_LINE, theme_mod.COLOR_SURFACE)
    assert ratio >= 3.0, f"{mode}: line/surface contrast {ratio:.2f} < 3"
    app.processEvents()
