"""Top-level package for the GOLD XAUUSD trading stack."""

from importlib import metadata

try:
    __version__ = metadata.version("goldbot")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.0"

from .config import settings  # noqa: E402

__all__ = ["__version__", "settings"]

