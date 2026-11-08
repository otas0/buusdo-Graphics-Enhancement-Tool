"""macOS Dock / .app icon helpers (ctypes AppKit — no PyObjC).

Runtime: ``setApplicationIconImage`` must load a **pre-masked squircle** icns
(transparent outside the continuous corner). A full-bleed opaque square becomes
a hard, oversize Dock tile.

Bundle: ``CFBundleIconFile`` can stay full-bleed for Finder; helpers that ignore
runtime overrides still need a branded Resources icns (see packaging).
"""

from __future__ import annotations

import ctypes
import ctypes.util
import sys
from pathlib import Path


def _resources_dir() -> Path | None:
    if not getattr(sys, "frozen", False):
        return None
    return Path(sys.executable).resolve().parent.parent / "Resources"


def dock_tile_icns_path() -> Path | None:
    """Icns with baked squircle alpha — for ``setApplicationIconImage`` only."""
    candidates: list[Path] = []
    res = _resources_dir()
    if res is not None:
        candidates.extend(
            [
                res / "AppIconDock.icns",
                res / "logo_dock.icns",
            ]
        )
    try:
        from buusdo.assets import asset_path

        candidates.append(asset_path("logo_dock.icns"))
        candidates.append(asset_path("logo.icns"))
    except Exception:
        pass
    # Fall back to masked PNG converted paths already in Resources
    if res is not None:
        candidates.append(res / "logo.icns")
    for path in candidates:
        if path.is_file():
            return path
    return None


def branded_icns_path() -> Path | None:
    """Prefer dock-tile (masked) asset; used by tests and runtime."""
    return dock_tile_icns_path()


def _objc() -> ctypes.CDLL | None:
    path = ctypes.util.find_library("objc")
    if not path:
        return None
    lib = ctypes.cdll.LoadLibrary(path)
    lib.objc_getClass.restype = ctypes.c_void_p
    lib.objc_getClass.argtypes = [ctypes.c_char_p]
    lib.sel_registerName.restype = ctypes.c_void_p
    lib.sel_registerName.argtypes = [ctypes.c_char_p]
    return lib


def _msg(objc: ctypes.CDLL, restype, argtypes):
    return ctypes.CFUNCTYPE(restype, *argtypes)(("objc_msgSend", objc))


def _nsimage_from_file(objc: ctypes.CDLL, path: Path):
    sel = objc.sel_registerName
    cls = objc.objc_getClass
    NSImage = cls(b"NSImage")
    NSString = cls(b"NSString")
    if not NSImage or not NSString:
        return None
    string_with_utf8 = _msg(
        objc, ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p]
    )
    path_ns = string_with_utf8(
        NSString, sel(b"stringWithUTF8String:"), str(path).encode("utf-8")
    )
    if not path_ns:
        return None
    alloc = _msg(objc, ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_void_p])
    init_file = _msg(
        objc, ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    )
    image = init_file(alloc(NSImage, sel(b"alloc")), sel(b"initWithContentsOfFile:"), path_ns)
    if not image:
        return None

    class NSSize(ctypes.Structure):
        _fields_ = [("width", ctypes.c_double), ("height", ctypes.c_double)]

    size = _msg(objc, NSSize, [ctypes.c_void_p, ctypes.c_void_p])(image, sel(b"size"))
    if size.width <= 0 or size.height <= 0:
        return None
    return image


def _nsapp() -> tuple[ctypes.CDLL, object, object] | None:
    objc = _objc()
    if objc is None:
        return None
    sel = objc.sel_registerName
    NSApplication = objc.objc_getClass(b"NSApplication")
    if not NSApplication:
        return None
    shared = _msg(objc, ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_void_p])
    app = shared(NSApplication, sel(b"sharedApplication"))
    if not app:
        return None
    return objc, app, sel


def clear_dock_icon_override() -> bool:
    """``setApplicationIconImage:nil`` so Dock uses CFBundleIconFile sizing."""
    if sys.platform != "darwin":
        return False
    ctx = _nsapp()
    if ctx is None:
        return False
    objc, app, sel = ctx
    _msg(objc, None, [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p])(
        app, sel(b"setApplicationIconImage:"), None
    )
    return True


def apply_dock_icon() -> bool:
    """Set the running app's Dock tile from an inset pre-masked squircle icns."""
    if sys.platform != "darwin":
        return False
    icns = dock_tile_icns_path()
    if icns is None:
        return False
    ctx = _nsapp()
    if ctx is None:
        return False
    objc, app, sel = ctx
    image = _nsimage_from_file(objc, icns)
    if not image:
        return False
    _msg(objc, None, [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p])(
        app, sel(b"setApplicationIconImage:"), image
    )
    return True


def set_bundle_finder_icon(app_bundle: Path, icns: Path) -> bool:
    """``NSWorkspace.setIcon:forFile:options:`` so Finder/Dock see branded art.

    Requires a live AppKit session: ``NSApplication.sharedApplication`` plus
    ``setActivationPolicy:`` (Accessory) before ``setIcon`` — otherwise the call
    returns NO on headless/CI builders.
    """
    if sys.platform != "darwin":
        return False
    if not app_bundle.is_dir() or not icns.is_file():
        return False
    ctx = _nsapp()
    if ctx is None:
        return False
    objc, app, sel = ctx
    # NSApplicationActivationPolicyAccessory = 1
    set_policy = _msg(
        objc, ctypes.c_bool, [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
    )
    set_policy(app, sel(b"setActivationPolicy:"), 1)

    image = _nsimage_from_file(objc, icns)
    if not image:
        return False
    NSWorkspace = objc.objc_getClass(b"NSWorkspace")
    NSString = objc.objc_getClass(b"NSString")
    if not NSWorkspace or not NSString:
        return False
    string_with_utf8 = _msg(
        objc, ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p]
    )
    path_ns = string_with_utf8(
        NSString, sel(b"stringWithUTF8String:"), str(app_bundle.resolve()).encode("utf-8")
    )
    shared = _msg(objc, ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_void_p])
    workspace = shared(NSWorkspace, sel(b"sharedWorkspace"))
    if not workspace or not path_ns:
        return False
    # BOOL setIcon:(NSImage*) forFile:(NSString*) options:(NSUInteger)
    set_icon = _msg(
        objc,
        ctypes.c_bool,
        [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong],
    )
    ok = bool(set_icon(workspace, sel(b"setIcon:forFile:options:"), image, path_ns, 0))
    # Flush Finder icon cache for this path.
    note = _msg(
        objc, None, [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    )
    note(workspace, sel(b"noteFileSystemChanged:"), path_ns)
    return ok
