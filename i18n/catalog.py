from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from config import ENV_LANG

LOCALES_DIR = Path(__file__).resolve().parent / "locales"
FALLBACK_LOCALE = "en"


@dataclass(frozen=True)
class LocaleInfo:
    code: str
    name: str
    native_name: str


def _read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _string_entries(data: dict) -> dict[str, str]:
    return {
        key: value
        for key, value in data.items()
        if not key.startswith("_") and isinstance(value, str)
    }


class I18n(QObject):
    """Looks up UI strings. Drop another JSON file in locales/ to add a language."""

    changed = pyqtSignal()

    def __init__(self, locale: str | None = None):
        super().__init__()
        self._fallback = _string_entries(_read_json(LOCALES_DIR / f"{FALLBACK_LOCALE}.json"))
        requested = locale or os.environ.get(ENV_LANG) or FALLBACK_LOCALE
        self._locale = requested if self._has_locale(requested) else FALLBACK_LOCALE
        self._messages = self._load(self._locale)

    @property
    def locale(self) -> str:
        return self._locale

    def t(self, key: str, **kwargs: object) -> str:
        template = self._messages.get(key) or self._fallback.get(key) or key
        if not kwargs:
            return template
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return template

    def set_locale(self, code: str) -> None:
        if not self._has_locale(code) or code == self._locale:
            return
        self._locale = code
        self._messages = self._load(code)
        self.changed.emit()

    def available(self) -> list[LocaleInfo]:
        found: list[LocaleInfo] = []
        for path in sorted(LOCALES_DIR.glob("*.json")):
            data = _read_json(path)
            meta = data.get("_meta") if isinstance(data.get("_meta"), dict) else {}
            found.append(
                LocaleInfo(
                    code=str(meta.get("code") or path.stem),
                    name=str(meta.get("name") or path.stem),
                    native_name=str(meta.get("nativeName") or path.stem),
                )
            )
        return found

    def _has_locale(self, code: str) -> bool:
        return (LOCALES_DIR / f"{code}.json").is_file()

    def _load(self, code: str) -> dict[str, str]:
        if code == FALLBACK_LOCALE:
            return dict(self._fallback)
        path = LOCALES_DIR / f"{code}.json"
        if not path.is_file():
            return dict(self._fallback)
        return _string_entries(_read_json(path))
