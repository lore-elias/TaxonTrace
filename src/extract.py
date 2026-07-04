"""High-level taxonomy resolution facade."""

from __future__ import annotations

from .lineage import TaxonomyLineageFetcher
from .matcher import PanelMatcher
from .models import PanelMatchResult, TaxonRecord
from .providers import TaxonomyProvider


class TaxonomyResolver:
    """Main high-level API for resolving taxonomy records and matching names."""

    def __init__(
        self,
        provider: TaxonomyProvider | None = None,
        lineage_fetcher: TaxonomyLineageFetcher | None = None,
        matcher: PanelMatcher | None = None,
    ) -> None:
        self.lineage_fetcher = lineage_fetcher or TaxonomyLineageFetcher(provider=provider)
        self.matcher = matcher or PanelMatcher()

    def resolve_taxid(self, taxid: str) -> TaxonRecord | None:
        """Resolve a taxid into a canonical TaxonRecord."""
        return self.lineage_fetcher.fetch_taxid_record(taxid)

    def resolve_name(self, name: str, taxon: TaxonRecord | None = None) -> PanelMatchResult:
        """Resolve a name using the configured matching logic."""
        return self.match_name(name, taxon=taxon)

    def match_name(self, name: str, taxon: TaxonRecord | None = None) -> PanelMatchResult:
        """Match a reported name against the configured panel."""
        return self.matcher.match_name(name, taxon=taxon)
