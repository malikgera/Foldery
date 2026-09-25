import sys

from platforms.backend import FolderIconBackend
from platforms.macos import MacBackend
from platforms.unsupported import UnsupportedBackend
from platforms.windows import WindowsBackend


def create_backend() -> FolderIconBackend:
    if sys.platform.startswith("win"):
        return WindowsBackend()
    if sys.platform == "darwin":
        return MacBackend()
    return UnsupportedBackend()
