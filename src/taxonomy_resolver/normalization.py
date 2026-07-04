"""Helpers for normalizing taxonomic names and extracting genera."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable


def normalize_name(name: str | None) -> str:
    """Normalize a taxonomic name into a compact lowercase token sequence."""
    if not name:
        return ""

    norm = unicodedata.normalize("NFKD", str(name))
    norm = norm.lower()
    norm = norm.replace("&", " and ")
    norm = re.sub(r"[()\[\]{}]", " ", norm)
    norm = re.sub(r"[^a-z0-9\s\-]", " ", norm)
    norm = re.sub(r"\s+", " ", norm)
    return norm.strip()


def extract_genus(name: str | None) -> str:
    normalized = normalize_name(name)
    parts = normalized.split()
    return parts[0] if parts else ""


def normalize_names(names: Iterable[str | None]) -> set[str]:
    return {normalize_name(name) for name in names if name}
