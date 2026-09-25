from __future__ import annotations

from pathlib import Path

from domain.errors import IconAssignError
from i18n.catalog import I18n
from platforms.backend import FolderIconBackend


class AssignmentService:
    def __init__(self, backend: FolderIconBackend):
        self._backend = backend

    @property
    def supports_source_preview(self) -> bool:
        return self._backend.supports_source_preview

    def assign(
        self,
        folders: list[Path],
        icon: Path,
        *,
        pack_dir: Path | None = None,
    ) -> list[tuple[Path, IconAssignError]]:
        errors: list[tuple[Path, IconAssignError]] = []
        for folder in folders:
            try:
                self._backend.set_icon(folder, icon, pack_dir=pack_dir)
            except IconAssignError as exc:
                errors.append((folder, exc))
        return errors

    def remove(self, folders: list[Path]) -> list[tuple[Path, IconAssignError]]:
        errors: list[tuple[Path, IconAssignError]] = []
        for folder in folders:
            try:
                self._backend.remove_icon(folder)
            except IconAssignError as exc:
                errors.append((folder, exc))
        return errors

    def preview_path(self, folder: Path, *, pack_dir: Path | None = None) -> Path | None:
        return self._backend.assigned_icon(folder, pack_dir=pack_dir)


def format_assign_error(i18n: I18n, error: IconAssignError) -> str:
    details = {key: str(value) for key, value in error.details.items()}
    if "error" not in details:
        details["error"] = str(error)
    key = f"error.{error.code}"
    text = i18n.t(key, **details)
    return text if text != key else str(error)
