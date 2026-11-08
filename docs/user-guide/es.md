# Guía de usuario de buusdo (Español)

Idiomas: [Deutsch](de.md) · [English](en.md) · **Español** · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)

Descargar y abrir buusdo en Windows, macOS y Linux. [v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0).

## Resumen

Coordinador / programador de mejoras gráficas. Kits BYO. macOS es **solo configuración**. v1.1.0 está **sin firmar**.

## 1. Descarga

En [https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0) → **Assets**: Setup Windows `.exe` / zip macOS `.app` / Linux onedir o wheel + `install_linux.sh`.

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

Elige carpetas de kits en la UI. El bloqueo anti-cheat no se puede omitir. Issues: https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues.

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*[Deutsch](de.md) · [English](en.md) · **Español** · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)*
