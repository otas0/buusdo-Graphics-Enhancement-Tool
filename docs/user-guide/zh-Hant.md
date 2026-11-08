# buusdo 使用者指南（繁體中文）

語言: [Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · **繁體中文** · [简体中文](zh.md)

如何在 Windows / macOS / Linux 下載並開啟 **buusdo**。最新版：[v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0)。

## 你在安裝什麼

buusdo 是桌面端的圖形增強 **排程 / 設定協調** 工具。工具包需 **自行準備（BYO）**。macOS **僅設定、無注入**。

## 該走哪條路徑

| 對象 | 怎麼做 |
|------|--------|
| **一般使用者** | 使用 **Releases** 的安裝包（Windows Setup / macOS `.app` zip / Linux `install_linux.sh` 或 onedir），並依下文解除封鎖 / SmartScreen / Gatekeeper。 |
| **開發者 / 進階** | 可用文末 **從原始碼執行**。這是 **開發路徑**，不是為了繞過 SmartScreen / Gatekeeper。 |

下載整個倉庫 **不能** 取代上述安裝包作為日常安裝方式。

## 1. 下載正確的檔案

1. 開啟 [https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0)。
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

在 UI 選擇 ReShade / OptiScaler 工具包目錄；反作弊阻擋無法略過。問題請開 https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues。

## 從原始碼執行（開發者 / 進階）

這是 **開發路徑**，**不是**一般使用者建議安裝方式，也 **不是** 用來繞過 SmartScreen / Gatekeeper。

```bash
git clone https://github.com/otas0/buusdo.git
cd buusdo
uv venv --python 3.12 .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
uv sync --extra devui
# or: python -m pip install -e ".[devui]"
python -m buusdo
```

仍需在 UI 自備工具包；自行編譯的套件預設仍為 **未簽名**。

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*[Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · **繁體中文** · [简体中文](zh.md)*
