from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("codexrenderer")
except PackageNotFoundError:  # pragma: no cover - editable install
    __version__ = "0.0.dev0"

__all__ = ["__version__"]
