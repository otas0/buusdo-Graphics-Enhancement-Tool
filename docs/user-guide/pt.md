# Guia do utilizador buusdo (Português)

Idiomas: [Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · **Português** · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)

Transferir e abrir o buusdo no Windows, macOS e Linux. [v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0).

## Resumo

Agendador / coordenador de configuração gráfica. Kits BYO. macOS é **só configuração**. v1.1.0 está **sem assinatura**.

## 1. Transferência

Em [https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0) → **Assets**: Setup Windows `.exe` / zip macOS `.app` / Linux onedir ou wheel + `install_linux.sh`.

## 2. Windows

1. Explorador → **Transferências** → clique direito no `.exe` → **Propriedades** → assinale **Desbloquear** → **Aplicar** → **OK**.
2. Duplo clique. Se aparecer **O Windows protegeu o PC**: **Mais informações** → **Executar mesmo assim**. UAC: **Sim**.
3. Após instalar: tecla Win, escreva `buusdo`.
4. Ficheiro desapareceu: **Segurança do Windows** → **Vírus e ameaças** → **Histórico** → **Restaurar**.

Não precisa de Python para o Setup.

## 3. macOS

1. Extraia o zip; arraste `buusdo Graphics Enhancement Tool.app` para **Aplicações**.
2. **Clique direito** → **Abrir** → **Abrir** outra vez.
3. Não use só duplo clique; não desative o SIP.
4. **Definições do Sistema** → **Privacidade e segurança** → **Abrir mesmo assim**.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. Após o primeiro arranque

Escolha as pastas dos kits na UI. Bloqueios anti-cheat não têm “continuar mesmo assim”. Issues: https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues.

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*[Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · **Português** · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)*
