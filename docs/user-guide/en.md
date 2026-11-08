# buusdo Graphics Enhancement Tool — user guide (English)

Languages: [Deutsch](de.md) · **English** · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)

How to download and open **buusdo Graphics Enhancement Tool** on Windows, macOS, and Linux. Latest release: [v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0).

## Who should use which path

| Audience | What to do |
|----------|------------|
| **Most users** | Download **Releases** packages (Windows Setup / macOS `.app` zip / Linux `install_linux.sh` or onedir). Follow the unblock / SmartScreen / Gatekeeper steps below. |
| **Developers / advanced** | Optional **from-source** path at the end of this guide (`git clone` → venv → `python -m buusdo`). That path is for **development**, not a supported way to “avoid” SmartScreen or Gatekeeper. |

Cloning the whole repository does **not** replace the recommended installers for normal use.

## What you are installing

**buusdo Graphics Enhancement Tool** is a desktop **scheduler / config coordinator** for existing graphics stacks (ReShade, OptiScaler, etc.). Kits are **BYO** (not bundled). Capabilities differ by OS — macOS is **config-only** (no injection).

## 1. Download the right file

1. Open [https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0) in a browser.
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
2. Or open `C:\Program Files\buusdo\buusdo.exe` (or `Program Files (x86)`).

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
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv sync --extra devui
# Or: python -m pip install -e ".[devui]"
python -m buusdo
```

You still need BYO ReShade / OptiScaler kits in the UI. Building your own `.exe` / `.app` from source remains **unsigned** unless you sign it yourself.

## 7. Still stuck?

Note: (1) full dialog title/screenshot, (2) installer vs installed app, (3) OS version. Open an issue at https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues.

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*[Deutsch](de.md) · **English** · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)*
