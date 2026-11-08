# buusdo 사용자 가이드（한국어）

언어: [Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · **한국어** · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)

Windows / macOS / Linux 다운로드 및 실행. [v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0).

## 개요

그래픽 향상 **스케줄러/설정 조정** 도구. 키트는 번들되지 않음(BYO). macOS는 **설정 전용**(인젝션 없음). v1.1.0은 **미서명**입니다.

## 1. 다운로드

[https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0) **Assets**에서 OS별 파일 선택(Windows Setup `.exe` / macOS `.app` zip / Linux onedir 또는 wheel + `install_linux.sh`).

## 2. Windows

1. 탐색기 → **다운로드** → `.exe` 우클릭 → **속성** → **차단 해제** 체크 → **적용** → **확인**.
2. 더블클릭. **Windows의 PC 보호**가 뜨면 **추가 정보** → **실행**. UAC는 **예**.
3. 설치 후 Win 키로 `buusdo` 검색 후 실행.
4. 파일이 사라지면: **Windows 보안** → **바이러스 및 위협 방지** → **보호 기록** → **복원**.

Setup 실행에 Python 설치는 필요 없습니다.

## 3. macOS

1. zip 압축 해제 후 `Buusdo.app`을 **응용 프로그램**으로 이동.
2. **우클릭**(Control-클릭) → **열기** → 다시 **열기**.
3. 처음에는 더블클릭만으로 막힐 수 있음. SIP를 끄지 마세요.
4. **시스템 설정** → **개인정보 보호 및 보안** → **확인 없이 열기** 가능.

## 4. Linux

```bash
bash install_linux.sh && buusdo
python3 -m pip install ./buusdo-*-py3-none-any.whl "PySide6-Essentials==6.12.0" && python3 -m buusdo
```

## 5. 실행 후

UI에서 ReShade/OptiScaler 키트 폴더 지정. 안티치트 차단은 우회 불가. 이슈: https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/issues.

---

## Related docs

- Signing status: [CODE_SIGNING.md](../CODE_SIGNING.md)
- macOS package notes: [MAC_PACKAGE.md](../MAC_PACKAGE.md)
- Hardware honesty: [HARDWARE_NOTES.md](../HARDWARE_NOTES.md)
- Project constraints: [PROJECT.md](../PROJECT.md)

v1.1.0 is **unsigned**. SmartScreen / Gatekeeper warnings are expected. You do **not** need a system Python install to run the Windows Setup or macOS `.app` packages.

*[Deutsch](de.md) · [English](en.md) · [Español](es.md) · [Français](fr.md) · [Italiano](it.md) · [日本語](ja.md) · **한국어** · [Português (Brasil)](pt-BR.md) · [Português](pt.md) · [Русский](ru.md) · [繁體中文](zh-Hant.md) · [简体中文](zh.md)*
