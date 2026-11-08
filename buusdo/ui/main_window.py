"""Main window — backend-agnostic (C3)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QAction, QColor, QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QSystemTrayIcon,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from buusdo import PRODUCT_NAME
from buusdo.ui.tray_icon import tray_icon
from buusdo.backends import get_backend
from buusdo.core.backend import EnhancementBackend, EnhancementTarget
from buusdo.companion.bindpref import apply_companion_bind_preference
from buusdo.core.config_store import (
    export_configs,
    get_optiscaler_kit_path,
    get_reshade_kit_path,
    import_configs,
    load_settings,
    save_settings,
    set_optiscaler_kit_path,
    set_reshade_kit_path,
    update_game_config,
)
from buusdo.core.conflict_preview import (
    migrate_conflict_export,
    preview_optiscaler_deploy,
    preview_reshade_deploy,
    preview_triple_matrix,
)
from buusdo.backends.windows_display import (
    clear_display_session,
    display_session_status,
    drop_session_ccd_target,
    retry_display_mode,
    retry_hdr_target,
    rollback_display_session,
)
from buusdo.core.crash_report import (
    capture_exception,
    clear_crash_opt_in_audit,
    crash_upload_opted_in,
    export_crash_opt_in_audit,
    redact,
    set_crash_upload_opt_in,
)
from buusdo.core.errors import BuusdoError, UnsafeTargetError
from buusdo.core.graphics_detect import GraphicsApi
from buusdo.core.history import list_events
from buusdo.core.i18n import available_locales, get_locale, locale_display_name, set_locale, t
from buusdo.core.kit_validate import validate_optiscaler_kit, validate_reshade_kit
from buusdo.core.library_progress import resume_scan_status
from buusdo.core.platform_detect import steam_roots
from buusdo.core.recent_games import (
    clear_uninstalled,
    is_greyed,
    list_recent,
    mark_uninstalled,
    push_recent,
)
from buusdo.core.steam_launch import find_localconfig, list_steam_users, write_proton_launch_note
from buusdo.core.steam_uris import (
    DEFAULT_STEAM_URI_CACHE_TTL_S,
    clear_properties_uri_cache,
    game_properties_uri_candidates,
    probe_open_uris,
    set_steam_uri_cache_ttl_s,
    steam_uri_cache_status,
    steam_uri_cache_ttl_s,
    try_steam_uri_candidate,
)
from buusdo.core.transaction import Transaction
from buusdo.core.vkbasalt_template import list_presets
from buusdo.ui.blocked_page import BlockedPage
from buusdo.ui.linux_deploy_dialog import LinuxDeployDialog
from buusdo.ui.scan_worker import assert_gui_thread, start_scan
from buusdo.ui.theme import ThemeName, apply_theme, badge_color, current_theme
from buusdo.ui.tray_icon import make_mark_icon
from buusdo.companion.pairing import PairingDesk
from buusdo.companion.transport import CompanionTransport
from buusdo.ui.about_dialog import show_about_dialog
from buusdo.ui.companion_dialog import make_desktop_companion_host, show_companion_dialog
from buusdo.ui.logo_widget import make_logo_label, refresh_logo_label
from buusdo.ui.selection_utils import clear_row_selections
from buusdo.ui.language_dialog import LanguageDialog, needs_locale_pick
from buusdo.ui.wizard import FirstRunWizard, needs_wizard


class MainWindow(QMainWindow):
    def __init__(self, backend: EnhancementBackend | None = None):
        super().__init__()
        self.setWindowTitle(PRODUCT_NAME)
        self.resize(980, 720)

        # Window/taskbar icon is set in app.py (skipped on macOS so Dock uses
        # Buusdo.app AppIcon.icns instead of a Qt hard-square override).

        self._backend = backend or get_backend()
        self._target: EnhancementTarget | None = None
        self._games: list[EnhancementTarget] = []
        self._filtered: list[EnhancementTarget] = []
        self._scan_thread = None
        self._scan_worker = None
        self._scan_accepting = False
        self._scan_generation = 0
        self._companion_pairing = PairingDesk()
        self._companion_host = make_desktop_companion_host(
            request_scan=self._companion_request_scan,
        )
        self._companion_transport = CompanionTransport(
            host=self._companion_host,
            pairing=self._companion_pairing,
        )
        apply_companion_bind_preference(self._companion_transport)

        settings = load_settings()
        if settings.get("locale") in available_locales():
            set_locale(settings["locale"])

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        brand = QHBoxLayout()
        # Flush wordmark to the top-left corner (no subtitle chrome).
        brand.setContentsMargins(12, 12, 12, 10)
        brand.setSpacing(12)
        self._logo_label = make_logo_label(40, self)
        brand.addWidget(self._logo_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        brand.addStretch(1)
        from buusdo.ui.theme import style_brand_chip

        # Same widget class as other brand chips — QLabel + stylesheet ignores
        # fixed height and paints a taller box than QPushButton#headerChip.
        backend_chip = QPushButton(f"backend · {self._backend.platform_id()}")
        backend_chip.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        backend_chip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        style_brand_chip(backend_chip)
        brand.addWidget(backend_chip, 0, Qt.AlignmentFlag.AlignVCenter)
        self._theme_btn = QPushButton()
        style_brand_chip(self._theme_btn)
        self._theme_btn.clicked.connect(self._toggle_theme)
        self._refresh_theme_button()
        brand.addWidget(self._theme_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        self._lang = None  # legacy combo removed — use search popup
        self._lang_btn = QPushButton(locale_display_name(get_locale()))
        style_brand_chip(self._lang_btn)
        self._lang_btn.setToolTip(t("lang.button"))
        self._lang_btn.clicked.connect(self._open_language_dialog)
        brand.addWidget(self._lang_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        self._btn_companion = QPushButton(t("companion.button"))
        style_brand_chip(self._btn_companion)
        self._btn_companion.clicked.connect(self._show_companion)
        brand.addWidget(self._btn_companion, 0, Qt.AlignmentFlag.AlignVCenter)
        self._companion_chip = QPushButton(t("companion.chip_on"))
        style_brand_chip(self._companion_chip)
        self._companion_chip.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._companion_chip.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._companion_chip.setToolTip(t("companion.chip_open"))
        self._companion_chip.clicked.connect(self._show_companion)
        self._companion_chip.hide()
        brand.addWidget(self._companion_chip, 0, Qt.AlignmentFlag.AlignVCenter)
        self._btn_about = QPushButton(t("about.button"))
        style_brand_chip(self._btn_about)
        self._btn_about.clicked.connect(self._show_about)
        brand.addWidget(self._btn_about, 0, Qt.AlignmentFlag.AlignVCenter)
        self._brand_chips = [
            backend_chip,
            self._theme_btn,
            self._lang_btn,
            self._btn_companion,
            self._companion_chip,
            self._btn_about,
        ]
        outer.addLayout(brand)

        self._stack = QStackedWidget()
        outer.addWidget(self._stack, stretch=1)

        self._home = QWidget()
        home = QVBoxLayout(self._home)
        home.setContentsMargins(8, 4, 8, 8)
        home.setSpacing(10)

        filter_row = QHBoxLayout()
        self._filter_lbl = QLabel(t("label.filter"))
        self._filter_lbl.setObjectName("sectionLabel")
        filter_row.addWidget(self._filter_lbl)
        self._filter = QLineEdit()
        self._filter.setPlaceholderText(t("filter.placeholder"))
        self._filter.setAccessibleName(t("a11y.game_filter"))
        self._filter.textChanged.connect(self._refresh_game_list)
        filter_row.addWidget(self._filter)
        home.addLayout(filter_row)

        self._kits_banner = QLabel("")
        self._kits_banner.setWordWrap(True)
        self._kits_banner.setStyleSheet("color: #FF4F00;")
        self._btn_complete_kits = QPushButton(t("settings.complete_kits"))
        self._btn_complete_kits.setObjectName("accentAction")
        self._btn_complete_kits.clicked.connect(self._complete_kits_setup)
        kits_row = QHBoxLayout()
        kits_row.addWidget(self._kits_banner, stretch=1)
        kits_row.addWidget(self._btn_complete_kits)
        home.addLayout(kits_row)
        self._refresh_kits_banner()

        self._games_lbl = QLabel(t("label.games"))
        self._games_lbl.setObjectName("sectionLabel")
        home.addWidget(self._games_lbl)
        self._game_list = QListWidget()
        self._game_list.setAccessibleName(t("a11y.game_list"))
        self._game_list.currentRowChanged.connect(self._on_game_selected)
        home.addWidget(self._game_list, stretch=1)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFormat("%p%")
        self._progress.setVisible(False)
        home.addWidget(self._progress)

        pref_row = QHBoxLayout()
        self._exe_lbl = QLabel(t("label.exe"))
        pref_row.addWidget(self._exe_lbl)
        self._exe_combo = QComboBox()
        pref_row.addWidget(self._exe_combo, stretch=1)
        self._api_lbl = QLabel(t("label.api"))
        pref_row.addWidget(self._api_lbl)
        self._api_combo = QComboBox()
        self._api_combo.addItem("auto", "")
        for api in GraphicsApi:
            if api is GraphicsApi.UNKNOWN:
                continue
            self._api_combo.addItem(api.value, api.value)
        pref_row.addWidget(self._api_combo)
        home.addLayout(pref_row)

        user_row = QHBoxLayout()
        self._steam_user_lbl = QLabel(t("label.steam_user"))
        user_row.addWidget(self._steam_user_lbl)
        self._steam_user = QComboBox()
        user_row.addWidget(self._steam_user, stretch=1)
        home.addLayout(user_row)
        self._reload_steam_users()

        mode_row = QHBoxLayout()
        self._mode_lbl = QLabel(t("label.mode"))
        mode_row.addWidget(self._mode_lbl)
        self._mode_combo = QComboBox()
        self._reload_mode_combo()
        mode_row.addWidget(self._mode_combo)
        self._vk_lbl = QLabel("vkBasalt")
        mode_row.addWidget(self._vk_lbl)
        self._vk_preset = QComboBox()
        for name in list_presets():
            self._vk_preset.addItem(name, name)
        idx = self._vk_preset.findData("cas")
        if idx >= 0:
            self._vk_preset.setCurrentIndex(idx)
        mode_row.addWidget(self._vk_preset)
        home.addLayout(mode_row)

        self._crash_opt = QCheckBox(t("action.crash_opt_in"))
        self._crash_opt.setChecked(crash_upload_opted_in())
        self._crash_opt.toggled.connect(self._on_crash_opt_toggled)
        home.addWidget(self._crash_opt)
        audit_row = QHBoxLayout()
        self._btn_export_audit = QPushButton(t("action.export_audit"))
        self._btn_clear_audit = QPushButton(t("action.clear_audit"))
        self._btn_export_audit.clicked.connect(self._export_crash_audit)
        self._btn_clear_audit.clicked.connect(self._clear_crash_audit)
        audit_row.addWidget(self._btn_export_audit)
        audit_row.addWidget(self._btn_clear_audit)
        home.addLayout(audit_row)

        ttl_row = QHBoxLayout()
        self._steam_ttl_lbl = QLabel(t("settings.steam_uri_ttl"))
        ttl_row.addWidget(self._steam_ttl_lbl)
        self._steam_ttl = QSpinBox()
        self._steam_ttl.setRange(1, 90)
        self._steam_ttl.setSuffix(t("settings.steam_uri_ttl_suffix"))
        days = max(1, int(round(steam_uri_cache_ttl_s() / 86400)))
        self._steam_ttl.setValue(days)
        self._steam_ttl.setToolTip(
            t("settings.steam_uri_ttl_tip", default_days=DEFAULT_STEAM_URI_CACHE_TTL_S // 86400)
        )
        self._steam_ttl.valueChanged.connect(self._on_steam_ttl_changed)
        ttl_row.addWidget(self._steam_ttl)
        self._btn_clear_steam_uri = QPushButton(t("settings.steam_uri_clear"))
        self._btn_clear_steam_uri.clicked.connect(self._clear_steam_uri_cache)
        ttl_row.addWidget(self._btn_clear_steam_uri)
        self._btn_steam_try_first = QPushButton(t("settings.steam_uri_try_first"))
        self._btn_steam_try_first.setToolTip(t("settings.steam_uri_try_first"))
        self._btn_steam_try_first.clicked.connect(lambda: self._try_open_steam_uri_candidate(0))
        ttl_row.addWidget(self._btn_steam_try_first)
        self._btn_steam_try_next = QPushButton(t("settings.steam_uri_try_next"))
        self._btn_steam_try_next.setToolTip(t("settings.steam_uri_try_next"))
        self._btn_steam_try_next.clicked.connect(self._try_open_next_steam_uri)
        self._btn_steam_try_next.setEnabled(False)
        self._steam_try_next_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self._steam_try_next_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._steam_try_next_shortcut.activated.connect(self._try_open_next_steam_uri)
        self._steam_try_next_shortcut.setEnabled(False)
        ttl_row.addWidget(self._btn_steam_try_next)
        self._steam_uri_try_index = 0
        self._steam_uri_cache_label = QLabel("")
        self._steam_uri_cache_label.setWordWrap(True)
        ttl_row.addWidget(self._steam_uri_cache_label, stretch=1)
        home.addLayout(ttl_row)
        self._refresh_steam_uri_controls()

        self._session_banner = QLabel("")
        self._session_banner.setWordWrap(True)
        self._session_banner.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self._session_banner.setStyleSheet("color: #FF4F00;")
        self._btn_clear_session = QPushButton(t("action.clear_display_session"))
        self._btn_clear_session.clicked.connect(self._clear_display_session)
        self._btn_rollback_now = QPushButton(t("action.rollback_now"))
        self._btn_rollback_now.setObjectName("primaryAction")
        self._btn_rollback_now.clicked.connect(self._rollback_display_now)
        sess_row = QHBoxLayout()
        sess_row.addWidget(self._session_banner, stretch=1)
        sess_row.addWidget(self._btn_rollback_now)
        sess_row.addWidget(self._btn_clear_session)
        home.addLayout(sess_row)
        self._refresh_session_banner()

        self._caps_lbl = QLabel(t("label.capabilities"))
        self._caps_lbl.setObjectName("sectionLabel")
        home.addWidget(self._caps_lbl)
        self._cap_list = QListWidget()
        home.addWidget(self._cap_list)

        self._hist_lbl = QLabel(t("label.history"))
        self._hist_lbl.setObjectName("sectionLabel")
        home.addWidget(self._hist_lbl)
        self._history_list = QListWidget()
        home.addWidget(self._history_list)

        actions_col = QVBoxLayout()
        actions_col.setSpacing(8)
        row_primary = QHBoxLayout()
        row_primary.setSpacing(8)
        row_secondary = QHBoxLayout()
        row_secondary.setSpacing(8)
        self._btn_scan = QPushButton(t("action.scan"))
        self._btn_scan.setObjectName("accentAction")
        self._btn_force = QPushButton(t("action.force_scan"))
        self._btn_cancel = QPushButton(t("action.cancel_scan"))
        self._btn_cancel.setEnabled(False)
        self._btn_preview = QPushButton(t("conflict.title"))
        self._btn_steam = QPushButton(t("proton.open_steam"))
        self._btn_proton_note = QPushButton(t("action.proton_note"))
        self._btn_kit = QPushButton(t("action.kit_reshade"))
        self._btn_opti = QPushButton(t("action.kit_optiscaler"))
        self._btn_install = QPushButton(t("action.deploy"))
        self._btn_install.setObjectName("primaryAction")
        self._btn_install.setDefault(True)
        self._btn_uninstall = QPushButton(t("action.uninstall"))
        self._btn_export = QPushButton(t("action.export"))
        self._btn_import = QPushButton(t("action.import"))
        self._btn_history = QPushButton(t("action.history"))
        for b in (
            self._btn_scan,
            self._btn_force,
            self._btn_cancel,
            self._btn_install,
            self._btn_uninstall,
        ):
            row_primary.addWidget(b)
        for b in (
            self._btn_preview,
            self._btn_steam,
            self._btn_proton_note,
            self._btn_kit,
            self._btn_opti,
            self._btn_export,
            self._btn_import,
            self._btn_history,
        ):
            row_secondary.addWidget(b)
        actions_col.addLayout(row_primary)
        actions_col.addLayout(row_secondary)
        home.addLayout(actions_col)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        self._status.setAccessibleName(t("a11y.status"))
        home.addWidget(self._status)

        self._stack.addWidget(self._home)

        self._btn_scan.clicked.connect(lambda: self._scan_games(force=False))
        self._btn_force.clicked.connect(lambda: self._scan_games(force=True))
        self._btn_cancel.clicked.connect(self._cancel_scan)
        self._btn_preview.clicked.connect(self._on_preview)
        self._btn_steam.clicked.connect(self._open_steam_for_target)
        self._btn_proton_note.clicked.connect(self._write_proton_note)
        self._btn_kit.clicked.connect(self._pick_reshade_kit)
        self._btn_opti.clicked.connect(self._pick_optiscaler_kit)
        self._btn_install.clicked.connect(self._on_install)
        self._btn_uninstall.clicked.connect(self._on_uninstall)
        self._btn_export.clicked.connect(self._on_export)
        self._btn_import.clicked.connect(self._on_import)
        self._btn_history.clicked.connect(self._refresh_history)

        kit = get_reshade_kit_path()
        if kit:
            self._status.setText(f"ReShade: {kit}")
        self._refresh_history()
        self._refresh_capabilities()
        self._setup_tray()

        # Defer first-run wizard until after the window is shown. Running a modal
        # QDialog (and QMessageBox on Skip) during MainWindow.__init__ can abort
        # the process on macOS.
        QTimer.singleShot(0, self._maybe_run_first_run_wizard)

    def _setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self._tray = QSystemTrayIcon(tray_icon(), self)
        self._tray.setToolTip(PRODUCT_NAME)
        show = QAction("Show", self)
        show.triggered.connect(self.showNormal)
        quit_act = QAction("Quit", self)
        quit_act.triggered.connect(self.close)
        from PySide6.QtWidgets import QMenu

        menu = QMenu()
        menu.addAction(show)
        recent_menu = menu.addMenu("Uninstall recent")
        self._tray_recent_menu = recent_menu
        self._rebuild_tray_recent()
        menu.addAction(quit_act)
        self._tray.setContextMenu(menu)
        self._tray.show()

    def _rebuild_tray_recent(self) -> None:
        menu = getattr(self, "_tray_recent_menu", None)
        if menu is None:
            return
        menu.clear()
        for item in list_recent():
            name = str(item.get("name") or "game")
            if is_greyed(item):
                grey = QAction(f"{name} {t('tray.uninstalled')}", self)
                grey.setEnabled(False)
                menu.addAction(grey)
                clear_act = QAction(t("tray.clear_uninstalled"), self)
                clear_act.triggered.connect(
                    lambda _=False, data=item: self._tray_clear_uninstalled(data)
                )
                menu.addAction(clear_act)
            else:
                act = QAction(f"Uninstall {name}", self)
                act.triggered.connect(lambda _=False, data=item: self._tray_uninstall(data))
                menu.addAction(act)
        if menu.isEmpty():
            empty = QAction("(none)", self)
            empty.setEnabled(False)
            menu.addAction(empty)

    def _tray_clear_uninstalled(self, data: dict) -> None:
        name = str(data.get("name") or "game")
        reply = QMessageBox.question(
            self,
            PRODUCT_NAME,
            t("tray.clear_uninstalled_confirm", name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if clear_uninstalled(data):
            # Re-push to the front of recent so the tray order reflects a reinstall.
            push_recent(dict(data))
            self._rebuild_tray_recent()
            self._status.setText(t("tray.clear_uninstalled"))

    def _has_valid_kit(self) -> bool:
        return validate_reshade_kit(get_reshade_kit_path()).ok or validate_optiscaler_kit(
            get_optiscaler_kit_path()
        ).ok

    def _kits_both_valid(self) -> bool:
        return validate_reshade_kit(get_reshade_kit_path()).ok and validate_optiscaler_kit(
            get_optiscaler_kit_path()
        ).ok

    def _missing_kit_side(self) -> str | None:
        """When exactly one kit is valid, return the side that still needs a path."""
        r_ok = validate_reshade_kit(get_reshade_kit_path()).ok
        o_ok = validate_optiscaler_kit(get_optiscaler_kit_path()).ok
        if r_ok and not o_ok:
            return "optiscaler"
        if o_ok and not r_ok:
            return "reshade"
        return None

    def _kit_banner_state(self) -> tuple[str, str]:
        """Return (text, severity): empty | one_side | incomplete."""
        r_path = get_reshade_kit_path()
        o_path = get_optiscaler_kit_path()
        r_ok = validate_reshade_kit(r_path).ok
        o_ok = validate_optiscaler_kit(o_path).ok
        r_set = r_path is not None
        o_set = o_path is not None

        parts: list[str] = []
        # Exactly one kit is valid → dedicated one-side copy.
        if r_ok ^ o_ok:
            parts.append(t("settings.kits_one_side"))
            severity = "one_side"
        else:
            parts.append(t("settings.kits_banner"))
            severity = "empty"

        incomplete = False
        if r_set and not r_ok:
            incomplete = True
            rs = validate_reshade_kit(r_path)
            miss = ", ".join(rs.missing) if rs.missing else rs.message
            parts.append(f"ReShade: {t('wizard.kit_bad')} ({miss})")
        elif not r_set:
            parts.append(f"ReShade: {t('settings.kits_path_empty')}")
        else:
            parts.append(f"ReShade: {t('wizard.kit_ok')}")

        if o_set and not o_ok:
            incomplete = True
            os_ = validate_optiscaler_kit(o_path)
            miss = ", ".join(os_.missing) if os_.missing else os_.message
            parts.append(f"OptiScaler: {t('wizard.kit_bad')} ({miss})")
        elif not o_set:
            parts.append(f"OptiScaler: {t('settings.kits_path_empty')}")
        else:
            parts.append(f"OptiScaler: {t('wizard.kit_ok')}")

        if incomplete and severity != "one_side":
            severity = "incomplete"
        elif incomplete and severity == "one_side":
            # Keep one_side as primary, but prefer red styling when DLL incomplete.
            severity = "incomplete"
        return "\n".join(parts), severity

    def _refresh_kits_banner(self) -> None:
        skipped = bool(load_settings().get("wizard_skipped_kits"))
        # Keep banner while either side is missing/invalid (incl. one-side-valid).
        show = skipped and not self._kits_both_valid()
        if not show:
            self._kits_banner.setText("")
            self._kits_banner.setStyleSheet("")
            self._btn_complete_kits.setVisible(False)
            return
        text, severity = self._kit_banner_state()
        self._kits_banner.setText(text)
        # incomplete: block red; one_side: ok blue; empty: accent orange
        if severity == "incomplete":
            self._kits_banner.setStyleSheet("color: #C73E1D; font-weight: 600;")
        elif severity == "one_side":
            self._kits_banner.setStyleSheet("color: #1F6F8B; font-weight: 600;")
        else:
            self._kits_banner.setStyleSheet("color: #FF4F00;")
        missing = self._missing_kit_side()
        if missing == "reshade":
            self._btn_complete_kits.setText(t("settings.complete_kits_reshade"))
        elif missing == "optiscaler":
            self._btn_complete_kits.setText(t("settings.complete_kits_optiscaler"))
        else:
            self._btn_complete_kits.setText(t("settings.complete_kits"))
        self._btn_complete_kits.setVisible(True)

    def _on_steam_ttl_changed(self, days: int) -> None:
        set_steam_uri_cache_ttl_s(int(days) * 86400)
        self._refresh_steam_uri_controls()
        self._status.setText(t("settings.steam_uri_ttl_saved", days=int(days)))

    def _refresh_steam_uri_controls(self) -> None:
        st = steam_uri_cache_status()
        has_game = bool(self._target and self._target.metadata.get("app_id"))
        if st.get("cached"):
            self._steam_uri_cache_label.setText(
                t("settings.steam_uri_cache_on", template=str(st.get("template") or ""))
            )
            self._btn_clear_steam_uri.setEnabled(True)
            tip = str(st.get("template") or "")
        else:
            self._steam_uri_cache_label.setText(t("settings.steam_uri_cache_off"))
            self._btn_clear_steam_uri.setEnabled(False)
            tip = t("settings.steam_uri_cache_off")
        self._btn_clear_steam_uri.setToolTip(tip)
        self._btn_steam_try_first.setEnabled(has_game)
        # "Try next" only after a failed attempt with remaining candidates.
        remaining = self._steam_uri_candidates_left()
        # Disable after exhaust (remaining == 0) even if try_index advanced.
        can_next = bool(
            has_game
            and getattr(self, "_steam_uri_try_index", 0) > 0
            and remaining > 0
        )
        self._btn_steam_try_next.setEnabled(can_next)
        if remaining <= 0 and getattr(self, "_steam_uri_try_index", 0) > 0:
            self._btn_steam_try_next.setEnabled(False)
            self._btn_steam_try_next.setText(t("settings.steam_uri_try_next"))
            self._btn_steam_try_next.setToolTip(t("settings.steam_uri_try_exhausted", total=len(self._steam_uri_candidates())))
        elif can_next:
            self._btn_steam_try_next.setText(
                t("settings.steam_uri_try_next_count", remaining=remaining)
            )
            uris = self._steam_uri_candidates()
            idx = int(getattr(self, "_steam_uri_try_index", 0))
            next_uri = uris[idx] if 0 <= idx < len(uris) else ""
            tip_next = t(
                "settings.steam_uri_try_next_tip",
                index=idx + 1,
                total=len(uris),
                uri=next_uri,
            )
            self._btn_steam_try_next.setToolTip(
                f"{tip_next}\n{t('settings.steam_uri_try_next_shortcut')}"
            )
        else:
            self._btn_steam_try_next.setText(t("settings.steam_uri_try_next"))
            self._btn_steam_try_next.setToolTip(t("settings.steam_uri_try_next"))
        if hasattr(self, "_steam_try_next_shortcut"):
            self._steam_try_next_shortcut.setEnabled(self._btn_steam_try_next.isEnabled())
        if hasattr(self, "_btn_steam"):
            self._btn_steam.setToolTip(tip)

    def _steam_uri_candidates(self) -> list[str]:
        if not self._target or not self._target.metadata.get("app_id"):
            return []
        return game_properties_uri_candidates(str(self._target.metadata["app_id"]))

    def _steam_uri_candidates_left(self) -> int:
        uris = self._steam_uri_candidates()
        idx = int(getattr(self, "_steam_uri_try_index", 0))
        return max(0, len(uris) - idx)

    def _steam_uri_probe_preview_text(self) -> str:
        """List URI candidates for the selected game after cache clear (no desktop open)."""
        if not self._target or not self._target.metadata.get("app_id"):
            return t("settings.steam_uri_probe_no_game")
        uris = self._steam_uri_candidates()
        return t("settings.steam_uri_probe_preview", uris="\n".join(f"  {u}" for u in uris))

    def _try_open_steam_uri_candidate(self, index: int, *, opener=None) -> None:
        """Open one properties URI candidate by index; offer Try next on failure."""
        uris = self._steam_uri_candidates()
        if not uris:
            self._steam_uri_try_index = 0
            self._toast(t("settings.steam_uri_probe_no_game"))
            self._refresh_steam_uri_controls()
            return

        if opener is None:
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices

            def opener(u: str) -> bool:
                return bool(QDesktopServices.openUrl(QUrl(u)))

        result = try_steam_uri_candidate(uris, index, opener=opener, cache_success=True)
        self._steam_uri_try_index = int(result.get("next_index") or 0)
        self._refresh_steam_uri_controls()
        total = int(result.get("total") or 0)
        uri = result.get("uri")
        if result.get("opened"):
            self._toast(
                t(
                    "settings.steam_uri_try_first_ok",
                    index=int(result.get("index") or 0) + 1,
                    total=total,
                    uri=str(uri or ""),
                )
            )
            return
        if result.get("exhausted"):
            self._toast(t("settings.steam_uri_try_exhausted", total=total))
            return
        self._toast(
            t(
                "settings.steam_uri_try_first_fail",
                index=int(result.get("index") or 0) + 1,
                total=total,
                uri=str(uri or ""),
            )
        )

    def _try_open_next_steam_uri(self) -> None:
        self._try_open_steam_uri_candidate(int(getattr(self, "_steam_uri_try_index", 0)))

    def _clear_steam_uri_cache(self) -> None:
        cleared = clear_properties_uri_cache()
        self._steam_uri_try_index = 0
        self._refresh_steam_uri_controls()
        preview = self._steam_uri_probe_preview_text()
        base = t("settings.steam_uri_cleared") if cleared else t("settings.steam_uri_clear_empty")
        self._status.setText(f"{base}\n{preview}")
        if hasattr(self, "_tray"):
            self._tray.showMessage(PRODUCT_NAME, base)

    def _toast(self, message: str) -> None:
        self._status.setText(message)
        if hasattr(self, "_tray"):
            self._tray.showMessage(PRODUCT_NAME, message)

    def _kit_side_toast(self, *, side: str, saved: bool) -> None:
        if not saved:
            self._toast(t("settings.kit_side_cancelled"))
            return
        if self._kits_both_valid():
            self._toast(t("settings.kit_both_ready"))
        else:
            self._toast(t("settings.kit_still_missing", side=side))

    def _complete_kits_setup(self) -> None:
        focus = self._missing_kit_side()
        if focus == "reshade":
            # One-side CTA: jump straight to the missing side picker, then toast.
            ok = self._pick_reshade_kit()
            self._kit_side_toast(side="ReShade", saved=ok)
        elif focus == "optiscaler":
            ok = self._pick_optiscaler_kit()
            self._kit_side_toast(side="OptiScaler", saved=ok)
        else:
            FirstRunWizard(self, focus_side=focus).exec()
            if self._kits_both_valid():
                self._toast(t("settings.kit_both_ready"))
        data = load_settings()
        if self._kits_both_valid():
            data["wizard_skipped_kits"] = False
            data["wizard_completed"] = True
            save_settings(data)
        self._refresh_kits_banner()
        kit = get_reshade_kit_path()
        if kit and focus is None and not self._kits_both_valid():
            self._status.setText(f"ReShade: {kit}")

    def _tray_uninstall(self, data: dict) -> None:
        name = str(data.get("name") or "game")
        reply = QMessageBox.question(
            self,
            PRODUCT_NAME,
            t("action.confirm_uninstall", name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        target = EnhancementTarget(
            name=name,
            install_path=Path(str(data.get("install_path"))),
            executable=Path(data["executable"]) if data.get("executable") else None,
            metadata=dict(data.get("metadata") or {}),
        )
        try:
            result = self._backend.uninstall(target)
            mark_uninstalled(data)
            self._status.setText(result.message)
            if hasattr(self, "_tray"):
                self._tray.showMessage(PRODUCT_NAME, result.message)
            self._rebuild_tray_recent()
            self._refresh_game_list()
            self._refresh_history()
            self._refresh_session_banner()
        except (BuusdoError, UnsafeTargetError) as exc:
            QMessageBox.warning(self, PRODUCT_NAME, str(exc))

    def _maybe_run_first_run_wizard(self) -> None:
        # After install / first launch: language preference before kit setup.
        settings = load_settings()
        if needs_locale_pick(settings):
            try:
                dlg = LanguageDialog(self, first_run=True)
                dlg.exec()
                loc = dlg.selected_locale() or "en"
                set_locale(loc)
                settings["locale"] = loc
                save_settings(settings)
                self._apply_locale_to_chrome()
            except Exception as exc:
                capture_exception(exc, context={"op": "first_run_locale"})
                set_locale("en")
                settings["locale"] = "en"
                save_settings(settings)
        if not needs_wizard():
            self._refresh_kits_banner()
            return
        try:
            FirstRunWizard(self).exec()
        except Exception as exc:
            capture_exception(exc, context={"op": "first_run_wizard"})
            QMessageBox.warning(self, PRODUCT_NAME, str(exc))
        self._refresh_kits_banner()

    def _open_language_dialog(self) -> None:
        if self._scan_accepting:
            return
        # Brief disable avoids re-entry while the modal + retranslate runs.
        self._lang_btn.setEnabled(False)
        try:
            dlg = LanguageDialog(self, first_run=False)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return
            loc = dlg.selected_locale()
            if not loc or loc == get_locale():
                self._lang_btn.setText(locale_display_name(get_locale()))
                return
            set_locale(loc)
            data = load_settings()
            data["locale"] = loc
            save_settings(data)
            self._apply_locale_to_chrome()
        finally:
            if not self._scan_accepting:
                self._lang_btn.setEnabled(True)

    def _apply_locale_to_chrome(self) -> None:
        """Rebind *all* catalog-driven chrome after set_locale (no mixed leftovers)."""
        prev = self._selection_key(self._target)
        self._lang_btn.setText(locale_display_name(get_locale()))
        self._lang_btn.setToolTip(t("lang.button"))
        self._btn_about.setText(t("about.button"))
        self._btn_companion.setText(t("companion.button"))
        self._refresh_companion_chip()
        self._refresh_theme_button()
        self._btn_scan.setText(t("action.scan"))
        self._btn_force.setText(t("action.force_scan"))
        self._btn_cancel.setText(t("action.cancel_scan"))
        self._btn_install.setText(t("action.deploy"))
        self._btn_uninstall.setText(t("action.uninstall"))
        self._btn_preview.setText(t("conflict.title"))
        self._btn_steam.setText(t("proton.open_steam"))
        self._btn_proton_note.setText(t("action.proton_note"))
        self._btn_kit.setText(t("action.kit_reshade"))
        self._btn_opti.setText(t("action.kit_optiscaler"))
        self._btn_export.setText(t("action.export"))
        self._btn_import.setText(t("action.import"))
        self._btn_history.setText(t("action.history"))
        self._btn_export_audit.setText(t("action.export_audit"))
        self._btn_clear_audit.setText(t("action.clear_audit"))
        self._btn_clear_session.setText(t("action.clear_display_session"))
        self._btn_rollback_now.setText(t("action.rollback_now"))
        self._btn_clear_steam_uri.setText(t("settings.steam_uri_clear"))
        self._btn_steam_try_first.setText(t("settings.steam_uri_try_first"))
        self._btn_steam_try_first.setToolTip(t("settings.steam_uri_try_first"))
        self._crash_opt.setText(t("action.crash_opt_in"))
        self._filter_lbl.setText(t("label.filter"))
        self._games_lbl.setText(t("label.games"))
        self._hist_lbl.setText(t("label.history"))
        self._caps_lbl.setText(t("label.capabilities"))
        self._exe_lbl.setText(t("label.exe"))
        self._api_lbl.setText(t("label.api"))
        self._steam_user_lbl.setText(t("label.steam_user"))
        self._mode_lbl.setText(t("label.mode"))
        self._steam_ttl_lbl.setText(t("settings.steam_uri_ttl"))
        self._steam_ttl.setSuffix(t("settings.steam_uri_ttl_suffix"))
        self._steam_ttl.setToolTip(
            t(
                "settings.steam_uri_ttl_tip",
                default_days=DEFAULT_STEAM_URI_CACHE_TTL_S // 86400,
            )
        )
        self._filter.setPlaceholderText(t("filter.placeholder"))
        self._filter.setAccessibleName(t("a11y.game_filter"))
        self._game_list.setAccessibleName(t("a11y.game_list"))
        self._status.setAccessibleName(t("a11y.status"))
        refresh_logo_label(self._logo_label)
        self._reload_mode_combo()
        self._reload_steam_users()
        self._refresh_kits_banner()
        self._refresh_session_banner()
        self._refresh_steam_uri_controls()
        self._refresh_history()
        # Badges / capability titles are locale-sensitive — rebuild in the active language.
        self._refresh_game_list()
        self._restore_selection(prev)
        self._refresh_capabilities()
        if self._target is None and self._games:
            self._status.setText(t("scan.games_count", count=len(self._games)))

    def _refresh_theme_button(self) -> None:
        # Button shows the mode you can switch *to*.
        if current_theme() == "dark":
            self._theme_btn.setText(t("theme.to_light"))
        else:
            self._theme_btn.setText(t("theme.to_dark"))

    def _restyle_brand_chips(self) -> None:
        from buusdo.ui.theme import style_brand_chip

        for w in getattr(self, "_brand_chips", []):
            style_brand_chip(w)

    def _sync_brand_about_visibility(self) -> None:
        """Hide About on narrow widths so brand chips stay one row."""
        about = getattr(self, "_btn_about", None)
        if about is None:
            return
        about.setVisible(self.width() >= 960)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._sync_brand_about_visibility()

    def _toggle_theme(self) -> None:
        nxt: ThemeName = "light" if current_theme() == "dark" else "dark"
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, nxt)
        data = load_settings()
        data["ui_theme"] = nxt
        save_settings(data)
        refresh_logo_label(self._logo_label)
        self._refresh_theme_button()
        # Stylesheet swap can drift chip metrics — re-apply fixed headerChip height.
        self._restyle_brand_chips()
        self._sync_brand_about_visibility()

    def _reload_steam_users(self) -> None:
        current = self._steam_user.currentData() if self._steam_user.count() else None
        self._steam_user.clear()
        self._steam_user.addItem(t("steam.user_default"), "")
        for profile in list_steam_users(steam_roots()):
            self._steam_user.addItem(profile.label, profile.steam_id3)
        if current is not None:
            idx = self._steam_user.findData(current)
            if idx >= 0:
                self._steam_user.setCurrentIndex(idx)

    _MODE_KEYS: tuple[tuple[str, str], ...] = (
        ("reshade", "mode.reshade"),
        ("optiscaler", "mode.optiscaler"),
        ("vkbasalt", "mode.vkbasalt"),
        ("goverlay", "mode.goverlay"),
        ("display_profile", "mode.display_profile"),
        ("preview", "mode.preview"),
        ("rtx_remix_enable", "mode.rtx_remix_enable"),
        ("rtx_remix_disable", "mode.rtx_remix_disable"),
        ("dwm_hdr", "mode.dwm_hdr"),
    )

    def _reload_mode_combo(self) -> None:
        current = self._mode_combo.currentData() if self._mode_combo.count() else "reshade"
        self._mode_combo.clear()
        for mode, key in self._MODE_KEYS:
            self._mode_combo.addItem(t(key), mode)
        if current is not None:
            idx = self._mode_combo.findData(current)
            if idx >= 0:
                self._mode_combo.setCurrentIndex(idx)

    @staticmethod
    def _selection_key(target: EnhancementTarget | None) -> tuple[str, str, str] | None:
        from buusdo.core.selection import selection_key

        return selection_key(target)

    def _restore_selection(self, key: tuple[str, str, str] | None) -> None:
        if key is None:
            return
        for i, game in enumerate(self._filtered):
            if self._selection_key(game) == key:
                self._game_list.setCurrentRow(i)
                return

    def _set_scan_chrome_enabled(self, enabled: bool) -> None:
        """Language/theme toggles must not re-enter paint while a scan is live."""
        self._theme_btn.setEnabled(enabled)
        if hasattr(self, "_lang_btn"):
            self._lang_btn.setEnabled(enabled)
        if hasattr(self, "_lang") and self._lang is not None:
            self._lang.setEnabled(enabled)

    def _scan_ui_idle(self) -> None:
        self._scan_accepting = False
        self._progress.setValue(0)
        self._progress.setVisible(False)
        self._btn_scan.setEnabled(True)
        self._btn_force.setEnabled(True)
        self._btn_cancel.setEnabled(False)
        self._set_scan_chrome_enabled(True)

    def _scan_games(self, *, force: bool) -> None:
        # Drop any in-flight scan UI updates before starting another.
        self._scan_generation += 1
        self._scan_accepting = True
        self._set_scan_chrome_enabled(False)
        self._progress.setRange(0, 100)
        self._progress.setFormat("%p%")
        self._progress.setVisible(True)
        self._progress.setValue(0)
        self._status.setText(t("scan.progress"))
        self._btn_scan.setEnabled(False)
        self._btn_force.setEnabled(False)
        self._btn_cancel.setEnabled(True)

        # Surface pending resume before worker starts
        resume = resume_scan_status()
        if resume.get("resume"):
            scanned = int(resume.get("scanned", 0) or 0)
            total = max(1, int(resume.get("total_manifests", 0) or 1))
            self._progress.setValue(int(100 * scanned / total))
            self._status.setText(
                t(
                    "scan.resume",
                    scanned=scanned,
                    total=total,
                    match=resume.get("fingerprint_match"),
                )
            )

        gen = self._scan_generation
        self._scan_thread, self._scan_worker = start_scan(force=force, receiver=self)
        # Stash generation on worker for stale-signal ignore (object may outlive gen).
        self._scan_worker.setProperty("scanGeneration", gen)

    @Slot(str, float)
    def on_scan_progress(self, stage: str, value: float) -> None:
        assert_gui_thread("on_scan_progress")
        if not self._scan_accepting:
            return
        worker = self._scan_worker
        if worker is not None:
            gen = worker.property("scanGeneration")
            if gen is not None and int(gen) != self._scan_generation:
                return
        pct = int(max(0, min(100, value * 100)))
        self._progress.setValue(pct)
        if isinstance(stage, str) and stage.startswith("resume:"):
            st = resume_scan_status()
            scanned = int(st.get("scanned", 0) or 0)
            total = max(1, int(st.get("total_manifests", 0) or 1))
            resume_pct = int(100 * scanned / total)
            self._progress.setValue(max(pct, min(99, resume_pct)))
            self._status.setText(
                t(
                    "scan.resume",
                    scanned=scanned,
                    total=total,
                    match=st.get("fingerprint_match"),
                )
            )

    @Slot(list)
    def on_scan_finished(self, games: list) -> None:
        assert_gui_thread("on_scan_finished")
        if not self._scan_accepting:
            return
        prev = self._selection_key(self._target)
        try:
            restored: list[EnhancementTarget] = []
            for item in games or []:
                if isinstance(item, EnhancementTarget):
                    restored.append(item)
                elif isinstance(item, dict):
                    restored.append(EnhancementTarget.from_payload(item))
            self._games = restored
            self._refresh_game_list()
            self._restore_selection(prev)
            self._reload_steam_users()
            if self._target is None:
                self._status.setText(t("scan.games_count", count=len(self._games)))
            self._rebuild_tray_recent()
        except Exception as exc:  # noqa: BLE001
            capture_exception(exc, context={"op": "scan_finished", "payload_len": len(games or [])})
            self._status.setText(str(exc))
        finally:
            self._scan_ui_idle()

    @Slot(str)
    def on_scan_failed(self, message: str) -> None:
        assert_gui_thread("on_scan_failed")
        # Cancel already flipped accepting=False and restored buttons; ignore
        # late non-cancel failures, but always idle-out a live scan.
        if not self._scan_accepting:
            return
        try:
            if message and message != "cancelled":
                self._status.setText(message)
                capture_exception(RuntimeError(message), context={"op": "scan"})
        finally:
            self._scan_ui_idle()

    def _cancel_scan(self) -> None:
        # Stop accepting progress *before* asking the worker to stop — queued
        # progress events must not call setValue after we hide the bar.
        self._scan_accepting = False
        self._scan_generation += 1
        if self._scan_worker is not None:
            self._scan_worker.cancel()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFormat("%p%")
        self._progress.setVisible(False)
        self._btn_scan.setEnabled(True)
        self._btn_force.setEnabled(True)
        self._btn_cancel.setEnabled(False)
        self._set_scan_chrome_enabled(True)
        resume = resume_scan_status()
        if resume.get("partial") or resume.get("resume"):
            self._status.setText(
                t(
                    "scan.cancel_resume",
                    scanned=int(resume.get("scanned") or 0),
                    total=int(resume.get("total_manifests") or 0),
                )
            )
        else:
            self._status.setText(t("action.cancel_scan"))

    def _open_steam_for_target(self) -> None:
        if not self._target:
            return
        st = self._backend.status(self._target)
        health = st.get("proton_health") or {}
        uri = health.get("steam_uri") or (
            f"steam://run/{self._target.metadata['app_id']}"
            if self._target.metadata.get("app_id")
            else None
        )
        if not uri:
            QMessageBox.information(self, PRODUCT_NAME, t("proton.missing_prefix"))
            return
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        QDesktopServices.openUrl(QUrl(uri))
        if not health.get("ok", True):
            QMessageBox.information(self, PRODUCT_NAME, t("proton.missing_prefix"))

    def _write_proton_note(self) -> None:
        if not self._target or not self._target.metadata.get("app_id"):
            QMessageBox.information(self, PRODUCT_NAME, t("proton.missing_prefix"))
            return
        steam_id3 = self._steam_user.currentData() or self._target.metadata.get("steam_id3")
        localconfig = find_localconfig(steam_roots(), steam_id3=steam_id3 or None)
        if localconfig is None:
            QMessageBox.warning(self, PRODUCT_NAME, t("proton.missing_prefix"))
            return
        try:
            with Transaction() as tx:
                write_proton_launch_note(
                    tx,
                    localconfig,
                    str(self._target.metadata["app_id"]),
                    note=t("proton.note_text"),
                )
        except BuusdoError as exc:
            QMessageBox.warning(self, PRODUCT_NAME, str(exc))
            return
        self._status.setText(t("proton.note_written"))
        QMessageBox.information(self, PRODUCT_NAME, t("proton.note_written"))
        app_id = str(self._target.metadata["app_id"])
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        def _open(uri: str) -> bool:
            return bool(QDesktopServices.openUrl(QUrl(uri)))

        probe_open_uris(game_properties_uri_candidates(app_id), opener=_open)
        self._refresh_steam_uri_controls()

    def _refresh_game_list(self) -> None:
        needle = self._filter.text().strip().lower()
        self._game_list.clear()
        self._filtered = []
        for game in self._games:
            if needle and needle not in game.name.lower():
                continue
            st = self._backend.status(game)
            kind, badge = self._badge_for_status(st)
            runtime = " [Proton]" if game.metadata.get("runtime") == "proton" else ""
            health = st.get("proton_health") or {}
            warn = ""
            if health and not health.get("ok", True):
                warn = " ⚠"
            item = QListWidgetItem(f"{badge}{warn} {game.name}{runtime}")
            tip = str(game.install_path)
            if health and not health.get("ok", True):
                tip += f"\n{health.get('message')}"
            item.setToolTip(tip)
            item.setForeground(badge_color(kind if not warn else "warn"))
            self._game_list.addItem(item)
            self._filtered.append(game)

    def _badge_for_status(self, st: dict) -> tuple[str, str]:
        if st.get("installed") or (st.get("reshade") or {}).get("installed"):
            return "ok", t("badge.deployed")
        if st.get("vkbasalt_configured"):
            return "warn", "[vkBasalt]"
        return "muted", t("badge.none")

    def _on_game_selected(self, row: int) -> None:
        if row < 0 or row >= len(self._filtered):
            self._target = None
            self._exe_combo.clear()
            self._refresh_capabilities()
            return
        self._target = self._filtered[row]
        self._steam_uri_try_index = 0
        self._refresh_capabilities()
        self._populate_exe_combo()
        self._refresh_steam_uri_controls()
        st = self._backend.status(self._target)
        _, badge = self._badge_for_status(st)
        msg = f"{self._target.name} — {badge}\n{self._target.install_path}"
        health = st.get("proton_health")
        if health and not health.get("ok", True):
            msg += f"\n{health.get('message')}"
        self._status.setText(msg)

    def _populate_exe_combo(self) -> None:
        self._exe_combo.clear()
        if not self._target:
            return
        exes = self._target.metadata.get("executables") or []
        if not exes and self._target.executable:
            exes = [str(self._target.executable)]
        for path in exes:
            self._exe_combo.addItem(Path(path).name, path)
        if self._target.executable:
            idx = self._exe_combo.findData(str(self._target.executable))
            if idx >= 0:
                self._exe_combo.setCurrentIndex(idx)

    def _refresh_capabilities(self) -> None:
        self._cap_list.clear()
        if self._target:
            for cap in self._backend.list_capabilities(self._target):
                avail = "Y" if cap.available else "N"
                self._cap_list.addItem(f"[{avail}] {cap.title} — {cap.description}")
        # Host honesty rows (C4) — informational only, never marketed as boosts.
        from buusdo.core.hardware_notes import honesty_capabilities

        for cap in honesty_capabilities(t=t):
            self._cap_list.addItem(f"[i] {cap.title} — {cap.description}")

    def _format_history_action(self, action: str) -> str:
        raw = str(action or "")
        head, _, rest = raw.partition(":")
        if head == "install":
            label = t("history.action.install")
            return f"{label}:{rest}" if rest else label
        if head == "uninstall":
            return t("history.action.uninstall")
        return raw

    def _format_history_message(self, event: dict) -> str:
        key = str(event.get("message_key") or "")
        if key:
            params = event.get("message_params") or {}
            if isinstance(params, dict):
                return t(key, **params)
            return t(key)
        return str(event.get("message") or "")

    def _refresh_history(self) -> None:
        self._history_list.clear()
        for event in list_events(limit=50):
            status = t("history.ok") if event.get("success") else t("history.fail")
            line = t(
                "history.line",
                ts=event.get("ts", ""),
                status=status,
                action=self._format_history_action(str(event.get("action") or "")),
                target=event.get("target") or "",
            )
            msg = self._format_history_message(event)
            if msg:
                line = f"{line} — {msg}"
            self._history_list.addItem(line)

    def _pick_reshade_kit(self) -> bool:
        path = QFileDialog.getExistingDirectory(self, "ReShade")
        if not path:
            return False
        set_reshade_kit_path(path)
        self._status.setText(path)
        if self._kits_both_valid():
            data = load_settings()
            data["wizard_skipped_kits"] = False
            save_settings(data)
        self._refresh_kits_banner()
        return True

    def _pick_optiscaler_kit(self) -> bool:
        path = QFileDialog.getExistingDirectory(self, "OptiScaler")
        if not path:
            return False
        set_optiscaler_kit_path(path)
        self._status.setText(path)
        if self._kits_both_valid():
            data = load_settings()
            data["wizard_skipped_kits"] = False
            save_settings(data)
        self._refresh_kits_banner()
        return True

    def _install_options(self) -> dict:
        opts: dict = {"mode": self._mode_combo.currentData()}
        exe = self._exe_combo.currentData()
        if exe:
            opts["executable"] = exe
        api = self._api_combo.currentData()
        if api:
            opts["api"] = api
        steam_id3 = self._steam_user.currentData()
        if steam_id3:
            opts["steam_id3"] = steam_id3
            if self._target and self._target.metadata.get("app_id"):
                update_game_config(str(self._target.metadata["app_id"]), steam_id3=steam_id3)
        if opts["mode"] == "display_profile":
            opts["hdr_preferred"] = True
        if opts["mode"] == "preview":
            opts["preview_mode"] = "reshade"
            opts["triple_matrix"] = True
        if opts["mode"] == "vkbasalt":
            dlg = LinuxDeployDialog(
                self,
                preset=str(self._vk_preset.currentData() or "cas"),
            )
            if dlg.exec() != QDialog.DialogCode.Accepted:
                opts["_abort"] = True
                return opts
            opts.update(dlg.options())
            idx = self._vk_preset.findData(opts.get("vkbasalt_preset"))
            if idx >= 0:
                self._vk_preset.setCurrentIndex(idx)
        return opts

    def _show_about(self) -> None:
        show_about_dialog(self)

    def _show_companion(self) -> None:
        show_companion_dialog(
            self,
            host=self._companion_host,
            transport=self._companion_transport,
            pairing=self._companion_pairing,
        )
        self._refresh_companion_chip()

    def _refresh_companion_chip(self) -> None:
        from buusdo.companion.netinfo import companion_bind_addr, truncate_bind_addr

        transport = self._companion_transport
        running = bool(getattr(transport, "running", False))
        port = int(getattr(transport, "port", 0) or 0)
        addr = companion_bind_addr(
            loopback_only=bool(getattr(transport, "loopback_only", False)),
            port=port,
        )
        short = truncate_bind_addr(addr)
        if running:
            self._companion_chip.setText(t("companion.chip_bind", addr=short))
        else:
            self._companion_chip.setText(t("companion.chip_on"))
        self._companion_chip.setVisible(running)
        err = str(getattr(transport, "last_error", "") or "")
        open_hint = t("companion.chip_open")
        if err:
            tip = t("companion.chip_error", error=err)
            if running:
                tip = f"{t('companion.chip_bind', addr=addr)}\n{tip}\n{open_hint}"
            self._companion_chip.setToolTip(tip)
        elif running:
            self._companion_chip.setToolTip(f"{t('companion.chip_bind', addr=addr)}\n{open_hint}")
        else:
            self._companion_chip.setToolTip(open_hint)

    def _companion_request_scan(self) -> str:
        """Allowlisted companion op: queue the same desktop library scan."""
        if self._scan_accepting:
            return "scan already running"
        self._scan_games(force=False)
        return "scan queued"

    def closeEvent(self, event) -> None:  # noqa: N802
        try:
            self._companion_transport.stop()
        except Exception:
            pass
        super().closeEvent(event)

    def _severity_rank(self, severity: str) -> int:
        order = {"block": 0, "warning": 1, "info": 2, "conflict": 3, "": 4}
        return order.get(severity, 5)

    @staticmethod
    def _esc_clears_selection_not_reject(dlg: QDialog, *widgets) -> None:
        """Esc clears row selection; does not close the dialog (override reject)."""

        def _clear() -> None:
            clear_row_selections(*widgets)

        def _reject_clear() -> None:
            _clear()

        dlg.reject = _reject_clear  # type: ignore[method-assign]
        for w in widgets:
            if w is not None:
                QShortcut(QKeySequence(Qt.Key.Key_Escape), w, activated=_clear)

    def _show_conflict_dialog(self, details: dict) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle(t("conflict.title"))
        dlg.setObjectName("instrumentDialog")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        title = QLabel(t("conflict.title"))
        title.setObjectName("sectionLabel")
        layout.addWidget(title)
        schema_v = details.get("schema_version") or 1
        badge = QLabel(t("conflict.schema_badge", version=schema_v))
        badge.setObjectName("backendChip")
        layout.addWidget(badge)
        rows = []
        for item in details.get("diffs") or []:
            detail = str(item.get("detail") or "")
            severity = ""
            if item.get("action") == "conflict":
                if detail.startswith("[block]"):
                    severity = "block"
                elif detail.startswith("[warning]"):
                    severity = "warning"
                elif detail.startswith("[info]"):
                    severity = "info"
                else:
                    severity = "conflict"
            rows.append((severity, item, detail))
        rows.sort(key=lambda r: self._severity_rank(r[0]))
        table = QTableWidget(len(rows), 4)
        table.setHorizontalHeaderLabels(
            [
                t("conflict.col.severity"),
                t("conflict.col.action"),
                t("conflict.col.path"),
                t("conflict.col.detail"),
            ]
        )
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        colors = {
            "block": QColor("#C73E1D"),
            "warning": QColor("#FF4F00"),
            "info": QColor("#1F6F8B"),
        }
        for i, (severity, item, detail) in enumerate(rows):
            values = [
                severity,
                str(item.get("action") or ""),
                str(item.get("path") or ""),
                detail,
            ]
            color = colors.get(severity)
            for col, text in enumerate(values):
                cell = QTableWidgetItem(text)
                if color is not None:
                    cell.setForeground(color)
                table.setItem(i, col, cell)
        table.resizeColumnsToContents()
        layout.addWidget(table)
        layout.addWidget(QLabel(t("ui.clear_selection_tip")))
        payload = migrate_conflict_export(
            {
                "schema_version": details.get("schema_version", 1),
                "mode": details.get("mode"),
                "blocked": details.get("blocked"),
                "triple_matrix_summary": details.get("triple_matrix_summary"),
                "diffs": details.get("diffs") or [],
            }
        )
        actions = QHBoxLayout()
        copy_btn = QPushButton(t("action.copy_json"))
        export_btn = QPushButton(t("action.export_json"))
        clear_sel = QPushButton(t("action.clear_selection"))
        close = QPushButton("OK")

        def _copy() -> None:
            from PySide6.QtWidgets import QApplication
            import json as _json

            QApplication.clipboard().setText(_json.dumps(payload, indent=2, ensure_ascii=False))

        def _export() -> None:
            import json as _json

            path, _ = QFileDialog.getSaveFileName(
                dlg, t("action.export_json"), "conflict-preview.json", "JSON (*.json)"
            )
            if path:
                Path(path).write_text(
                    _json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                )

        def _clear_conflict_selection() -> None:
            clear_row_selections(table)

        copy_btn.clicked.connect(_copy)
        export_btn.clicked.connect(_export)
        clear_sel.clicked.connect(_clear_conflict_selection)
        close.setObjectName("primaryAction")
        close.setDefault(True)
        close.clicked.connect(dlg.accept)
        self._esc_clears_selection_not_reject(dlg, table)
        table.setToolTip(t("ui.clear_selection_tip"))
        clear_sel.setToolTip(t("ui.clear_selection_tip"))
        actions.addWidget(copy_btn)
        actions.addWidget(export_btn)
        actions.addWidget(clear_sel)
        actions.addWidget(close)
        layout.addLayout(actions)
        dlg.resize(720, 420)
        dlg.exec()

    def _on_crash_opt_toggled(self, enabled: bool) -> None:
        if not enabled:
            set_crash_upload_opt_in(False)
            return
        sample = redact(f"boom at {Path.home()}/secret token=sekrit")
        preview = QMessageBox(self)
        preview.setWindowTitle(t("action.crash_opt_preview"))
        preview.setText(t("action.crash_opt_confirm"))
        preview.setInformativeText(sample)
        preview.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        preview.setDefaultButton(QMessageBox.StandardButton.No)
        if preview.exec() != QMessageBox.StandardButton.Yes:
            self._crash_opt.blockSignals(True)
            self._crash_opt.setChecked(False)
            self._crash_opt.blockSignals(False)
            return
        set_crash_upload_opt_in(True)

    def _refresh_session_banner(self) -> None:
        st = display_session_status()
        if not st.get("present"):
            self._session_banner.setText("")
            self._btn_clear_session.setEnabled(False)
            self._btn_rollback_now.setEnabled(False)
            return
        self._btn_clear_session.setEnabled(True)
        self._btn_rollback_now.setEnabled(True)
        mins = max(1, int((st.get("ttl_remaining_s") or 0) / 60))
        self._session_banner.setText(
            t(
                "display.session_warn",
                minutes=mins,
                displays=int(st.get("displays") or 0),
                targets=int(st.get("targets") or 0),
            )
        )

    def _clear_display_session(self) -> None:
        clear_display_session()
        self._refresh_session_banner()
        self._status.setText(t("action.clear_display_session"))

    def _rollback_display_now(self) -> None:
        result = rollback_display_session(dry_run=False)
        self._refresh_session_banner()
        if result.get("restored"):
            self._status.setText(t("display.rollback_ok"))
            if hasattr(self, "_tray"):
                self._tray.showMessage(PRODUCT_NAME, t("display.rollback_ok"))
            self._refresh_capabilities()
            self._refresh_game_list()
            return
        failed = result.get("failed_displays") or []
        succeeded = result.get("succeeded_displays") or []
        if failed:
            if succeeded or result.get("partial"):
                msg = t(
                    "display.rollback_partial",
                    ok=len(succeeded),
                    fail=len(failed),
                )
                self._status.setText(msg)
                if hasattr(self, "_tray"):
                    self._tray.showMessage(PRODUCT_NAME, msg)
                self._refresh_capabilities()
            self._show_rollback_failures(failed, hdr_step=result.get("details", {}).get("hdr"))
        else:
            self._status.setText(str(result.get("reason") or "no_session"))

    def _show_rollback_failures(self, failed: list, *, hdr_step: dict | None = None) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle(t("display.fail_table"))
        dlg.setObjectName("instrumentDialog")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        fail_title = QLabel(t("display.fail_table"))
        fail_title.setObjectName("sectionLabel")
        layout.addWidget(fail_title)
        table = QTableWidget(len(failed), 7)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        table.setHorizontalHeaderLabels(
            ["device", "name", "code", "size", "refresh", "adapter", "targetId"]
        )
        for i, row in enumerate(failed):
            table.setItem(i, 0, QTableWidgetItem(str(row.get("device") or "")))
            table.setItem(i, 1, QTableWidgetItem(str(row.get("device_string") or "")))
            table.setItem(i, 2, QTableWidgetItem(str(row.get("code") if row.get("code") is not None else row.get("error") or "")))
            table.setItem(
                i,
                3,
                QTableWidgetItem(f"{row.get('width')}x{row.get('height')}"),
            )
            table.setItem(i, 4, QTableWidgetItem(str(row.get("refresh_hz") or "")))
            adapter = ""
            if row.get("adapterLow") is not None:
                adapter = f"{row.get('adapterLow')}/{row.get('adapterHigh') or 0}"
            table.setItem(i, 5, QTableWidgetItem(adapter))
            table.setItem(i, 6, QTableWidgetItem(str(row.get("targetId") if row.get("targetId") is not None else "")))
        table.resizeColumnsToContents()
        layout.addWidget(table)
        remaining = QLabel("")
        remaining.setWordWrap(True)
        remaining_list = QListWidget()
        remaining_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        remaining_list.setAccessibleName(t("display.session_targets_list"))

        def _sync_remaining_targets() -> None:
            st = display_session_status()
            remaining_list.clear()
            if not st.get("present"):
                remaining.setText(t("display.session_targets_cleared"))
                return
            remaining.setText(
                t(
                    "display.session_targets_left",
                    targets=int(st.get("targets") or 0),
                    displays=int(st.get("displays") or 0),
                )
            )
            for tgt in st.get("target_rows") or []:
                low = tgt.get("adapterLow")
                high = tgt.get("adapterHigh") if tgt.get("adapterHigh") is not None else 0
                tid = tgt.get("targetId")
                if tid is None and tgt.get("id") is not None:
                    tid = tgt.get("id")
                label = f"adapter={low}/{high} targetId={tid}"
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, {
                    "adapterLow": low,
                    "adapterHigh": high,
                    "targetId": tid,
                })
                remaining_list.addItem(item)

        _sync_remaining_targets()
        layout.addWidget(remaining)
        layout.addWidget(QLabel(t("display.session_targets_list")))
        layout.addWidget(remaining_list)
        layout.addWidget(QLabel(t("display.retry_hdr_shortcut")))
        retry = QPushButton(t("display.retry_one"))
        retry_hdr = QPushButton(t("display.retry_hdr"))
        retry_hdr_sel = QPushButton(t("display.retry_hdr_selected"))
        retry_hdr_sel.setObjectName("accentAction")
        retry_hdr_sel.setToolTip(t("display.retry_hdr_shortcut"))
        remaining_list.setToolTip(t("display.retry_hdr_shortcut"))

        def _retry() -> None:
            r = table.currentRow()
            if r < 0 or r >= len(failed):
                return
            row = failed[r]
            out = retry_display_mode(
                device=row.get("device"),
                width=int(row.get("width") or 0),
                height=int(row.get("height") or 0),
                refresh_hz=row.get("refresh_hz"),
                dry_run=False,
            )
            if out.get("ok"):
                QMessageBox.information(self, PRODUCT_NAME, t("display.rollback_ok"))
                table.removeRow(r)
                failed.pop(r)
            else:
                QMessageBox.warning(
                    self,
                    PRODUCT_NAME,
                    t(
                        "display.rollback_failed",
                        devices=str(row.get("device_string") or row.get("device")),
                    ),
                )

        def _hdr_enable_for(row: dict | None) -> bool:
            enable = bool((row or {}).get("hdr_enable"))
            if hdr_step and hdr_step.get("enable") is not None:
                enable = bool(hdr_step.get("enable"))
            return enable

        def _apply_hdr_retry(
            *,
            adapter_low: int,
            adapter_high: int,
            target_id: int,
            enable: bool,
            row: dict | None,
            row_index: int,
        ) -> None:
            out = retry_hdr_target(
                adapter_low=int(adapter_low),
                adapter_high=int(adapter_high or 0),
                target_id=int(target_id),
                enable=enable,
                dry_run=False,
            )
            if out.get("ok"):
                QMessageBox.information(self, PRODUCT_NAME, t("display.rollback_ok"))
                drop_session_ccd_target(
                    adapter_low=int(adapter_low),
                    adapter_high=int(adapter_high or 0),
                    target_id=int(target_id),
                )
                self._refresh_session_banner()
                _sync_remaining_targets()
                if row is not None and 0 <= row_index < len(failed):
                    if (
                        row.get("targetId") is not None
                        and int(row.get("targetId")) == int(target_id)
                    ) or (
                        row.get("adapterLow") is not None
                        and int(row.get("adapterLow")) == int(adapter_low)
                    ):
                        table.removeRow(row_index)
                        failed.pop(row_index)
            else:
                QMessageBox.warning(
                    self,
                    PRODUCT_NAME,
                    t("display.rollback_failed", devices=f"HDR target {target_id}"),
                )

        def _retry_hdr() -> None:
            r = table.currentRow()
            row = failed[r] if 0 <= r < len(failed) else None
            enable = _hdr_enable_for(row)
            adapter_low = (row or {}).get("adapterLow")
            adapter_high = (row or {}).get("adapterHigh") or 0
            target_id = (row or {}).get("targetId")
            if target_id is None or adapter_low is None:
                targets = list((hdr_step or {}).get("targets") or [])
                bad = next((tg for tg in targets if not tg.get("ok")), None)
                if not bad:
                    QMessageBox.information(self, PRODUCT_NAME, t("display.retry_hdr_need_id"))
                    return
                adapter_low = bad.get("adapterLow")
                adapter_high = bad.get("adapterHigh") or 0
                target_id = bad.get("id") if bad.get("id") is not None else bad.get("targetId")
            _apply_hdr_retry(
                adapter_low=int(adapter_low),
                adapter_high=int(adapter_high or 0),
                target_id=int(target_id),
                enable=enable,
                row=row,
                row_index=r,
            )

        def _retry_hdr_selected() -> None:
            item = remaining_list.currentItem()
            if item is None:
                QMessageBox.information(self, PRODUCT_NAME, t("display.retry_hdr_need_id"))
                return
            data = item.data(Qt.ItemDataRole.UserRole) or {}
            if data.get("adapterLow") is None or data.get("targetId") is None:
                QMessageBox.information(self, PRODUCT_NAME, t("display.retry_hdr_need_id"))
                return
            # Prefer matching fail-table row when present.
            match_i = -1
            match_row = None
            for i, row in enumerate(failed):
                if (
                    row.get("targetId") is not None
                    and int(row.get("targetId")) == int(data["targetId"])
                    and row.get("adapterLow") is not None
                    and int(row.get("adapterLow")) == int(data["adapterLow"])
                ):
                    match_i = i
                    match_row = row
                    break
            _apply_hdr_retry(
                adapter_low=int(data["adapterLow"]),
                adapter_high=int(data.get("adapterHigh") or 0),
                target_id=int(data["targetId"]),
                enable=_hdr_enable_for(match_row),
                row=match_row,
                row_index=match_i,
            )

        def _clear_hdr_selection() -> None:
            clear_row_selections(remaining_list, table)

        retry.clicked.connect(_retry)
        retry_hdr.clicked.connect(_retry_hdr)
        retry_hdr_sel.clicked.connect(_retry_hdr_selected)
        remaining_list.itemDoubleClicked.connect(lambda _item: _retry_hdr_selected())
        # Keyboard: Return / Ctrl+Return retries; Esc clears multi-select on list + fail table.
        QShortcut(QKeySequence(Qt.Key.Key_Return), remaining_list, activated=_retry_hdr_selected)
        QShortcut(QKeySequence(Qt.Key.Key_Enter), remaining_list, activated=_retry_hdr_selected)
        QShortcut(QKeySequence("Ctrl+Return"), remaining_list, activated=_retry_hdr_selected)
        self._esc_clears_selection_not_reject(dlg, remaining_list, table)
        clear_sel = QPushButton(t("action.clear_selection"))
        clear_sel.setToolTip(t("ui.clear_selection_tip"))
        clear_sel.clicked.connect(_clear_hdr_selection)
        table.setToolTip(t("ui.clear_selection_tip"))
        close = QPushButton("OK")
        close.setObjectName("primaryAction")
        close.setDefault(True)
        close.clicked.connect(dlg.accept)
        row = QHBoxLayout()
        row.addWidget(retry)
        row.addWidget(retry_hdr)
        row.addWidget(retry_hdr_sel)
        row.addWidget(clear_sel)
        row.addWidget(close)
        layout.addLayout(row)
        dlg.resize(720, 420)
        dlg.exec()

    def _export_crash_audit(self) -> None:
        data = load_settings()
        last_dir = str(data.get("crash_audit_export_dir") or "")
        suggested = str(Path(last_dir) / "buusdo-crash-audit.jsonl") if last_dir else "buusdo-crash-audit.jsonl"
        while True:
            path, _ = QFileDialog.getSaveFileName(
                self, t("action.export_audit"), suggested, "JSONL (*.jsonl)"
            )
            if not path:
                return
            try:
                export_crash_opt_in_audit(Path(path))
                settings = load_settings()
                settings["crash_audit_export_dir"] = str(Path(path).expanduser().parent)
                save_settings(settings)
                self._status.setText(t("action.export_audit"))
                return
            except OSError as exc:
                box = QMessageBox(self)
                box.setIcon(QMessageBox.Icon.Warning)
                box.setWindowTitle(PRODUCT_NAME)
                box.setText(t("action.export_audit_failed", error=str(exc)))
                retry = box.addButton(
                    t("action.export_audit_retry"), QMessageBox.ButtonRole.AcceptRole
                )
                box.addButton(QMessageBox.StandardButton.Cancel)
                box.exec()
                if box.clickedButton() is not retry:
                    return
                # Remember the failed directory so the next dialog opens there.
                failed_dir = str(Path(path).expanduser().parent)
                settings = load_settings()
                settings["crash_audit_export_dir"] = failed_dir
                save_settings(settings)
                suggested = str(Path(failed_dir) / Path(path).name)

    def _clear_crash_audit(self) -> None:
        clear_crash_opt_in_audit()
        self._status.setText(t("action.clear_audit"))

    def _on_preview(self) -> None:
        if not self._target:
            QMessageBox.information(self, PRODUCT_NAME, "Select a game first.")
            return
        mode = self._mode_combo.currentData()
        try:
            r_kit = get_reshade_kit_path()
            o_kit = get_optiscaler_kit_path()
            api_raw = self._api_combo.currentData()
            api = GraphicsApi(api_raw) if api_raw else None
            if mode == "optiscaler":
                if not o_kit:
                    raise BuusdoError(t("err.optiscaler_kit"))
                details = preview_optiscaler_deploy(self._target, Path(o_kit))
            else:
                details = preview_triple_matrix(
                    self._target,
                    reshade_kit=Path(r_kit) if r_kit else None,
                    optiscaler_kit=Path(o_kit) if o_kit else None,
                    api=api,
                )
        except BuusdoError as exc:
            QMessageBox.warning(self, PRODUCT_NAME, str(exc))
            return
        self._show_conflict_dialog(details)

    def _show_blocked(self, error: UnsafeTargetError) -> None:
        page = BlockedPage(error)
        while self._stack.count() > 1:
            w = self._stack.widget(1)
            self._stack.removeWidget(w)
            w.deleteLater()
        self._stack.addWidget(page)
        self._stack.setCurrentWidget(page)

    def _on_install(self) -> None:
        if not self._target:
            QMessageBox.information(self, PRODUCT_NAME, "Select a game first.")
            return
        opts = self._install_options()
        if opts.pop("_abort", False):
            return
        try:
            result = self._backend.install(self._target, opts)
        except UnsafeTargetError as exc:
            self._show_blocked(exc)
            self._refresh_history()
            return
        except BuusdoError as exc:
            capture_exception(exc, context={"op": "install", "target": self._target.name})
            QMessageBox.warning(self, PRODUCT_NAME, str(exc))
            self._refresh_history()
            return
        if self._mode_combo.currentData() == "preview":
            self._show_conflict_dialog(result.details)
        self._status.setText(result.message)
        self._stack.setCurrentWidget(self._home)
        self._refresh_game_list()
        self._refresh_history()
        self._rebuild_tray_recent()
        self._refresh_session_banner()

    def _on_uninstall(self) -> None:
        if not self._target:
            return
        try:
            result = self._backend.uninstall(self._target)
        except UnsafeTargetError as exc:
            self._show_blocked(exc)
            return
        except BuusdoError as exc:
            QMessageBox.warning(self, PRODUCT_NAME, str(exc))
            return
        self._status.setText(result.message)
        self._refresh_game_list()
        self._refresh_history()

    def _on_export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, t("dialog.export_title"), "buusdo-config.zip", "Zip (*.zip)"
        )
        if path:
            export_configs(path)

    def _on_import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, t("dialog.import_title"), "", "Zip (*.zip)"
        )
        if path:
            import_configs(path)
