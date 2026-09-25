import os
import sys
from pathlib import Path

APP_NAME = "Foldery"
ORG_NAME = "Foldery"
ENV_PACK = "FOLDER_ICONS"
ENV_LANG = "FOLDERY_LANG"

IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS = sys.platform == "darwin"

ICON_EXTENSIONS = (".ico", ".png", ".jpg", ".jpeg")
if IS_MACOS:
    ICON_EXTENSIONS = ICON_EXTENSIONS + (".icns",)


def pack_dir_from_env() -> Path | None:
    raw = os.environ.get(ENV_PACK)
    if not raw:
        return None
    path = Path(raw).expanduser()
    return path if path.is_dir() else None
