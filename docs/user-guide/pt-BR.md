# Guia do usuário buusdo (Português do Brasil)

Idiomas: [Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · **Português (Brasil)** · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)

Baixar e abrir o buusdo no Windows, macOS e Linux. [v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0).

## Resumo

Agendador / coordenador de configuração gráfica. Kits BYO. macOS é **só configuração**. v1.1.0 está **sem assinatura**.

## 1. Download

Em [https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0) → **Assets**: Setup Windows `.exe` / zip macOS `.app` / Linux onedir ou wheel + `install_linux.sh`.

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

Escolha as pastas dos kits na UI. Bloqueio anti-cheat não tem bypass. Issues: https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues.

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*[Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · **Português (Brasil)** · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)*
