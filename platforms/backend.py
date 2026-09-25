from abc import ABC, abstractmethod
from pathlib import Path


class FolderIconBackend(ABC):
    @abstractmethod
    def set_icon(self, folder: Path, icon: Path, *, pack_dir: Path | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_icon(self, folder: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    def assigned_icon(self, folder: Path, *, pack_dir: Path | None = None) -> Path | None:
        """Return a path the UI can preview, or None if nothing is set."""
        raise NotImplementedError

    @property
    def supports_source_preview(self) -> bool:
        return False
