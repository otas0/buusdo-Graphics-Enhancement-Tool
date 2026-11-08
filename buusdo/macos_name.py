"""Make macOS Dock / menu bar show the product short name instead of \"Python\"."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _running_from_app_bundle(exe: Path) -> bool:
    """True when argv0 lives in ``Something.app/Contents/MacOS/``."""
    try:
        return exe.parent.name == "MacOS" and exe.parent.parent.name == "Contents"
    except OSError:
        return False


def ensure_process_name(name: str = "buusdo") -> None:
    """Re-exec via a same-dir symlink named for Dock (basename of argv0).

    Important: do **not** ``resolve()`` ``sys.executable`` — uv/venv may point at a
    shared CPython install; the shim must live next to the *venv* ``python`` so
    ``site-packages`` still resolve.

    Frozen PyInstaller / ``.app`` launches must **not** re-exec — Dock/menu names
    come from ``CFBundleName`` / ``CFBundleDisplayName``.
    """
    if sys.platform != "darwin":
        return
    if os.environ.get("BUUSDO_SKIP_REEXEC") == "1":
        return
    if os.environ.get("_BUUSDO_NAMED") == "1":
        return
    if getattr(sys, "frozen", False):
        return

    exe = Path(sys.executable)  # keep venv path; do not resolve()
    if _running_from_app_bundle(exe):
        return
    # Avoid clobbering the console-script entry ``.venv/bin/buusdo``.
    shim_name = "Buusdo" if name.lower() == "buusdo" else name
    if exe.name in {shim_name, name}:
        os.environ["_BUUSDO_NAMED"] = "1"
        return

    shim = exe.parent / shim_name
    try:
        target = exe.name  # relative symlink target
        if shim.is_symlink():
            if os.readlink(shim) != target:
                shim.unlink()
                shim.symlink_to(target)
        elif shim.exists():
            # Stale setuptools script or file — replace with symlink to interpreter.
            shim.unlink()
            shim.symlink_to(target)
        else:
            shim.symlink_to(target)
    except OSError:
        return

    os.environ["_BUUSDO_NAMED"] = "1"
    argv = [str(shim)]
    if "-m" in sys.argv:
        argv.extend(sys.argv[1:])
    else:
        argv.extend(["-m", "buusdo", *sys.argv[1:]])
    os.execv(str(shim), argv)
