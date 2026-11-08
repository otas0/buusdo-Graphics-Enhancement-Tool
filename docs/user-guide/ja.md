# buusdo ユーザーガイド（日本語）

言語: [Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · **日本語** · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)

Windows / macOS / Linux でのダウンロードと起動手順。[v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0)。

## 概要

グラフィックス強化の **スケジューラ / 設定コーディネータ**。キットは同梱されません（BYO）。macOS は **設定のみ**（注入なし）。v1.1.0 は **未署名** です。

## 1. ダウンロード

[https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0) の **Assets** から OS 用ファイルを選びます（Windows Setup `.exe` / macOS `.app` zip / Linux onedir または wheel + `install_linux.sh`）。

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

UI で ReShade / OptiScaler キットフォルダを指定。アンチチート遮断は迂回できません。問題は https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues。

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*[Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · **日本語** · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)*
