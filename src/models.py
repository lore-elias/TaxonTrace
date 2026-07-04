"""Core data models for taxonomy records and match results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MatchConfidence(str, Enum):
    """Confidence labels for taxonomy name matching."""

    EXACT = "exact"
    TAXID = "taxid"
    GENUS = "genus"
    FUZZY = "fuzzy"
    NONE = "none"


@dataclass(slots=True)
class TaxonRecord:
    """A normalized representation of a taxon entry."""

    taxid: str
    name: str
    rank: str = ""
    lineage: list[dict[str, str]] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    historical_names: list[str] = field(default_factory=list)
    provider: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "taxid": self.taxid,
            "name": self.name,
            "rank": self.rank,
            "lineage": self.lineage,
            "synonyms": self.synonyms,
            "historical_names": self.historical_names,
            "provider": self.provider,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaxonRecord":
        return cls(
            taxid=str(payload.get("taxid", "")),
            name=str(payload.get("name", "")),
            rank=str(payload.get("rank", "")),
            lineage=list(payload.get("lineage", []) or []),
            synonyms=list(payload.get("synonyms", []) or []),
            historical_names=list(payload.get("historical_names", []) or []),
            provider=payload.get("provider"),
            metadata=dict(payload.get("metadata", {}) or {}),
        )

    def lineage_names(self) -> list[str]:
        return [entry.get("name", "") for entry in self.lineage if entry.get("name")]

    def ancestor_by_rank(self, rank: str) -> dict[str, str] | None:
        target_rank = rank.lower()
        for entry in reversed(self.lineage):
            if str(entry.get("rank", "")).lower() == target_rank:
                return entry
        return None


@dataclass(slots=True)
class PanelMatchResult:
    """The outcome of matching a user-provided name against known taxa."""

    matched: bool
    genus_fallback: bool = False
    fuzzy_match: str | None = None
    matched_name: str | None = None
    confidence: MatchConfidence = MatchConfidence.NONE

    def to_dict(self) -> dict[str, Any]:
        return {
            "matched": self.matched,
            "genus_fallback": self.genus_fallback,
            "fuzzy_match": self.fuzzy_match,
            "matched_name": self.matched_name,
            "confidence": self.confidence.value,
        }
