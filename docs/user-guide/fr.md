# Guide utilisateur buusdo (Français)

Langues : [Deutsch](de.md) · [English](en.md) · [Español](es.md) · **Français** · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)

Télécharger et ouvrir buusdo sur Windows, macOS et Linux. [v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0).

## Aperçu

Coordinateur / planificateur d’améliorations graphiques. Kits **non inclus** (BYO). macOS = **config seule** (pas d’injection). v1.1.0 est **non signé**.

## 1. Téléchargement

Sur [https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0), section **Assets** : Setup Windows `.exe` / zip macOS `.app` / Linux onedir ou wheel + `install_linux.sh`.

## 2. Windows

1. Explorateur → **Téléchargements** → clic droit `.exe` → **Propriétés** → cocher **Débloquer** → **Appliquer** → **OK**.
2. Double-clic. Si **Windows a protégé votre PC** : **Informations complémentaires** → **Exécuter quand même**. UAC : **Oui**.
3. Après install : touche Win, taper `buusdo`.
4. Fichier disparu : **Sécurité Windows** → **Protection contre les virus** → **Historique** → **Restaurer**.

Pas besoin de Python pour le Setup.

## 3. macOS

1. Dézipper, glisser `buusdo Graphics Enhancement Tool.app` vers **Applications**.
2. **Clic droit** → **Ouvrir** → **Ouvrir** à nouveau.
3. Ne pas seulement double-cliquer ; ne pas désactiver SIP.
4. **Réglages Système** → **Confidentialité et sécurité** → **Ouvrir quand même**.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. Après le premier lancement

Choisir les dossiers de kits dans l’UI. Pas de contournement anti-cheat. Issues : https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues.

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*[Deutsch](de.md) · [English](en.md) · [Español](es.md) · **Français** · [Italiano](it.md) · [日本語](ja.md) · [한국어](ko.md) · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)*
