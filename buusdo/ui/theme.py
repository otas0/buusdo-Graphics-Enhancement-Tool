"""Product UI theme — instrument-panel clarity (Nothing × teenage engineering cues).

Light / dark modes share the same layout language: cool surfaces, ink type,
single orange accent, monospace labels, hairline borders, flat fills.
"""

from __future__ import annotations

from typing import Literal

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

ThemeName = Literal["light", "dark"]

# Brand-row chrome (backend chip, theme/lang/companion/about chips).
HEADER_CHIP_VERTICAL_PAD = 12

# Colorblind-safe-ish: blue (ok) / orange (warn+accent) / vermillion (block)
COLOR_OK = "#1F6F8B"
COLOR_WARN = "#FF4F00"
COLOR_BLOCK = "#C73E1D"

_LIGHT = {
    "bg": "#EDEDED",
    "surface": "#FAFAFA",
    "ink": "#111111",
    "muted": "#6B6B6B",
    "line": "#111111",
    "btn": "#111111",
    "btn_text": "#FAFAFA",
    "btn_secondary": "#E4E4E4",
    "btn_hover": "#DADADA",
    "btn_pressed": "#CFCFCF",
    "disabled_fg": "#9A9A9A",
    "disabled_border": "#BDBDBD",
    "disabled_bg": "#EFEFEF",
    "list_rule": "#E2E2E2",
    "grid": "#D0D0D0",
    "alt_base": "#E6E6E6",
    "scroll": "#B5B5B5",
    "primary_hover": "#2A2A2A",
}

_DARK = {
    "bg": "#1A1A1A",
    "surface": "#242424",
    "ink": "#F2F2F2",
    "muted": "#9A9A9A",
    "line": "#F2F2F2",
    "btn": "#F2F2F2",
    "btn_text": "#111111",
    "btn_secondary": "#2E2E2E",
    "btn_hover": "#3A3A3A",
    "btn_pressed": "#444444",
    "disabled_fg": "#666666",
    "disabled_border": "#444444",
    "disabled_bg": "#222222",
    "list_rule": "#333333",
    "grid": "#333333",
    "alt_base": "#2A2A2A",
    "scroll": "#555555",
    "primary_hover": "#FFFFFF",
}

# Mutable module colors — updated by apply_theme()
COLOR_BG = _LIGHT["bg"]
COLOR_SURFACE = _LIGHT["surface"]
COLOR_INK = _LIGHT["ink"]
COLOR_MUTED = _LIGHT["muted"]
COLOR_LINE = _LIGHT["line"]
COLOR_BTN = _LIGHT["btn"]
COLOR_BTN_TEXT = _LIGHT["btn_text"]
COLOR_BTN_SECONDARY = _LIGHT["btn_secondary"]
COLOR_TEXT = COLOR_INK

_current: ThemeName = "light"


def current_theme() -> ThemeName:
    return _current


def _mono_family() -> str:
    return "Menlo, Courier New, monospace"


def header_chip_height() -> int:
    """Shared brand-row chip height — keep in sync with stylesheet max-height."""
    return 28


def style_brand_chip(widget: QWidget) -> None:
    """Apply shared header chrome: ``headerChip`` + identical fixed height.

    Brand-row controls must be ``QPushButton`` (not ``QLabel``): QLabel +
    stylesheet border/padding ignores fixed height and paints a taller box.
    """
    from PySide6.QtWidgets import QSizePolicy

    h = header_chip_height()
    widget.setObjectName("headerChip")
    widget.setFixedHeight(h)
    widget.setMinimumHeight(h)
    widget.setMaximumHeight(h)
    widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)


def relative_luminance(hex_color: str) -> float:
    """sRGB relative luminance (0..1) for WCAG-style contrast checks."""

    def _chan(c: int) -> float:
        x = c / 255.0
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4

    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _chan(r) + 0.7152 * _chan(g) + 0.0722 * _chan(b)


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    l1 = relative_luminance(fg_hex)
    l2 = relative_luminance(bg_hex)
    lighter, darker = (l1, l2) if l1 >= l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


def apply_dark_theme(app: QApplication) -> None:
    """Legacy alias — applies the product theme (default light)."""
    apply_theme(app, "light")


def apply_product_theme(app: QApplication) -> None:
    apply_theme(app, "light")


def apply_theme(app: QApplication, mode: ThemeName = "light") -> None:
    global COLOR_BG, COLOR_SURFACE, COLOR_INK, COLOR_MUTED, COLOR_LINE
    global COLOR_BTN, COLOR_BTN_TEXT, COLOR_BTN_SECONDARY, COLOR_TEXT, _current

    mode = "dark" if mode == "dark" else "light"
    _current = mode
    c = _DARK if mode == "dark" else _LIGHT

    COLOR_BG = c["bg"]
    COLOR_SURFACE = c["surface"]
    COLOR_INK = c["ink"]
    COLOR_MUTED = c["muted"]
    COLOR_LINE = c["line"]
    COLOR_BTN = c["btn"]
    COLOR_BTN_TEXT = c["btn_text"]
    COLOR_BTN_SECONDARY = c["btn_secondary"]
    COLOR_TEXT = COLOR_INK

    app.setStyle("Fusion")
    font = QFont()
    font.setFamilies(["Helvetica Neue", "Arial"])
    font.setPointSize(11)
    app.setFont(font)

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLOR_BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLOR_INK))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLOR_SURFACE))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(c["alt_base"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLOR_INK))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLOR_BTN_SECONDARY))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLOR_INK))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLOR_WARN))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(COLOR_SURFACE))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(COLOR_INK))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(COLOR_MUTED))
    palette.setColor(QPalette.ColorRole.Light, QColor(COLOR_SURFACE))
    palette.setColor(QPalette.ColorRole.Mid, QColor(COLOR_MUTED))
    palette.setColor(QPalette.ColorRole.Dark, QColor(COLOR_INK))
    app.setPalette(palette)

    mono = _mono_family()
    app.setStyleSheet(
        f"""
        QWidget {{
            background: {COLOR_BG};
            color: {COLOR_INK};
        }}
        QMainWindow, QDialog {{
            background: {COLOR_BG};
        }}
        QLabel#brandMark {{
            margin-right: 4px;
            background: transparent;
        }}
        QLabel#brandTitle {{
            font-family: {mono};
            font-size: 26px;
            font-weight: 700;
            letter-spacing: 3px;
            color: {COLOR_INK};
            text-transform: lowercase;
        }}
        QLabel#brandSubtitle {{
            font-family: {mono};
            font-size: 10px;
            color: {COLOR_MUTED};
            letter-spacing: 1.5px;
        }}
        QDialog#instrumentDialog {{
            background: {COLOR_BG};
        }}
        QLabel#sectionLabel, QLabel#backendChip {{
            font-family: {mono};
            font-size: 10px;
            letter-spacing: 1.5px;
            color: {COLOR_MUTED};
            text-transform: uppercase;
        }}
        /* Legacy status badges only (not brand-row; those are QPushButton#headerChip). */
        QLabel#backendChip {{
            border: 1px solid {COLOR_LINE};
            border-radius: 0px;
            padding: 0px 10px;
            background: {COLOR_SURFACE};
        }}
        QLabel#blockTitle {{
            color: {COLOR_BLOCK};
            font-weight: 700;
            font-family: {mono};
        }}
        QLabel#badgeOk {{ color: {COLOR_OK}; font-weight: 600; }}
        QLabel#badgeWarn {{ color: {COLOR_WARN}; font-weight: 600; }}
        QPushButton {{
            font-family: {mono};
            font-size: 11px;
            padding: 7px 12px;
            border: 1px solid {COLOR_LINE};
            border-radius: 2px;
            background: {COLOR_BTN_SECONDARY};
            color: {COLOR_INK};
        }}
        QPushButton:hover {{
            background: {c["btn_hover"]};
        }}
        QPushButton:pressed {{
            background: {c["btn_pressed"]};
        }}
        /* After generic QPushButton so brand chips fully override padding/font.
           Height is forced in style_brand_chip() — do not set min/max-height here
           (Qt treats those as content box and drifts past fixedHeight). */
        QPushButton#headerChip {{
            font-family: {mono};
            font-size: 10px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: {COLOR_INK};
            border: 1px solid {COLOR_LINE};
            border-radius: 0px;
            padding: 0px 10px;
            background: {COLOR_SURFACE};
        }}
        QPushButton#headerChip:hover {{
            background: {c["btn_hover"]};
        }}
        QPushButton#headerChip:pressed {{
            background: {c["btn_pressed"]};
        }}
        QPushButton:disabled {{
            color: {c["disabled_fg"]};
            border-color: {c["disabled_border"]};
            background: {c["disabled_bg"]};
        }}
        QPushButton:default, QPushButton#primaryAction {{
            background: {COLOR_BTN};
            color: {COLOR_BTN_TEXT};
            border: 1px solid {COLOR_BTN};
        }}
        QPushButton:default:hover, QPushButton#primaryAction:hover {{
            background: {c["primary_hover"]};
        }}
        QPushButton#accentAction {{
            background: {COLOR_WARN};
            color: #FFFFFF;
            border: 1px solid {COLOR_WARN};
        }}
        QLineEdit, QSpinBox, QComboBox, QTextEdit {{
            font-family: {mono};
            font-size: 12px;
            padding: 6px 8px;
            border: 1px solid {COLOR_LINE};
            border-radius: 0px;
            background: {COLOR_SURFACE};
            selection-background-color: {COLOR_WARN};
            selection-color: #FFFFFF;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 22px;
        }}
        QListWidget, QTableWidget {{
            font-family: {mono};
            font-size: 12px;
            border: 1px solid {COLOR_LINE};
            border-radius: 0px;
            background: {COLOR_SURFACE};
            outline: none;
            gridline-color: {c["grid"]};
        }}
        QListWidget::item {{
            padding: 8px 10px;
            border-bottom: 1px solid {c["list_rule"]};
        }}
        QListWidget::item:selected, QTableWidget::item:selected {{
            background: {COLOR_WARN};
            color: #FFFFFF;
        }}
        QHeaderView::section {{
            font-family: {mono};
            font-size: 10px;
            letter-spacing: 1px;
            text-transform: uppercase;
            background: {COLOR_BG};
            color: {COLOR_MUTED};
            border: none;
            border-bottom: 1px solid {COLOR_LINE};
            border-right: 1px solid {c["grid"]};
            padding: 6px 8px;
        }}
        QProgressBar {{
            border: 1px solid {COLOR_LINE};
            border-radius: 0px;
            background: {COLOR_SURFACE};
            text-align: center;
            font-family: {mono};
            font-size: 10px;
            height: 16px;
        }}
        QProgressBar::chunk {{
            background: {COLOR_WARN};
        }}
        QCheckBox, QRadioButton {{
            font-family: {mono};
            spacing: 8px;
        }}
        QToolTip {{
            font-family: {mono};
            background: {COLOR_INK};
            color: {COLOR_SURFACE};
            border: none;
            padding: 6px 8px;
        }}
        QStatusBar {{
            font-family: {mono};
            font-size: 11px;
            border-top: 1px solid {COLOR_LINE};
        }}
        QScrollBar:vertical {{
            background: {COLOR_BG};
            width: 10px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {c["scroll"]};
            min-height: 24px;
            border-radius: 0px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        """
    )


def badge_color(kind: str) -> QColor:
    if kind in {"deployed", "ok"}:
        return QColor(COLOR_OK)
    if kind in {"warn", "vkbasalt", "remix"}:
        return QColor(COLOR_WARN)
    if kind in {"block", "unsafe"}:
        return QColor(COLOR_BLOCK)
    return QColor(COLOR_MUTED)
