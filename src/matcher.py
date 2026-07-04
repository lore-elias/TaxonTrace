"""String matching utilities and a taxonomic panel matcher."""

from __future__ import annotations

from typing import Iterable

from .models import MatchConfidence, PanelMatchResult, TaxonRecord
from .normalization import extract_genus, normalize_name, normalize_names

try:
    from rapidfuzz.distance import Levenshtein
except ImportError:  # pragma: no cover - fallback for minimal environments
    Levenshtein = None


def _distance(query: str, candidate: str) -> int:
    if Levenshtein is not None:
        return int(Levenshtein.distance(query, candidate))
    if query == candidate:
        return 0
    if not query:
        return len(candidate)
    if not candidate:
        return len(query)

    # Lightweight fallback for environments without rapidfuzz.
    previous_row = list(range(len(candidate) + 1))
    for i, query_char in enumerate(query):
        current_row = [i + 1]
        for j, candidate_char in enumerate(candidate):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (query_char != candidate_char)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def fuzzy_match(query: str, candidates: Iterable[str], max_distance: int = 2) -> tuple[bool, str | None]:
    """Return a close match from a set of candidates using rapidfuzz when available."""
    candidate_list = {normalize_name(candidate) for candidate in candidates if candidate}
    normalized_query = normalize_name(query)
    if not normalized_query or not candidate_list:
        return False, None

    best_match: str | None = None
    best_distance = max_distance + 1

    for candidate in candidate_list:
        distance = _distance(normalized_query, candidate)
        if distance <= max_distance and distance < best_distance:
            best_distance = distance
            best_match = candidate

    return best_match is not None, best_match


class PanelMatcher:
    """Match a user-provided organism name against a known reference panel."""

    def __init__(
        self,
        reported_names: Iterable[str] | None = None,
        bacterial_genera: Iterable[str] | None = None,
        viral_genera: Iterable[str] | None = None,
        use_fuzzy: bool = True,
        max_edit_distance: int = 2,
    ) -> None:
        self.reported_names = normalize_names(reported_names or [])
        self.bacterial_genera = normalize_names(bacterial_genera or [])
        self.viral_genera = normalize_names(viral_genera or [])
        self.use_fuzzy = use_fuzzy
        self.max_edit_distance = max_edit_distance

    def match_name(self, name: str, taxon: TaxonRecord | None = None) -> PanelMatchResult:
        normalized = normalize_name(name)
        if normalized in self.reported_names:
            return PanelMatchResult(matched=True, confidence=MatchConfidence.EXACT, matched_name=name)

        if taxon is not None:
            taxon_normalized = normalize_name(taxon.name)
            if taxon_normalized in self.reported_names:
                return PanelMatchResult(matched=True, confidence=MatchConfidence.TAXID, matched_name=taxon.name)

            genus = extract_genus(taxon.name)
            if genus and genus in self._target_genera(taxon):
                return PanelMatchResult(
                    matched=False,
                    genus_fallback=True,
                    matched_name=genus,
                    confidence=MatchConfidence.GENUS,
                )

        genus = extract_genus(name)
        if genus and genus in self.bacterial_genera.union(self.viral_genera):
            return PanelMatchResult(
                matched=False,
                genus_fallback=True,
                matched_name=genus,
                confidence=MatchConfidence.GENUS,
            )

        if self.use_fuzzy:
            matched, best = fuzzy_match(normalized, self.reported_names, self.max_edit_distance)
            if matched:
                return PanelMatchResult(
                    matched=False,
                    fuzzy_match=best,
                    matched_name=best,
                    confidence=MatchConfidence.FUZZY,
                )

        return PanelMatchResult(matched=False, confidence=MatchConfidence.NONE)

    def _target_genera(self, taxon: TaxonRecord) -> set[str]:
        if normalize_name(taxon.name) in self.viral_genera:
            return self.viral_genera
        return self.bacterial_genera
