#!/usr/bin/env python3
"""Generate docs/user-guide/*.md for every UI locale (run from repo root)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "user-guide"
LOCALES = ROOT / "buusdo" / "locales"

# Display names for known locale stems (native, english). New stems need an entry
# here (or they fall back to the raw code) when discovered under buusdo/locales/.
LOCALE_NAMES: dict[str, tuple[str, str]] = {
    "en": ("English", "English"),
    "zh": ("简体中文", "Simplified Chinese"),
    "zh-Hant": ("繁體中文", "Traditional Chinese"),
    "ja": ("日本語", "Japanese"),
    "ko": ("한국어", "Korean"),
    "pt-BR": ("Português (Brasil)", "Portuguese (Brazil)"),
    "pt": ("Português", "Portuguese"),
    "es": ("Español", "Spanish"),
    "de": ("Deutsch", "German"),
    "fr": ("Français", "French"),
    "it": ("Italiano", "Italian"),
    "ru": ("Русский", "Russian"),
}

RELEASE = "https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0"
REPO = "https://github.com/otas0/buusdo-Graphics-Enhancement-Tool"


def discover_langs() -> list[tuple[str, str, str]]:
    """UI locale stems from buusdo/locales/*.json → (code, native, english)."""
    if not LOCALES.is_dir():
        raise SystemExit(f"missing locales dir: {LOCALES}")
    langs: list[tuple[str, str, str]] = []
    for path in sorted(LOCALES.glob("*.json")):
        code = path.stem
        native, eng = LOCALE_NAMES.get(code, (code, code))
        langs.append((code, native, eng))
    if not langs:
        raise SystemExit(f"no locale JSON under {LOCALES}")
    return langs


def nav(current: str, langs: list[tuple[str, str, str]] | None = None) -> str:
    rows = langs if langs is not None else discover_langs()
    parts = []
    for code, native, _ in rows:
        if code == current:
            parts.append(f"**{native}**")
        else:
            parts.append(f"[{native}]({code}.md)")
    return " · ".join(parts)


def common_footer(code: str, langs: list[tuple[str, str, str]]) -> str:
    return f"""
---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*{nav(code, langs)}*
"""


# --- Per-language bodies (install + first-open babysitter steps) ---

BODIES: dict[str, str] = {}

BODIES["en"] = f"""# buusdo Graphics Enhancement Tool — user guide (English)

Languages: {nav("en")}

How to download and open **buusdo Graphics Enhancement Tool** on Windows, macOS, and Linux. Latest release: [v1.1.0]({RELEASE}).

## Who should use which path

| Audience | What to do |
|----------|------------|
| **Most users** | Download **Releases** packages (Windows Setup / macOS `.app` zip / Linux `install_linux.sh` or onedir). Follow the unblock / SmartScreen / Gatekeeper steps below. |
| **Developers / advanced** | Optional **from-source** path at the end of this guide (`git clone` → venv → `python -m buusdo`). That path is for **development**, not a supported way to “avoid” SmartScreen or Gatekeeper. |

Cloning the whole repository does **not** replace the recommended installers for normal use.

## What you are installing

**buusdo Graphics Enhancement Tool** is a desktop **scheduler / config coordinator** for existing graphics stacks (ReShade, OptiScaler, etc.). Kits are **BYO** (not bundled). Capabilities differ by OS — macOS is **config-only** (no injection).

## 1. Download the right file

1. Open [{RELEASE}]({RELEASE}) in a browser.
2. Scroll to **Assets**.
3. Pick the file for your OS (names may vary slightly):
   - **Windows:** installer / Setup `.exe` (Inno)
   - **macOS:** `.app` inside a `.zip`
   - **Linux:** onedir archive and/or wheel + `install_linux.sh`
4. Do **not** use only the source code zip unless you intend to build from source (see **From source** below).
5. Optional: verify checksums with the release `SHA256SUMS` file.

## 2. Windows — open the installer (unsigned)

v1.1.0 is **not** Authenticode-signed. SmartScreen is expected. You do **not** need Python for the Setup `.exe`.

### A. Unblock the file (do this first)

1. Open **File Explorer** (taskbar folder icon, or `Win + E`).
2. Open **Downloads**.
3. **Right-click** the Setup `.exe` → **Properties**.
4. On the **General** tab, at the bottom, if you see **Unblock**, **check** it.
5. Click **Apply**, then **OK**.

### B. SmartScreen: “Windows protected your PC”

1. Double-click the Setup `.exe`.
2. If you see **Windows protected your PC**:
   - Click **More info** (under the message text) if **Run anyway** is not visible yet.
   - Click **Run anyway**.
3. If **User Account Control** appears → click **Yes**.
4. Finish the wizard: Next → Next → Install → Finish.

### C. Open buusdo Graphics Enhancement Tool after install

1. Press **Win**, type `buusdo Graphics Enhancement Tool`, press **Enter**.
2. Or open `C:\\Program Files\\buusdo\\buusdo.exe` (or `Program Files (x86)`).

### D. If the file vanishes / “not found”

1. Open **Windows Security** (search that name in Start).
2. **Virus & threat protection** → **Protection history**.
3. Find buusdo / Setup → **Restore** or **Allow**.
4. Retry Unblock + Run anyway.

Edge/Chrome may also quarantine the download — open the download list (`Ctrl + J`) and choose **Keep** / **Keep anyway**.

## 3. macOS — open the .app (unsigned)

v1.1.0 is **not** notarized. Gatekeeper blocks are expected.

1. Download the macOS `.zip` from Assets; double-click to unzip.
2. Drag `Buusdo.app` to **Applications** (recommended).
3. In Finder, go to **Applications**.
4. **Right-click** (or Control-click) `Buusdo.app` → **Open**.
5. In the dialog, click **Open** again (first launch only while unsigned).
6. If you only double-clicked and saw **Move to Trash** / cannot be opened:
   - Use right-click → **Open** (do not only double-click the first time).
7. Optional System Settings path (macOS Ventura+):
   - **System Settings** → **Privacy & Security**
   - Scroll to the message about Buusdo → **Open Anyway** → confirm.

You do **not** need to disable SIP. macOS buusdo is config-only (C5).

## 4. Linux — install and run

### Option A — `install_linux.sh` (wheel next to the script)

```bash
cd /path/to/extracted-release   # folder that has install_linux.sh + buusdo-*.whl
bash install_linux.sh
# Ensure ~/.local/bin is on PATH, then:
buusdo
```

The script creates `~/.local/share/buusdo/venv` and a launcher at `~/.local/bin/buusdo`.

### Option B — manual wheel

```bash
python3 -m pip install ./buusdo-*-py3-none-any.whl
python3 -m pip install "PySide6-Essentials==6.12.0"
python3 -m buusdo
```

### Option C — onedir binary (if provided in the release)

Extract the archive and run the bundled executable from the extracted folder (see release notes for the exact binary name).

If the UI fails to start, install Qt/xcb deps for your distro (e.g. on Debian/Ubuntu: packages providing `libxcb-cursor0` / XCB libs as required by PySide6).

## 5. After first launch

1. In the UI, select your **ReShade** and/or **OptiScaler** kit folders (BYO).
2. Scan games / apply configs per the main window.
3. Anti-cheat blocks cannot be bypassed (“continue anyway” does not exist).
4. Language: use the language control in the UI (same codes as this guide).

## 6. From source (developers / advanced)

This is a **dev path** for contributing or debugging. It is **not** the recommended install for most users, and it is **not** documented as a way to bypass SmartScreen / Gatekeeper.

```bash
git clone https://github.com/otas0/buusdo.git
cd buusdo
# Prefer uv if you have it:
uv venv --python 3.12 .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
uv sync --extra devui
# Or: python -m pip install -e ".[devui]"
python -m buusdo
```

You still need BYO ReShade / OptiScaler kits in the UI. Building your own `.exe` / `.app` from source remains **unsigned** unless you sign it yourself.

## 7. Still stuck?

Note: (1) full dialog title/screenshot, (2) installer vs installed app, (3) OS version. Open an issue at {REPO}/issues.
"""

BODIES["zh"] = f"""# buusdo Graphics Enhancement Tool — 用户指南（简体中文）

语言: {nav("zh")}

如何在 Windows / macOS / Linux 上下载并打开 **buusdo**。最新版：[v1.1.0]({RELEASE})。

## 该走哪条路径

| 对象 | 怎么做 |
|------|--------|
| **普通用户** | 继续用 **Releases** 里的安装包（Windows Setup / macOS `.app` zip / Linux `install_linux.sh` 或 onedir），并按下文做解除锁定 / SmartScreen / Gatekeeper。 |
| **开发者 / 进阶** | 可用文末 **从源码运行**（`git clone` → venv → `python -m buusdo`）。这是 **开发路径**，不是为了绕过 SmartScreen / Gatekeeper，也不是普通用户推荐安装方式。 |

下载整个仓库 **不能** 代替上述安装包，作为日常安装方式。

## 你在安装什么

buusdo 是桌面端的图形增强 **调度 / 配置协调** 工具（ReShade、OptiScaler 等）。工具包 **自备（BYO）**，不随安装包捆绑。各系统能力不同 — **macOS 仅为配置**（无注入）。

## 1. 下载正确的文件

1. 浏览器打开 [{RELEASE}]({RELEASE})。
2. 滚到 **Assets**。
3. 按系统选择：
   - **Windows：** Setup / 安装包 `.exe`
   - **macOS：** zip 里的 `.app`
   - **Linux：** onedir 和/或 wheel + `install_linux.sh`
4. 不要只下 Source code，除非你要自己从源码跑（见下文 **从源码运行**）。
5. 可用发布页的 `SHA256SUMS` 校验。

## 2. Windows — 打开安装包（未签名）

v1.1.0 **没有** Authenticode 签名，出现 SmartScreen **正常**。跑 Setup **不需要** 安装 Python。

### A. 先解除锁定

1. 打开 **文件资源管理器**（任务栏文件夹，或 `Win + E`）。
2. 进入左侧 **下载**。
3. **右键** Setup 的 `.exe` → **属性**。
4. **常规** 底部若有 **解除锁定**，请 **勾选**。
5. 点 **应用**，再点 **确定**。

### B. SmartScreen：Windows 已保护你的电脑

1. **双击** Setup `.exe`。
2. 若出现 **Windows 已保护你的电脑**：
   - 若还没有「仍要运行」，先点说明下方的 **更多信息**。
   - 再点 **仍要运行**。
3. 若出现 **用户账户控制** → 点 **是**。
4. 按向导：**下一步 → 下一步 → 安装 → 完成**。

### C. 安装后打开

1. 按 **Win**，输入 `buusdo`，回车。
2. 或打开 `C:\\Program Files\\buusdo\\buusdo.exe`（或 `Program Files (x86)`）。

### D. 文件消失 / 提示找不到

1. 开始菜单搜索并打开 **Windows 安全中心**。
2. **病毒和威胁防护** → **防护历史记录**。
3. 找到 buusdo / Setup → **还原** 或 **允许**。
4. 再执行解除锁定 + 仍要运行。

Edge/Chrome：`Ctrl + J` 打开下载列表，选 **保留** / **仍要保留**。

## 3. macOS — 打开 .app（未公证）

v1.1.0 **未**公证，Gatekeeper 拦截 **正常**。

1. 下载 macOS `.zip`，双击解压。
2. 将 `Buusdo.app` 拖到 **应用程序**（建议）。
3. 打开 **访达** → **应用程序**。
4. **右键**（或 Control-单击）`Buusdo.app` → **打开**。
5. 对话框再点一次 **打开**（未签名时首次需要）。
6. 若只双击出现 **移到废纸篓** / 无法打开：必须用右键 → **打开**。
7. 可选（Ventura+）：**系统设置** → **隐私与安全性** → 滚到 Buusdo 提示 → **仍要打开**。

**不要**为了跑 buusdo 去关 SIP。macOS 版仅为配置（C5）。

## 4. Linux — 安装与运行

### 方式 A — `install_linux.sh`

```bash
cd /path/to/extracted-release
bash install_linux.sh
buusdo   # 确保 ~/.local/bin 在 PATH 中
```

脚本会创建 `~/.local/share/buusdo/venv` 与 `~/.local/bin/buusdo`。

### 方式 B — 手动 wheel

```bash
python3 -m pip install ./buusdo-*-py3-none-any.whl
python3 -m pip install "PySide6-Essentials==6.12.0"
python3 -m buusdo
```

### 方式 C — onedir（若发布提供）

解压后运行目录内可执行文件（以发布说明为准）。

若界面起不来，按发行版安装 PySide6 所需的 XCB/Qt 依赖。

## 5. 首次启动之后

1. 在界面中选择 **ReShade** / **OptiScaler** 工具包目录（自备）。
2. 按主窗口扫描游戏 / 应用配置。
3. 反作弊拦截 **无法**「仍然继续」。
4. 语言可在应用内切换（与本指南语言代码一致）。

## 6. 从源码运行（开发者 / 进阶）

这是 **开发路径**，用于贡献代码或调试。**不是**普通用户推荐安装方式，也 **不是** 用来绕过 SmartScreen / Gatekeeper 的官方办法。

```bash
git clone https://github.com/otas0/buusdo.git
cd buusdo
uv venv --python 3.12 .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
uv sync --extra devui
# 或: python -m pip install -e ".[devui]"
python -m buusdo
```

仍需在界面里自备 ReShade / OptiScaler 工具包。自行从源码打出的 `.exe` / `.app` 默认仍是 **未签名**。

## 7. 仍打不开？

请记录：(1) 完整弹窗标题/截图 (2) 是安装包还是已安装程序 (3) 系统版本。到 {REPO}/issues 提 Issue。
"""

BODIES["zh-Hant"] = f"""# buusdo 使用者指南（繁體中文）

語言: {nav("zh-Hant")}

如何在 Windows / macOS / Linux 下載並開啟 **buusdo**。最新版：[v1.1.0]({RELEASE})。

## 你在安裝什麼

buusdo 是桌面端的圖形增強 **排程 / 設定協調** 工具。工具包需 **自行準備（BYO）**。macOS **僅設定、無注入**。

## 1. 下載正確的檔案

1. 開啟 [{RELEASE}]({RELEASE})。
2. 捲到 **Assets**。
3. Windows 選 Setup `.exe`；macOS 選 zip 內 `.app`；Linux 選 onedir 與/或 wheel + `install_linux.sh`。
4. 不要只下 Source code（除非要自行編譯）。

## 2. Windows — 開啟安裝程式（未簽名）

不需安裝 Python。SmartScreen 警告為預期現象。

1. **檔案總管** → **下載** → 對 `.exe` **右鍵** → **內容** → 勾選 **解除封鎖** → **套用** → **確定**。
2. 雙擊安裝：若出現「Windows 已保護您的電腦」→ 先點 **詳細資訊**（若有）→ **仍要執行** → UAC 按 **是**。
3. 安裝後按 **Win** 輸入 `buusdo` 開啟。
4. 若檔案消失：開啟 **Windows 安全性** → **病毒與威脅防護** → **保護紀錄** → **還原**。

## 3. macOS — 開啟 .app（未公證）

1. 下載並解壓 zip，將 `Buusdo.app` 拖到 **應用程式**。
2. **右鍵**（或 Control-點按）→ **打開** → 再按一次 **打開**。
3. 勿只靠雙擊；也勿為了執行而關閉 SIP。
4. 可選：**系統設定** → **隱私權與安全性** → **仍要打開**。

## 4. Linux

```bash
bash install_linux.sh
buusdo
```

或：

```bash
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0"
python3 -m buusdo
```

## 5. 首次啟動後

在 UI 選擇 ReShade / OptiScaler 工具包目錄；反作弊阻擋無法略過。問題請開 {REPO}/issues。
"""

# Compact but complete translations for remaining UI languages
BODIES["ja"] = f"""# buusdo ユーザーガイド（日本語）

言語: {nav("ja")}

Windows / macOS / Linux でのダウンロードと起動手順。[v1.1.0]({RELEASE})。

## 概要

グラフィックス強化の **スケジューラ / 設定コーディネータ**。キットは同梱されません（BYO）。macOS は **設定のみ**（注入なし）。v1.1.0 は **未署名** です。

## 1. ダウンロード

[{RELEASE}]({RELEASE}) の **Assets** から OS 用ファイルを選びます（Windows Setup `.exe` / macOS `.app` zip / Linux onedir または wheel + `install_linux.sh`）。

## 2. Windows

1. エクスプローラー → **ダウンロード** → `.exe` を右クリック → **プロパティ** → **ブロックの解除** にチェック → **適用** → **OK**。
2. ダブルクリック。**WindowsによってPCが保護されました** が出たら **詳細情報** → **実行**。UAC は **はい**。
3. インストール後、Win キーで `buusdo` と検索して起動。
4. ファイルが消える場合: **Windows セキュリティ** → **ウイルスと脅威の防止** → **保護の履歴** → **復元**。

Python の別途インストールは Setup 実行に不要です。

## 3. macOS

1. zip を展開し `Buusdo.app` を **アプリケーション** へ。
2. **右クリック**（Control+クリック）→ **開く** → もう一度 **開く**。
3. 初回はダブルクリックだけでは開けないことがあります。SIP を無効にしないでください。
4. **システム設定** → **プライバシーとセキュリティ** → **このまま開く** も可。

## 4. Linux

```bash
bash install_linux.sh && buusdo
# または
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. 起動後

UI で ReShade / OptiScaler キットフォルダを指定。アンチチート遮断は迂回できません。問題は {REPO}/issues。
"""

BODIES["ko"] = f"""# buusdo 사용자 가이드（한국어）

언어: {nav("ko")}

Windows / macOS / Linux 다운로드 및 실행. [v1.1.0]({RELEASE}).

## 개요

그래픽 향상 **스케줄러/설정 조정** 도구. 키트는 번들되지 않음(BYO). macOS는 **설정 전용**(인젝션 없음). v1.1.0은 **미서명**입니다.

## 1. 다운로드

[{RELEASE}]({RELEASE}) **Assets**에서 OS별 파일 선택(Windows Setup `.exe` / macOS `.app` zip / Linux onedir 또는 wheel + `install_linux.sh`).

## 2. Windows

1. 탐색기 → **다운로드** → `.exe` 우클릭 → **속성** → **차단 해제** 체크 → **적용** → **확인**.
2. 더블클릭. **Windows의 PC 보호**가 뜨면 **추가 정보** → **실행**. UAC는 **예**.
3. 설치 후 Win 키로 `buusdo` 검색 후 실행.
4. 파일이 사라지면: **Windows 보안** → **바이러스 및 위협 방지** → **보호 기록** → **복원**.

Setup 실행에 Python 설치는 필요 없습니다.

## 3. macOS

1. zip 압축 해제 후 `Buusdo.app`을 **응용 프로그램**으로 이동.
2. **우클릭**(Control-클릭) → **열기** → 다시 **열기**.
3. 처음에는 더블클릭만으로 막힐 수 있음. SIP를 끄지 마세요.
4. **시스템 설정** → **개인정보 보호 및 보안** → **확인 없이 열기** 가능.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. 실행 후

UI에서 ReShade/OptiScaler 키트 폴더 지정. 안티치트 차단은 우회 불가. 이슈: {REPO}/issues.
"""

BODIES["de"] = f"""# buusdo-Benutzerhandbuch (Deutsch)

Sprachen: {nav("de")}

Download und Start unter Windows, macOS und Linux. [v1.1.0]({RELEASE}).

## Überblick

Desktop-**Scheduler / Konfigurations-Koordinator**. Kits sind BYO. macOS ist **nur Konfiguration** (kein Inject). v1.1.0 ist **unsigniert**.

## 1. Download

Unter [{RELEASE}]({RELEASE}) bei **Assets** die Datei für Ihr OS wählen (Windows-Setup `.exe` / macOS-`.app`-ZIP / Linux onedir oder Wheel + `install_linux.sh`).

## 2. Windows

1. Explorer → **Downloads** → Rechtsklick auf `.exe` → **Eigenschaften** → **Zulassen** / **Unblock** aktivieren → **Übernehmen** → **OK**.
2. Doppelklick. Bei **Windows hat Ihren PC geschützt**: **Weitere Informationen** → **Trotzdem ausführen**. UAC: **Ja**.
3. Nach Installation: Win-Taste, `buusdo` suchen.
4. Datei verschwunden: **Windows-Sicherheit** → **Viren- & Bedrohungsschutz** → **Schutzverlauf** → **Wiederherstellen**.

Für das Setup ist **kein** separates Python nötig.

## 3. macOS

1. ZIP entpacken, `Buusdo.app` nach **Programme** ziehen.
2. **Rechtsklick** (Control-Klick) → **Öffnen** → erneut **Öffnen**.
3. Nicht nur doppelklicken; SIP nicht deaktivieren.
4. Optional: **Systemeinstellungen** → **Datenschutz & Sicherheit** → **Dennoch öffnen**.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. Nach dem Start

Im UI Kit-Ordner wählen. Anti-Cheat-Sperren sind nicht umgehbar. Issues: {REPO}/issues.
"""

BODIES["fr"] = f"""# Guide utilisateur buusdo (Français)

Langues : {nav("fr")}

Télécharger et ouvrir buusdo sur Windows, macOS et Linux. [v1.1.0]({RELEASE}).

## Aperçu

Coordinateur / planificateur d’améliorations graphiques. Kits **non inclus** (BYO). macOS = **config seule** (pas d’injection). v1.1.0 est **non signé**.

## 1. Téléchargement

Sur [{RELEASE}]({RELEASE}), section **Assets** : Setup Windows `.exe` / zip macOS `.app` / Linux onedir ou wheel + `install_linux.sh`.

## 2. Windows

1. Explorateur → **Téléchargements** → clic droit `.exe` → **Propriétés** → cocher **Débloquer** → **Appliquer** → **OK**.
2. Double-clic. Si **Windows a protégé votre PC** : **Informations complémentaires** → **Exécuter quand même**. UAC : **Oui**.
3. Après install : touche Win, taper `buusdo`.
4. Fichier disparu : **Sécurité Windows** → **Protection contre les virus** → **Historique** → **Restaurer**.

Pas besoin de Python pour le Setup.

## 3. macOS

1. Dézipper, glisser `Buusdo.app` vers **Applications**.
2. **Clic droit** → **Ouvrir** → **Ouvrir** à nouveau.
3. Ne pas seulement double-cliquer ; ne pas désactiver SIP.
4. **Réglages Système** → **Confidentialité et sécurité** → **Ouvrir quand même**.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. Après le premier lancement

Choisir les dossiers de kits dans l’UI. Pas de contournement anti-cheat. Issues : {REPO}/issues.
"""

BODIES["es"] = f"""# Guía de usuario de buusdo (Español)

Idiomas: {nav("es")}

Descargar y abrir buusdo en Windows, macOS y Linux. [v1.1.0]({RELEASE}).

## Resumen

Coordinador / programador de mejoras gráficas. Kits BYO. macOS es **solo configuración**. v1.1.0 está **sin firmar**.

## 1. Descarga

En [{RELEASE}]({RELEASE}) → **Assets**: Setup Windows `.exe` / zip macOS `.app` / Linux onedir o wheel + `install_linux.sh`.

## 2. Windows

1. Explorador → **Descargas** → clic derecho `.exe` → **Propiedades** → marcar **Desbloquear** → **Aplicar** → **Aceptar**.
2. Doble clic. Si aparece **Windows protegió tu PC**: **Más información** → **Ejecutar de todos modos**. UAC: **Sí**.
3. Tras instalar: tecla Win, escribe `buusdo`.
4. Si desaparece: **Seguridad de Windows** → **Virus y amenazas** → **Historial** → **Restaurar**.

No hace falta Python para el Setup.

## 3. macOS

1. Descomprime el zip; mueve `Buusdo.app` a **Aplicaciones**.
2. **Clic derecho** → **Abrir** → **Abrir** otra vez.
3. No solo doble clic; no desactives SIP.
4. **Ajustes del Sistema** → **Privacidad y seguridad** → **Abrir de todos modos**.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. Tras el primer inicio

Elige carpetas de kits en la UI. El bloqueo anti-cheat no se puede omitir. Issues: {REPO}/issues.
"""

BODIES["it"] = f"""# Guida utente buusdo (Italiano)

Lingue: {nav("it")}

Download e avvio su Windows, macOS e Linux. [v1.1.0]({RELEASE}).

## Panoramica

Scheduler / coordinatore di configurazione grafica. Kit BYO. macOS è **solo config**. v1.1.0 è **non firmato**.

## 1. Download

Su [{RELEASE}]({RELEASE}) → **Assets**: Setup Windows `.exe` / zip macOS `.app` / Linux onedir o wheel + `install_linux.sh`.

## 2. Windows

1. Esplora file → **Download** → tasto destro `.exe` → **Proprietà** → spunta **Sblocca** → **Applica** → **OK**.
2. Doppio clic. Se compare **Windows ha protetto il PC**: **Ulteriori informazioni** → **Esegui comunque**. UAC: **Sì**.
3. Dopo l’installazione: tasto Win, digita `buusdo`.
4. File sparito: **Sicurezza di Windows** → **Protezione da virus** → **Cronologia** → **Ripristina**.

Python non serve per il Setup.

## 3. macOS

1. Estrai lo zip; trascina `Buusdo.app` in **Applicazioni**.
2. **Clic destro** → **Apri** → di nuovo **Apri**.
3. Non solo doppio clic; non disattivare SIP.
4. **Impostazioni di Sistema** → **Privacy e sicurezza** → **Apri comunque**.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. Dopo il primo avvio

Seleziona le cartelle kit nell’UI. Nessun bypass anti-cheat. Issues: {REPO}/issues.
"""

BODIES["pt"] = f"""# Guia do utilizador buusdo (Português)

Idiomas: {nav("pt")}

Transferir e abrir o buusdo no Windows, macOS e Linux. [v1.1.0]({RELEASE}).

## Resumo

Agendador / coordenador de configuração gráfica. Kits BYO. macOS é **só configuração**. v1.1.0 está **sem assinatura**.

## 1. Transferência

Em [{RELEASE}]({RELEASE}) → **Assets**: Setup Windows `.exe` / zip macOS `.app` / Linux onedir ou wheel + `install_linux.sh`.

## 2. Windows

1. Explorador → **Transferências** → clique direito no `.exe` → **Propriedades** → assinale **Desbloquear** → **Aplicar** → **OK**.
2. Duplo clique. Se aparecer **O Windows protegeu o PC**: **Mais informações** → **Executar mesmo assim**. UAC: **Sim**.
3. Após instalar: tecla Win, escreva `buusdo`.
4. Ficheiro desapareceu: **Segurança do Windows** → **Vírus e ameaças** → **Histórico** → **Restaurar**.

Não precisa de Python para o Setup.

## 3. macOS

1. Extraia o zip; arraste `Buusdo.app` para **Aplicações**.
2. **Clique direito** → **Abrir** → **Abrir** outra vez.
3. Não use só duplo clique; não desative o SIP.
4. **Definições do Sistema** → **Privacidade e segurança** → **Abrir mesmo assim**.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. Após o primeiro arranque

Escolha as pastas dos kits na UI. Bloqueios anti-cheat não têm “continuar mesmo assim”. Issues: {REPO}/issues.
"""

BODIES["pt-BR"] = f"""# Guia do usuário buusdo (Português do Brasil)

Idiomas: {nav("pt-BR")}

Baixar e abrir o buusdo no Windows, macOS e Linux. [v1.1.0]({RELEASE}).

## Resumo

Agendador / coordenador de configuração gráfica. Kits BYO. macOS é **só configuração**. v1.1.0 está **sem assinatura**.

## 1. Download

Em [{RELEASE}]({RELEASE}) → **Assets**: Setup Windows `.exe` / zip macOS `.app` / Linux onedir ou wheel + `install_linux.sh`.

## 2. Windows

1. Explorador → **Downloads** → botão direito no `.exe` → **Propriedades** → marque **Desbloquear** → **Aplicar** → **OK**.
2. Clique duplo. Se aparecer **O Windows protegeu seu PC**: **Mais informações** → **Executar assim mesmo**. UAC: **Sim**.
3. Depois de instalar: tecla Win, digite `buusdo`.
4. Arquivo sumiu: **Segurança do Windows** → **Proteção contra vírus** → **Histórico** → **Restaurar**.

Não precisa de Python para o Setup.

## 3. macOS

1. Extraia o zip; arraste `Buusdo.app` para **Aplicativos**.
2. **Clique com o botão direito** → **Abrir** → **Abrir** de novo.
3. Não use só clique duplo; não desative o SIP.
4. **Ajustes do Sistema** → **Privacidade e segurança** → **Abrir mesmo assim**.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. Após a primeira abertura

Escolha as pastas dos kits na UI. Bloqueio anti-cheat não tem bypass. Issues: {REPO}/issues.
"""

BODIES["ru"] = f"""# Руководство пользователя buusdo (Русский)

Языки: {nav("ru")}

Скачивание и запуск на Windows, macOS и Linux. [v1.1.0]({RELEASE}).

## Обзор

Планировщик / координатор графических настроек. Наборы (kits) BYO. На macOS — **только конфигурация**. v1.1.0 **без подписи**.

## 1. Скачивание

На [{RELEASE}]({RELEASE}) в **Assets** выберите файл для вашей ОС (Windows Setup `.exe` / macOS `.app` в zip / Linux onedir или wheel + `install_linux.sh`).

## 2. Windows

1. Проводник → **Загрузки** → ПКМ по `.exe` → **Свойства** → отметьте **Разблокировать** → **Применить** → **ОК**.
2. Двойной щелчок. Если **Windows защитила компьютер**: **Подробнее** → **Выполнить в любом случае**. UAC: **Да**.
3. После установки: Win, введите `buusdo`.
4. Файл исчез: **Безопасность Windows** → **Защита от вирусов** → **Журнал** → **Восстановить**.

Для Setup отдельный Python не нужен.

## 3. macOS

1. Распакуйте zip; перетащите `Buusdo.app` в **Программы**.
2. **ПКМ** (Control-клик) → **Открыть** → снова **Открыть**.
3. Не полагайтесь только на двойной щелчок; не отключайте SIP.
4. **Системные настройки** → **Конфиденциальность и безопасность** → **Всё равно открыть**.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. После первого запуска

Укажите папки kits в UI. Обход античита невозможен. Issues: {REPO}/issues.
"""


_CLONE = f"""```bash
git clone {REPO}.git
cd buusdo
uv venv --python 3.12 .venv
source .venv/bin/activate   # Windows: .venv\\\\Scripts\\\\activate
uv sync --extra devui
# or: python -m pip install -e ".[devui]"
python -m buusdo
```"""

# Audience + from-source blocks for locales not inlined in BODIES["en"|"zh"].
PATH_BLOCKS: dict[str, tuple[str, str]] = {
    "zh-Hant": (
        """## 該走哪條路徑

| 對象 | 怎麼做 |
|------|--------|
| **一般使用者** | 使用 **Releases** 的安裝包（Windows Setup / macOS `.app` zip / Linux `install_linux.sh` 或 onedir），並依下文解除封鎖 / SmartScreen / Gatekeeper。 |
| **開發者 / 進階** | 可用文末 **從原始碼執行**。這是 **開發路徑**，不是為了繞過 SmartScreen / Gatekeeper。 |

下載整個倉庫 **不能** 取代上述安裝包作為日常安裝方式。
""",
        f"""## 從原始碼執行（開發者 / 進階）

這是 **開發路徑**，**不是**一般使用者建議安裝方式，也 **不是** 用來繞過 SmartScreen / Gatekeeper。

{_CLONE}

仍需在 UI 自備工具包；自行編譯的套件預設仍為 **未簽名**。
""",
    ),
    "ja": (
        """## どの手順を使うか

| 対象 | 内容 |
|------|------|
| **一般ユーザー** | **Releases** の Setup / `.app` / `install_linux.sh`（または onedir）を使い、下記のブロック解除・SmartScreen・Gatekeeper 手順に従う。 |
| **開発者 / 上級** | 末尾の **ソースから実行**（開発用）。SmartScreen / Gatekeeper 回避のための公式手段ではない。 |

リポジトリ全体のクローンは、通常インストールの代わりにはなりません。
""",
        f"""## ソースから実行（開発者 / 上級）

**開発用パス**です。一般ユーザー向け推奨インストールではなく、SmartScreen / Gatekeeper 回避用でもありません。

{_CLONE}

キットは BYO。自前ビルドの `.exe` / `.app` は通常 **未署名** のままです。
""",
    ),
    "ko": (
        """## 어떤 경로를 쓸까

| 대상 | 방법 |
|------|------|
| **일반 사용자** | **Releases**의 Setup / `.app` / `install_linux.sh`(또는 onedir) + 아래 차단 해제 / SmartScreen / Gatekeeper 단계. |
| **개발자 / 고급** | 하단 **소스에서 실행**. **개발용**이며 SmartScreen / Gatekeeper 우회용이 아님. |

전체 저장소 클론은 일상 설치를 대체하지 않습니다.
""",
        f"""## 소스에서 실행（개발자 / 고급）

**개발 경로**입니다. 일반 사용자 권장 설치가 아니며, SmartScreen / Gatekeeper 우회 방법이 아닙니다.

{_CLONE}

키트는 BYO. 직접 빌드한 패키지는 기본적으로 **미서명**입니다.
""",
    ),
    "de": (
        """## Welcher Weg?

| Zielgruppe | Vorgehen |
|------------|----------|
| **Die meisten Nutzer** | **Releases**-Pakete (Windows-Setup / macOS-`.app` / Linux `install_linux.sh` oder onedir) + Unblock / SmartScreen / Gatekeeper unten. |
| **Entwickler / Fortgeschrittene** | Optional **Aus dem Quellcode** am Ende. Das ist ein **Dev-Pfad**, kein offizieller Weg, SmartScreen/Gatekeeper zu umgehen. |

Das Klonen des gesamten Repos ersetzt die empfohlenen Installer nicht.
""",
        f"""## Aus dem Quellcode (Entwickler / Fortgeschrittene)

**Dev-Pfad** — nicht die empfohlene Nutzerinstallation und **nicht** zum Umgehen von SmartScreen / Gatekeeper.

{_CLONE}

Kits bleiben BYO. Selbst gebaute `.exe` / `.app` sind standardmäßig **unsigniert**.
""",
    ),
    "fr": (
        """## Quelle voie ?

| Public | Action |
|--------|--------|
| **La plupart des utilisateurs** | Paquets **Releases** (Setup Windows / `.app` macOS / `install_linux.sh` ou onedir) + étapes de déblocage / SmartScreen / Gatekeeper ci-dessous. |
| **Développeurs / avancé** | Option **Depuis les sources** en fin de guide. Chemin **dev**, pas un moyen officiel de contourner SmartScreen / Gatekeeper. |

Cloner tout le dépôt ne remplace pas les installateurs recommandés.
""",
        f"""## Depuis les sources (développeurs / avancé)

Chemin **dev** — pas l’installation recommandée pour le grand public, et **pas** pour contourner SmartScreen / Gatekeeper.

{_CLONE}

Kits BYO. Les binaires auto-construits restent **non signés** par défaut.
""",
    ),
    "es": (
        """## ¿Qué ruta usar?

| Público | Qué hacer |
|---------|-----------|
| **Mayoría de usuarios** | Paquetes de **Releases** (Setup Windows / `.app` macOS / `install_linux.sh` u onedir) + desbloqueo / SmartScreen / Gatekeeper abajo. |
| **Desarrolladores / avanzado** | Opción **Desde el código fuente** al final. Ruta **dev**, no un atajo oficial para evitar SmartScreen / Gatekeeper. |

Clonar todo el repositorio no sustituye los instaladores recomendados.
""",
        f"""## Desde el código fuente (desarrolladores / avanzado)

Ruta **dev** — no es la instalación recomendada para usuarios, ni un método para evitar SmartScreen / Gatekeeper.

{_CLONE}

Kits BYO. Los binarios propios siguen **sin firmar** por defecto.
""",
    ),
    "it": (
        """## Quale percorso?

| Pubblico | Cosa fare |
|----------|-----------|
| **Maggioranza degli utenti** | Pacchetti **Releases** (Setup Windows / `.app` macOS / `install_linux.sh` o onedir) + sblocco / SmartScreen / Gatekeeper sotto. |
| **Sviluppatori / avanzato** | Opzione **Dal codice sorgente** in fondo. Percorso **dev**, non un modo ufficiale per evitare SmartScreen / Gatekeeper. |

Clonare l’intero repository non sostituisce gli installer consigliati.
""",
        f"""## Dal codice sorgente (sviluppatori / avanzato)

Percorso **dev** — non l’installazione consigliata per gli utenti, né per aggirare SmartScreen / Gatekeeper.

{_CLONE}

Kit BYO. I binari auto-compilati restano **non firmati** di default.
""",
    ),
    "pt": (
        """## Que caminho usar?

| Público | O que fazer |
|---------|-------------|
| **A maioria dos utilizadores** | Pacotes **Releases** (Setup Windows / `.app` macOS / `install_linux.sh` ou onedir) + desbloqueio / SmartScreen / Gatekeeper abaixo. |
| **Programadores / avançado** | Opção **A partir do código-fonte** no fim. Caminho **dev**, não um atalho oficial para evitar SmartScreen / Gatekeeper. |

Clonar o repositório inteiro não substitui os instaladores recomendados.
""",
        f"""## A partir do código-fonte (programadores / avançado)

Caminho **dev** — não é a instalação recomendada para utilizadores, nem para contornar SmartScreen / Gatekeeper.

{_CLONE}

Kits BYO. Binários próprios continuam **sem assinatura** por omissão.
""",
    ),
    "pt-BR": (
        """## Qual caminho usar?

| Público | O que fazer |
|---------|-------------|
| **Maioria dos usuários** | Pacotes **Releases** (Setup Windows / `.app` macOS / `install_linux.sh` ou onedir) + desbloqueio / SmartScreen / Gatekeeper abaixo. |
| **Desenvolvedores / avançado** | Opção **A partir do código-fonte** no final. Caminho **dev**, não um atalho oficial para evitar SmartScreen / Gatekeeper. |

Clonar o repositório inteiro não substitui os instaladores recomendados.
""",
        f"""## A partir do código-fonte (desenvolvedores / avançado)

Caminho **dev** — não é a instalação recomendada para usuários, nem para contornar SmartScreen / Gatekeeper.

{_CLONE}

Kits BYO. Binários próprios continuam **sem assinatura** por padrão.
""",
    ),
    "ru": (
        """## Какой путь выбрать?

| Кому | Что делать |
|------|------------|
| **Большинству пользователей** | Пакеты **Releases** (Windows Setup / macOS `.app` / Linux `install_linux.sh` или onedir) + шаги разблокировки / SmartScreen / Gatekeeper ниже. |
| **Разработчикам / продвинутым** | Раздел **Из исходников** в конце. Это **dev-путь**, а не официальный способ обойти SmartScreen / Gatekeeper. |

Клонирование всего репозитория не заменяет рекомендуемые установщики.
""",
        f"""## Из исходников (разработчики / продвинутые)

**Dev-путь** — не рекомендуемая установка для обычных пользователей и не способ обойти SmartScreen / Gatekeeper.

{_CLONE}

Наборы BYO. Собранные вами `.exe` / `.app` по умолчанию остаются **без подписи**.
""",
    ),
}


def stub_body(code: str, native: str, eng: str, langs: list[tuple[str, str, str]]) -> str:
    """English stub when a locale JSON exists but BODIES[code] was never written."""
    return f"""# buusdo user guide ({eng})

Languages: {nav(code, langs)}

> **Stub:** add a full translation for `{code}` ({native}). Until then, follow the
> English guide: [en.md](en.md). Latest release: [v1.1.0]({RELEASE}).

## Who should use which path

| Audience | What to do |
|----------|------------|
| **Most users** | **Releases** Setup / `.app` / `install_linux.sh` (or onedir) + unblock steps in [en.md](en.md). |
| **Developers / advanced** | From-source below — **dev path**, not for bypassing SmartScreen / Gatekeeper. |

## What you are installing

**buusdo Graphics Enhancement Tool** is a desktop **scheduler / config coordinator** for existing graphics stacks
(ReShade, OptiScaler, etc.). Kits are **BYO**. macOS is **config-only** (no injection).

## 1. Download

Open [{RELEASE}]({RELEASE}) → **Assets** → pick Windows Setup / macOS `.app` zip /
Linux onedir or wheel. Optional: verify `SHA256SUMS`.

## 2–4. Open the app

Use the same SmartScreen / Gatekeeper / Linux steps as [en.md](en.md) (unsigned
build). Do **not** disable SIP on macOS.

## 5. After first launch

Point the UI at your kit folders. Anti-cheat cannot be bypassed. Issues: {REPO}/issues.

## 6. From source (developers / advanced)

**Dev path** — not the recommended user install; not for bypassing SmartScreen / Gatekeeper.

{_CLONE}
"""


def apply_path_blocks(code: str, body: str) -> str:
    """Insert audience + from-source sections when not already present."""
    if "From source (developers" in body or "从源码运行" in body or "從原始碼執行" in body:
        return body
    if "ソースから実行" in body or "소스에서 실행" in body or "Aus dem Quellcode" in body:
        return body
    if "Depuis les sources" in body or "Desde el código" in body or "Dal codice sorgente" in body:
        return body
    if "A partir do código" in body or "Из исходников" in body:
        return body
    audience, source = PATH_BLOCKS.get(code, (None, None))
    if audience is None:
        return body
    # Insert audience before first "## 1." / localized equivalent heading after intro.
    for marker in (
        "## 1. ",
        "## 1．",
        "## 你在安裝",
        "## 你在安装",
        "## What you are installing",
        "## Überblick",
        "## Aperçu",
        "## Resumen",
        "## Panoramica",
        "## Обзор",
        "## 概要",
        "## 개요",
    ):
        idx = body.find(marker)
        if idx != -1 and marker.startswith("## 1"):
            body = body[:idx] + audience.rstrip() + "\n\n" + body[idx:]
            break
        if idx != -1 and marker in (
            "## 你在安裝",
            "## 你在安装",
            "## What you are installing",
            "## Überblick",
            "## Aperçu",
            "## Resumen",
            "## Panoramica",
            "## Обзор",
            "## 概要",
            "## 개요",
        ):
            body = body[:idx] + audience.rstrip() + "\n\n" + body[idx:]
            break
    if source.rstrip() not in body:
        body = body.rstrip() + "\n\n" + source.rstrip() + "\n"
    return body


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    langs = discover_langs()
    missing = [c for c, _, _ in langs if c not in BODIES]
    for code, native, eng in langs:
        if code not in BODIES:
            BODIES[code] = stub_body(code, native, eng, langs)
            print(f"stub BODIES[{code!r}] ({eng})")
    if missing:
        print(
            f"note: stubbed missing bodies for {missing}; "
            f"replace with real translations and LOCALE_NAMES entries as needed"
        )
    orphan_bodies = sorted(set(BODIES) - {c for c, _, _ in langs})
    if orphan_bodies:
        print(f"warn: BODIES without locale JSON (ignored): {orphan_bodies}")

    index_rows = "\n".join(
        f"| [{native}]({code}.md) | `{code}` | {eng} |"
        for code, native, eng in langs
    )
    index = f"""# buusdo Graphics Enhancement Tool — user guides

**Most users:** install from [Releases]({RELEASE}) (Windows Setup / macOS `.app` /
Linux `install_linux.sh` or onedir) and follow the unblock / SmartScreen /
Gatekeeper steps in your language guide.

**Developers / advanced:** optional from-source section in each guide
(`git clone` → venv → `python -m buusdo`) — a **dev path**, not a way to bypass
unsigned-app warnings.

GitHub **does not** auto-translate repository docs. This folder ships one guide
per UI locale from `buusdo/locales/` (same codes as the in-app language picker).

| Guide | Code | English name |
|-------|------|----------------|
{index_rows}

Canonical English: [en.md](en.md).  
Release: [v1.1.0]({RELEASE}). Signing: [../CODE_SIGNING.md](../CODE_SIGNING.md).

**Note:** Product UI strings are localized separately in `buusdo/locales/*.json`.
These guides are download / first-open instructions (especially unsigned Windows
SmartScreen and macOS Gatekeeper).
"""
    (OUT / "README.md").write_text(index + "\n", encoding="utf-8")

    for code, _, _ in langs:
        body = apply_path_blocks(code, BODIES[code])
        body = body.rstrip() + "\n" + common_footer(code, langs)
        (OUT / f"{code}.md").write_text(body, encoding="utf-8")
        print("wrote", code)

    print("ok", OUT, f"({len(langs)} locales from {LOCALES.relative_to(ROOT)})")


if __name__ == "__main__":
    main()
