# Руководство пользователя buusdo (Русский)

Языки: [Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · **Русский** · [繁體中文](zh-Hant.md) · [简体中文](zh.md)

Скачивание и запуск на Windows, macOS и Linux. [v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0).

## Обзор

Планировщик / координатор графических настроек. Наборы (kits) BYO. На macOS — **только конфигурация**. v1.1.0 **без подписи**.

## 1. Скачивание

На [https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0) в **Assets** выберите файл для вашей ОС (Windows Setup `.exe` / macOS `.app` в zip / Linux onedir или wheel + `install_linux.sh`).

## 2. Windows

1. Проводник → **Загрузки** → ПКМ по `.exe` → **Свойства** → отметьте **Разблокировать** → **Применить** → **ОК**.
2. Двойной щелчок. Если **Windows защитила компьютер**: **Подробнее** → **Выполнить в любом случае**. UAC: **Да**.
3. После установки: Win, введите `buusdo`.
4. Файл исчез: **Безопасность Windows** → **Защита от вирусов** → **Журнал** → **Восстановить**.

Для Setup отдельный Python не нужен.

## 3. macOS

1. Распакуйте zip; перетащите `buusdo Graphics Enhancement Tool.app` в **Программы**.
2. **ПКМ** (Control-клик) → **Открыть** → снова **Открыть**.
3. Не полагайтесь только на двойной щелчок; не отключайте SIP.
4. **Системные настройки** → **Конфиденциальность и безопасность** → **Всё равно открыть**.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. После первого запуска

Укажите папки kits в UI. Обход античита невозможен. Issues: https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues.

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*[Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · **Русский** · [繁體中文](zh-Hant.md) · [简体中文](zh.md)*
