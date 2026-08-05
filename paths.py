"""Resolve file paths that work both in development and inside a PyInstaller bundle."""
import sys
import os


def resource_path(relative: str) -> str:
    """Return an absolute path to *relative* that works when frozen.

    PyInstaller extracts bundled data to a temporary folder given by
    ``sys._MEIPASS``; in normal development the project root is used.
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)
