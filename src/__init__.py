"""Public package interface for the taxonomy resolver."""

from .extract import TaxonomyResolver
from .matcher import PanelMatcher, fuzzy_match
from .models import MatchConfidence, PanelMatchResult, TaxonRecord
from .normalization import extract_genus, normalize_name
from .providers import NCBITaxonomyProvider, TaxonomyProvider, TaxonomyResolutionError

__all__ = [
    "MatchConfidence",
    "NCBITaxonomyProvider",
    "PanelMatchResult",
    "PanelMatcher",
    "TaxonRecord",
    "TaxonomyProvider",
    "TaxonomyResolutionError",
    "TaxonomyResolver",
    "extract_genus",
    "fuzzy_match",
    "normalize_name",
]
