# buusdo-Benutzerhandbuch (Deutsch)

Sprachen: **Deutsch** · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)

Download und Start unter Windows, macOS und Linux. [v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0).

## Überblick

Desktop-**Scheduler / Konfigurations-Koordinator**. Kits sind BYO. macOS ist **nur Konfiguration** (kein Inject). v1.1.0 ist **unsigniert**.

## 1. Download

Unter [https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0) bei **Assets** die Datei für Ihr OS wählen (Windows-Setup `.exe` / macOS-`.app`-ZIP / Linux onedir oder Wheel + `install_linux.sh`).

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

Im UI Kit-Ordner wählen. Anti-Cheat-Sperren sind nicht umgehbar. Issues: https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues.

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

***Deutsch** · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)*
