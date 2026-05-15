"""
Persistent JSON configuration for the cleaner.
"""
import json
import sys
from pathlib import Path

_DEFAULTS = {
    "version": "1.0",
    "confirm_before_clean": True,
    "excluded_paths": [],
}

def _app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


_CONFIG_FILE = _app_dir() / "config.json"


class Config:
    def __init__(self) -> None:
        self._data = _DEFAULTS.copy()
        self._load()

    def _load(self) -> None:
        if _CONFIG_FILE.exists():
            try:
                with _CONFIG_FILE.open(encoding="utf-8") as f:
                    self._data.update(json.load(f))
            except Exception:
                pass

    def save(self) -> None:
        with _CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value) -> None:
        self._data[key] = value
        self.save()
