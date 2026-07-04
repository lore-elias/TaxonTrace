"""High-level lineage fetching wrapper with caching."""

from __future__ import annotations

from pathlib import Path

from .cache import JsonTaxidCache
from .models import TaxonRecord
from .providers import NCBITaxonomyProvider, TaxonomyProvider, TaxonomyResolutionError


class TaxonomyLineageFetcher:
    """Fetch and cache taxonomy records using a provider abstraction."""

    def __init__(
        self,
        cache_path: str | Path = "data/taxon_cache.json",
        provider: TaxonomyProvider | None = None,
        cache: JsonTaxidCache | None = None,
        email: str | None = None,
        api_key: str | None = None,
        batch_delay: float = 0.35,
        rate_limit_delay: float = 0.35,
        raise_on_error: bool = False,
    ) -> None:
        self.cache = cache or JsonTaxidCache(cache_path)
        self.provider = provider or NCBITaxonomyProvider(
            email=email,
            api_key=api_key,
            batch_delay=batch_delay,
            rate_limit_delay=rate_limit_delay,
        )
        self.raise_on_error = raise_on_error

    def fetch_taxid_record(self, taxid: str) -> TaxonRecord | None:
        if not taxid or str(taxid) in {"0", "None"}:
            return None

        cached = self.cache.get(str(taxid))
        if cached:
            return TaxonRecord.from_dict(cached)

        try:
            record = self.provider.fetch_taxon(str(taxid))
        except TaxonomyResolutionError:
            if self.raise_on_error:
                raise
            return None

        if record is None:
            return None

        self.cache.set(str(taxid), record.to_dict())
        self.cache.save()
        return record
