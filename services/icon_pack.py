from __future__ import annotations

import shutil
from pathlib import Path

from config import ICON_EXTENSIONS, pack_dir_from_env


class IconPack:
    def __init__(self, directory: Path | None = None):
        self.directory = directory

    @classmethod
    def from_env(cls) -> IconPack:
        return cls(pack_dir_from_env())

    def set_directory(self, directory: Path | None) -> None:
        self.directory = directory

    def list_icons(self) -> list[Path]:
        if not self.directory or not self.directory.is_dir():
            return []
        files = [
            path
            for path in self.directory.iterdir()
            if path.is_file() and path.suffix.lower() in ICON_EXTENSIONS
        ]
        files.sort(key=lambda path: path.name.lower())
        return files

    def add_files(self, sources: list[Path]) -> tuple[int, list[tuple[Path, Exception]]]:
        if not self.directory:
            return 0, []
        self.directory.mkdir(parents=True, exist_ok=True)
        copied = 0
        errors: list[tuple[Path, Exception]] = []
        for src in sources:
            dest = self.directory / src.name
            try:
                if src.resolve() != dest.resolve():
                    shutil.copy2(src, dest)
                copied += 1
            except OSError as exc:
                errors.append((src, exc))
        return copied, errors
