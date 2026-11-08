# buusdo Graphics Enhancement Tool — 用户指南（简体中文）

语言: [Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · **简体中文**

如何在 Windows / macOS / Linux 上下载并打开 **buusdo**。最新版：[v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0)。

## 你在安装什么

buusdo 是桌面端的图形增强 **调度 / 配置协调** 工具（ReShade、OptiScaler 等）。工具包 **自备（BYO）**，不随安装包捆绑。各系统能力不同 — **macOS 仅为配置**（无注入）。

## 1. 下载正确的文件

1. 浏览器打开 [https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0)。
2. 滚到 **Assets**。
3. 按系统选择：
   - **Windows：** Setup / 安装包 `.exe`
   - **macOS：** zip 里的 `.app`
   - **Linux：** onedir 和/或 wheel + `install_linux.sh`
4. 不要只下 Source code，除非你要自己编译。
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
2. 或打开 `C:\Program Files\buusdo\buusdo.exe`（或 `Program Files (x86)`）。

### D. 文件消失 / 提示找不到

1. 开始菜单搜索并打开 **Windows 安全中心**。
2. **病毒和威胁防护** → **防护历史记录**。
3. 找到 buusdo / Setup → **还原** 或 **允许**。
4. 再执行解除锁定 + 仍要运行。

Edge/Chrome：`Ctrl + J` 打开下载列表，选 **保留** / **仍要保留**。

## 3. macOS — 打开 .app（未公证 / ad-hoc）

v1.1.0 **未**公证；zip 在改 Info.plist 后会做 **ad-hoc 签名**（便于启动），但 Gatekeeper 警告仍 **正常**。

1. 下载 macOS `.zip`，双击解压。
2. 将 **`buusdo Graphics Enhancement Tool.app`**（全称）拖到 **应用程序**。
3. 打开 **访达** → **应用程序**。
4. **右键**（或 Control-单击）应用 → **打开**。
5. 对话框再点一次 **打开**（未公证时首次需要）。
6. 若只双击出现 **移到废纸篓** / 无法打开：必须用右键 → **打开**。
7. 可选（Ventura+）：**系统设置** → **隐私与安全性** → 滚到应用提示 → **仍要打开**。
8. 核对 Dock：**logo** + 悬停全称。若用 venv / `python -m` 启动，Dock 可能是空白文档图标 — 请改用 `.app`。

**不要**为了跑 buusdo 去关 SIP。macOS 版仅为配置（C5）。

### 高级 — 自备 Developer ID 重签（可选）

仅当你**已经**有 Apple Developer ID Application 证书时适用。只影响**你本机**
（或你自己再分发的副本），**不能**消除其他人下载 GitHub zip 时的 Gatekeeper；
项目也**不会**上架公证包（见 [CODE_SIGNING.md](../CODE_SIGNING.md)）。

多数用户做到上面的「右键 → 打开」即可。完整命令见
[MAC_PACKAGE.md — Optional: re-sign with your own Developer ID](../MAC_PACKAGE.md)。

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

## 6. 仍打不开？

请记录：(1) 完整弹窗标题/截图 (2) 是安装包还是已安装程序 (3) 系统版本。到 https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues 提 Issue。

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*[Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · **简体中文***
