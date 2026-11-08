# buusdo Graphics Enhancement Tool

<p align="center">
  <img src="buusdo/assets/logo.png" alt="buusdo Graphics Enhancement Tool wordmark" width="280" />
</p>

<p align="center">
  <a href="docs/PROJECT_COMPLETE.md"><img src="https://img.shields.io/badge/product_track-complete-0E7A3A" alt="product track complete" /></a>
  <a href="https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0"><img src="https://img.shields.io/badge/shelf-v1.1.0-111111" alt="v1.1.0 GitHub shelf" /></a>
</p>

<p align="center">
  <strong>Download · Open · Install</strong><br />
  <a href="https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0"><strong>Get v1.1.0 (GitHub)</strong></a>
  ·
  <a href="https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/download/v1.1.0/buusdo-companion.apk"><strong>Companion APK</strong></a>
  ·
  <a href="docs/user-guide/README.md"><strong>User guide</strong></a>
  ·
  <a href="docs/user-guide/en.md">English</a>
  ·
  <a href="docs/PROJECT_COMPLETE.md"><strong>Complete</strong></a>
</p>

**buusdo Graphics Enhancement Tool** — cross-platform graphics enhancement **scheduler + config coordinator** (Windows / Linux / macOS).

It reuses each platform’s existing enhancement stack. It does not implement rendering beyond the injection host, does not implement ray tracing, and is not a game-mod authoring tool.

## User guide (start here)

If SmartScreen / Gatekeeper blocks the unsigned build, or you need step-by-step clicks for Windows, macOS, or Linux:

| | |
|--|--|
| **All languages (hub)** | **[docs/user-guide/](docs/user-guide/README.md)** |
| English | [en](docs/user-guide/en.md) |
| Chinese (Simplified) | [zh](docs/user-guide/zh.md) |
| Chinese (Traditional) | [zh-Hant](docs/user-guide/zh-Hant.md) |
| Japanese | [ja](docs/user-guide/ja.md) |
| Korean | [ko](docs/user-guide/ko.md) |
| Portuguese (Brazil) | [pt-BR](docs/user-guide/pt-BR.md) |
| Portuguese | [pt](docs/user-guide/pt.md) |
| Spanish | [es](docs/user-guide/es.md) |
| German | [de](docs/user-guide/de.md) |
| French | [fr](docs/user-guide/fr.md) |
| Italian | [it](docs/user-guide/it.md) |
| Russian | [ru](docs/user-guide/ru.md) |

Same locale codes as the in-app language picker (`buusdo/locales/`).

### GitHub shelf (v1.1.0) — not App Store / Play Store

| Product | Asset | Notes |
|---------|-------|-------|
| Desktop Windows | [`buusdo-setup-1.1.0.exe`](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/download/v1.1.0/buusdo-setup-1.1.0.exe) | Unsigned Inno |
| Desktop macOS | [`buusdo-macos-1.1.0.zip`](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/download/v1.1.0/buusdo-macos-1.1.0.zip) | Unsigned `.app` |
| Desktop Linux | [`buusdo-linux-1.1.0.tar.gz`](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/download/v1.1.0/buusdo-linux-1.1.0.tar.gz) + [`install_linux.sh`](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/download/v1.1.0/install_linux.sh) | Onedir |
| Desktop any OS | [`buusdo-1.1.0-py3-none-any.whl`](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/download/v1.1.0/buusdo-1.1.0-py3-none-any.whl) | pip |
| **Mobile Android** | [`buusdo-companion.apk`](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/download/v1.1.0/buusdo-companion.apk) | Sideload; cleartext LAN; **not** Play Store |
| Mobile iOS | [`mobile/flutter/ios/`](mobile/flutter/) | Source only — **no IPA** (certs cancelled) |
| Checksums | [`SHA256SUMS`](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/download/v1.1.0/SHA256SUMS) · [`SHA256SUMS-companion-apk.txt`](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/download/v1.1.0/SHA256SUMS-companion-apk.txt) | |

Latest release page: [v1.1.0](https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0). Scope: [docs/MVP.md](docs/MVP.md). Signing: [docs/CODE_SIGNING.md](docs/CODE_SIGNING.md). Mobile honesty: [docs/MOBILE.md](docs/MOBILE.md). Hardware: [docs/HARDWARE_NOTES.md](docs/HARDWARE_NOTES.md).

**Share blurb** (also [docs/SHARE_BLURB.md](docs/SHARE_BLURB.md); wordmark above):
buusdo Graphics Enhancement Tool 1.1.0 — desktop + companion APK (GitHub) · https://github.com/otas0/buusdo-Graphics-Enhancement-Tool/releases/tag/v1.1.0

### Unsigned vs notarized (macOS / Windows)

| Build | What you see | Status for v1.1.0 |
|-------|----------------|-------------------|
| **Unsigned** | Windows SmartScreen / macOS Gatekeeper (“Not Opened” / Move to Trash) | **Current** — expected |
| **Notarized + stapled** (macOS Developer ID) | Fresh download opens without that Gatekeeper block | **Cancelled** — will not ship ([CODE_SIGNING.md](docs/CODE_SIGNING.md)) |
| **Authenticode** (Windows EV/OV) | Fewer SmartScreen warnings | **Cancelled** — will not ship |

macOS first open: Finder → right-click `Buusdo.app` → **Open**. Product track is
**complete** at this unsigned shelf — [docs/PROJECT_COMPLETE.md](docs/PROJECT_COMPLETE.md).

## End-user install

**Most users:** prefer the **packaged release** (Windows Setup / macOS `.app` zip /
Linux `install_linux.sh` or onedir). See the **[User guide](docs/user-guide/README.md)**
for first-open steps (unsigned SmartScreen / Gatekeeper — unblock / Run anyway /
right-click Open). Downloading the whole git repository is **not** the recommended
install path for normal use.

### Developers / advanced: from source (dev path)

For contributing or debugging only — **not** a supported way to bypass SmartScreen /
Gatekeeper:

```bash
git clone https://github.com/otas0/buusdo.git
cd buusdo
uv venv --python 3.12 .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv sync --extra devui
python -m buusdo
```

Details (all UI languages): [docs/user-guide/](docs/user-guide/README.md).

### Advanced: Python wheel (from Releases)

1. Install Python 3.11+ and get a wheel from a release/`dist/` build (`buusdo-*.whl`).
2. Install and launch:

```bash
python -m pip install ./buusdo-*-py3-none-any.whl
python -m pip install "PySide6-Essentials==6.12.0"   # UI
python -m buusdo
```

3. In the UI, choose your **ReShade / OptiScaler kit** folders (third-party binaries are not bundled).

Verify: `shasum -a 256 -c dist/SHA256SUMS` (or `sha256sum -c`).

Developer self-test (no third-party acceptance): `python scripts/mvp_self_test.py`  
Wheel package: `bash scripts/package_mvp.sh`  
Windows Inno installer (**Windows builder only**, unsigned; SmartScreen may warn):
`scripts\windows_github_release.bat` or `bash scripts/package_windows_inno.sh`  
Kits are self-provided; DWM HDR is not in the GitHub v1 release ([docs/STORE_MVP.md](docs/STORE_MVP.md)).

## Development

```bash
# Prefer uv (Homebrew Python on this machine may have a broken platform.mac_ver)
uv venv --python 3.12 .venv
source .venv/bin/activate
# Canonical once lock consumers standardize:
uv sync --extra devui
# Equivalent editable path:
#   uv pip install -e ".[devui]"
pytest
python scripts/mvp_self_test.py
python -m buusdo
```

## Architecture

- `core/` — platform detection, Steam discovery, ReShade deploy, anti-cheat gate, transactional writes
- `backends/` — platform-specific implementations (the only places allowed to branch on platform, plus `platform_detect`)
- `ui/` — PySide6; depends only on `EnhancementBackend`; anti-cheat blocks are non-bypassable

## ReShade / OptiScaler kits

Third-party binaries are not bundled. Pick kit folders in the UI, or:

```python
from buusdo.core.config_store import set_reshade_kit_path, set_optiscaler_kit_path
set_reshade_kit_path("/path/to/reshade_kit")
set_optiscaler_kit_path("/path/to/optiscaler_kit")
```

- D3D/OpenGL: proxy DLL; Vulkan: explicit-layer JSON + launch-option hints
- Linux Proton: deploy under `steamapps/common/<game>`; vkBasalt can write back `localconfig.vdf`
- macOS: MetalFX compatibility-layer config only (GPTK / CrossOver / Bridgeplay)

```bash
python scripts/check_no_platform_branch.py   # C3 lint
./scripts/deploy.sh                          # pyside6-deploy packaging skeleton
```

## Steam URI probe (UI)

After **Clear cache now**, use **Try open first**; if that candidate fails, **Try next (N left)**
(or **Ctrl+N** while that button is enabled) walks the remaining deep-link schemes for the
selected game without clearing the list. The button tooltip previews the next URI candidate.

## CI, artifacts, and billing failures

GitHub Actions artifacts (`dwm-hdr-poc`, Qt diag tarballs) and common failure modes
(artifact quota, 0-step jobs from Actions spending limits, Bearer token prune) are
documented in [docs/CI_ARTIFACTS.md](docs/CI_ARTIFACTS.md).

After fixing Billing, **one** `workflow_dispatch` is enough — do not poll Actions from agents.
Billing awareness for local machines: **LaunchAgent only** (`install_watch_ci_billing_launchd.sh`); do not agent-poll Actions.

Quick local checks:

```bash
python scripts/watch_ci_billing.py --notify --once   # exit 1 if newest run looks billing-blocked
bash scripts/install_watch_ci_billing_launchd.sh     # hourly macOS LaunchAgent (appending logs)
bash scripts/assert_watch_ci_billing_log_append.sh    # kickstart + exit-after-timestamp assert
python scripts/verify_dwm_hdr_poc_local.py            # offline zip + hlsl_sha256 (no network)
python scripts/verify_dwm_hdr_poc_local.py --json     # machine-readable summary
bash scripts/push_when_online.sh                     # finite-retry git push (flaky HTTPS)
```

Optional weekly Monday assert (LaunchAgent — still no Actions poll):

```bash
bash scripts/install_assert_watch_ci_billing_weekly.sh
# or crontab: 0 9 * * 1 cd /path/to/buusdo && bash scripts/assert_watch_ci_billing_log_append.sh >>~/Library/Logs/buusdo/assert-cron.log 2>&1
```
