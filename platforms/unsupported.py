import platform
from pathlib import Path

from domain.errors import IconAssignError
from platforms.backend import FolderIconBackend


class UnsupportedBackend(FolderIconBackend):
    def set_icon(self, folder: Path, icon: Path, *, pack_dir: Path | None = None) -> None:
        raise IconAssignError(
            f"{platform.system()} is not supported",
            code="unsupported",
            system=platform.system(),
        )

    def remove_icon(self, folder: Path) -> None:
        raise IconAssignError(
            f"{platform.system()} is not supported",
            code="unsupported",
            system=platform.system(),
        )

    def assigned_icon(self, folder: Path, *, pack_dir: Path | None = None) -> Path | None:
        return None
