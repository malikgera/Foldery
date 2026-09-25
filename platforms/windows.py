from __future__ import annotations

import ctypes
import os
import re
from pathlib import Path

from domain.errors import IconAssignError
from platforms.backend import FolderIconBackend

FILE_ATTRIBUTE_READONLY = 0x01
FILE_ATTRIBUTE_HIDDEN = 0x02
FILE_ATTRIBUTE_SYSTEM = 0x04
FILE_ATTRIBUTE_NORMAL = 0x80
INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF

SHCNE_UPDATEITEM = 0x00002000
SHCNF_PATHW = 0x0005

ICON_RESOURCE_RE = re.compile(
    r'IconResource\s*=\s*"?([^",\r\n]+)"?(?:,-?\d+)?',
    re.IGNORECASE,
)
ICON_FILE_RE = re.compile(
    r'IconFile\s*=\s*"?([^",\r\n]+)"?',
    re.IGNORECASE,
)


class WindowsBackend(FolderIconBackend):
    def set_icon(self, folder: Path, icon: Path, *, pack_dir: Path | None = None) -> None:
        try:
            icon_ref = self._icon_ref(icon, pack_dir)
            ini_path = folder / "desktop.ini"
            self._clear_ini(ini_path)
            # utf-16 writes a BOM; Explorer expects that on desktop.ini
            ini_path.write_text(
                f"[.ShellClassInfo]\nIconResource={icon_ref},0\n",
                encoding="utf-16",
            )
            ctypes.windll.kernel32.SetFileAttributesW(
                str(ini_path), FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
            )
            ctypes.windll.kernel32.SetFileAttributesW(str(folder), FILE_ATTRIBUTE_READONLY)
            self._notify(folder)
        except PermissionError as exc:
            raise IconAssignError(str(exc), code="permission") from exc
        except OSError as exc:
            raise IconAssignError(str(exc), code="generic", error=str(exc)) from exc

    def remove_icon(self, folder: Path) -> None:
        ini_path = folder / "desktop.ini"
        if not ini_path.exists():
            return
        try:
            ctypes.windll.kernel32.SetFileAttributesW(str(ini_path), FILE_ATTRIBUTE_NORMAL)
            ini_path.unlink()
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(folder))
            if attrs != INVALID_FILE_ATTRIBUTES:
                ctypes.windll.kernel32.SetFileAttributesW(
                    str(folder), attrs & ~FILE_ATTRIBUTE_READONLY
                )
            self._notify(folder)
        except OSError as exc:
            raise IconAssignError(str(exc), code="generic", error=str(exc)) from exc

    def assigned_icon(self, folder: Path, *, pack_dir: Path | None = None) -> Path | None:
        ini_path = folder / "desktop.ini"
        if not ini_path.exists():
            return None
        try:
            raw = ini_path.read_bytes()
            text = raw.decode("utf-16-le", errors="ignore").replace("\0", "")
            match = ICON_RESOURCE_RE.search(text) or ICON_FILE_RE.search(text)
            if not match:
                return None
            icon_ref = match.group(1).strip()
            real = Path(os.path.expandvars(icon_ref))
            if not real.is_absolute() and pack_dir:
                real = pack_dir / real.name
            return real if real.exists() else None
        except OSError:
            return None

    @property
    def supports_source_preview(self) -> bool:
        return True

    def _icon_ref(self, icon: Path, pack_dir: Path | None) -> str:
        if pack_dir and os.path.normcase(str(icon.parent.resolve())) == os.path.normcase(
            str(pack_dir.resolve())
        ):
            return f"%FOLDER_ICONS%\\{icon.name}"
        return str(icon)

    def _clear_ini(self, ini_path: Path) -> None:
        if not ini_path.exists():
            return
        try:
            ctypes.windll.kernel32.SetFileAttributesW(str(ini_path), FILE_ATTRIBUTE_NORMAL)
            ini_path.unlink()
        except OSError:
            pass

    def _notify(self, folder: Path) -> None:
        ctypes.windll.shell32.SHChangeNotify(
            SHCNE_UPDATEITEM,
            SHCNF_PATHW,
            ctypes.c_wchar_p(str(folder)),
            None,
        )
