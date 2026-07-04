"""JSON-based cache for taxonomy records with optional expiration and versioning."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class JsonTaxidCache:
    """A small JSON cache for serialized taxonomy records."""

    def __init__(
        self,
        path: str | Path,
        version: str = "1.0",
        expires_after_seconds: int | None = None,
    ) -> None:
        self.path = Path(path)
        self.version = version
        self.expires_after_seconds = expires_after_seconds
        self.data: dict[str, Any] = {"version": version, "taxa": {}}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.data = {"version": self.version, "taxa": {}}
            return

        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.data = {"version": self.version, "taxa": {}}
            return

        if not isinstance(loaded, dict):
            self.data = {"version": self.version, "taxa": {}}
            return

        self.data = {
            "version": loaded.get("version", self.version),
            "taxa": loaded.get("taxa", {}),
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, delete=False) as handle:
            json.dump(self.data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            temp_path = handle.name
        os.replace(temp_path, self.path)

    def get(self, taxid: str) -> dict[str, Any] | None:
        entry = self.data.get("taxa", {}).get(str(taxid))
        if not isinstance(entry, dict):
            return None
        if self._is_expired(entry):
            self.data.setdefault("taxa", {}).pop(str(taxid), None)
            return None
        return entry

    def set(self, taxid: str, value: dict[str, Any]) -> None:
        payload = dict(value)
        payload["cached_at"] = payload.get("cached_at") or str(__import__("time").time())
        self.data.setdefault("taxa", {})[str(taxid)] = payload

    def bulk_set(self, values: dict[str, dict[str, Any]]) -> None:
        for taxid, value in values.items():
            self.set(taxid, value)

    def _is_expired(self, entry: dict[str, Any]) -> bool:
        if self.expires_after_seconds is None:
            return False
        cached_at = entry.get("cached_at")
        if not cached_at:
            return False
        try:
            cached_timestamp = float(cached_at)
        except (TypeError, ValueError):
            return False
        return (self._now() - cached_timestamp) > self.expires_after_seconds

    @staticmethod
    def _now() -> float:
        return __import__("time").time()
