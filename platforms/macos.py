from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from domain.errors import IconAssignError
from platforms.backend import FolderIconBackend

# Finder stores a custom icon as a resource file named Icon + CR
MAC_ICON_FILENAME = "Icon\r"


class MacBackend(FolderIconBackend):
    def __init__(self) -> None:
        self._pyobjc = False
        try:
            from AppKit import NSImage, NSWorkspace  # noqa: F401

            self._pyobjc = True
        except Exception:
            self._pyobjc = False

    def set_icon(self, folder: Path, icon: Path, *, pack_dir: Path | None = None) -> None:
        icns_path, is_temp = self._ensure_icns(icon)
        try:
            if self._pyobjc:
                self._set_pyobjc(folder, icns_path)
            else:
                self._set_applescript(folder, icns_path)
        finally:
            if is_temp:
                shutil.rmtree(icns_path.parent, ignore_errors=True)

    def remove_icon(self, folder: Path) -> None:
        icon_file = folder / MAC_ICON_FILENAME
        try:
            if icon_file.exists():
                icon_file.unlink()
            subprocess.run(
                ["xattr", "-d", "com.apple.FinderInfo", str(folder)],
                capture_output=True,
            )
            subprocess.run(
                ["xattr", "-d", "com.apple.ResourceFork", str(folder)],
                capture_output=True,
            )
        except OSError as exc:
            raise IconAssignError(str(exc), code="generic", error=str(exc)) from exc

    def assigned_icon(self, folder: Path, *, pack_dir: Path | None = None) -> Path | None:
        icon_file = folder / MAC_ICON_FILENAME
        if icon_file.exists():
            return icon_file
        try:
            result = subprocess.run(
                ["xattr", "-p", "com.apple.FinderInfo", str(folder)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                return Path("__embedded__")
        except OSError:
            pass
        return None

    def _ensure_icns(self, source: Path) -> tuple[Path, bool]:
        if source.suffix.lower() == ".icns":
            return source, False

        try:
            from PIL import Image
        except ImportError as exc:
            raise IconAssignError(str(exc), code="pillow") from exc

        tmp_dir = Path(tempfile.mkdtemp(prefix="foldery_icns_"))
        iconset = tmp_dir / "icon.iconset"
        iconset.mkdir()

        try:
            image = Image.open(source).convert("RGBA")
        except Exception as exc:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise IconAssignError(str(exc), code="badImage", error=str(exc)) from exc

        sizes = [16, 32, 64, 128, 256, 512, 1024]
        for size in sizes:
            image.resize((size, size), Image.LANCZOS).save(iconset / f"icon_{size}x{size}.png")
            if size <= 512:
                image.resize((size * 2, size * 2), Image.LANCZOS).save(
                    iconset / f"icon_{size}x{size}@2x.png"
                )

        icns_path = tmp_dir / "icon.icns"
        try:
            subprocess.run(
                ["iconutil", "-c", "icns", str(iconset), "-o", str(icns_path)],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise IconAssignError(str(exc), code="iconutil", error=str(exc)) from exc

        return icns_path, True

    def _set_pyobjc(self, folder: Path, icns_path: Path) -> None:
        from AppKit import NSImage, NSWorkspace

        image = NSImage.alloc().initWithContentsOfFile_(str(icns_path))
        if image is None:
            raise IconAssignError("Could not load .icns", code="icnsLoad")
        ok = NSWorkspace.sharedWorkspace().setIcon_forFile_options_(image, str(folder), 0)
        if not ok:
            raise IconAssignError("NSWorkspace refused", code="nsworkspace")

    def _set_applescript(self, folder: Path, icns_path: Path) -> None:
        script = f'''
        use framework "AppKit"
        set theImage to current application's NSImage's alloc()'s initWithContentsOfFile:"{icns_path}"
        current application's NSWorkspace's sharedWorkspace()'s setIcon:theImage forFile:"{folder}" options:0
        '''
        try:
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise IconAssignError(str(exc), code="applescript", error=str(exc)) from exc
