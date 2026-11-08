"""ensure_process_name must not re-exec frozen / .app launches."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

from buusdo.macos_name import _running_from_app_bundle, ensure_process_name


def test_running_from_app_bundle_detects_macos_layout(tmp_path: Path) -> None:
    exe = tmp_path / "Foo.app" / "Contents" / "MacOS" / "Buusdo"
    exe.parent.mkdir(parents=True)
    exe.write_text("")
    assert _running_from_app_bundle(exe) is True
    assert _running_from_app_bundle(tmp_path / "python") is False


def test_frozen_skips_reexec(monkeypatch) -> None:
    monkeypatch.delenv("BUUSDO_SKIP_REEXEC", raising=False)
    monkeypatch.delenv("_BUUSDO_NAMED", raising=False)
    monkeypatch.setattr(sys, "platform", "darwin", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    with patch("buusdo.macos_name.os.execv") as execv:
        ensure_process_name("buusdo")
        execv.assert_not_called()


def test_app_bundle_path_skips_reexec(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("BUUSDO_SKIP_REEXEC", raising=False)
    monkeypatch.delenv("_BUUSDO_NAMED", raising=False)
    monkeypatch.setattr(sys, "platform", "darwin", raising=False)
    if hasattr(sys, "frozen"):
        monkeypatch.delattr(sys, "frozen", raising=False)
    exe = tmp_path / "X.app" / "Contents" / "MacOS" / "Buusdo"
    exe.parent.mkdir(parents=True)
    exe.write_text("")
    monkeypatch.setattr(sys, "executable", str(exe))
    with patch("buusdo.macos_name.os.execv") as execv:
        ensure_process_name("buusdo")
        execv.assert_not_called()
