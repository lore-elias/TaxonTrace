"""Provider interfaces and an NCBI-backed implementation."""

from __future__ import annotations

import time
from typing import Protocol

from Bio import Entrez

from .models import TaxonRecord


class TaxonomyResolutionError(RuntimeError):
    """Raised when a taxonomy provider cannot resolve a record."""


class TaxonomyProvider(Protocol):
    """Protocol for providers that can resolve a taxon by taxid."""

    def fetch_taxon(self, taxid: str) -> TaxonRecord | None:
        """Return a serialized taxon record for the given taxid."""


class NCBITaxonomyProvider:
    """NCBI taxonomy provider using Entrez EFetch."""

    def __init__(
        self,
        email: str | None = None,
        api_key: str | None = None,
        batch_delay: float = 0.35,
        rate_limit_delay: float = 0.35,
        timeout: int = 30,
    ) -> None:
        self.batch_delay = batch_delay
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        if email:
            Entrez.email = email
        if api_key:
            Entrez.api_key = api_key

    def fetch_taxon(self, taxid: str) -> TaxonRecord | None:
        if not taxid or str(taxid) in {"0", "None"}:
            return None

        try:
            time.sleep(self.rate_limit_delay)
            handle = Entrez.efetch(db="taxonomy", id=str(taxid), retmode="xml")
            record = Entrez.read(handle)
            handle.close()
        except Exception as exc:  # pragma: no cover - depends on network availability
            raise TaxonomyResolutionError(f"Unable to fetch taxon {taxid}: {exc}") from exc

        if not record or not record[0]:
            return None

        node = record[0]
        scientific_name = str(node.get("ScientificName", "") or "")
        rank = str(node.get("Rank", "") or "")
        lineage: list[dict[str, str]] = []
        for entry in node.get("LineageEx", []) or []:
            lineage.append(
                {
                    "taxid": str(entry.get("TaxId", "") or ""),
                    "name": str(entry.get("ScientificName", "") or ""),
                    "rank": str(entry.get("Rank", "") or ""),
                }
            )

        if scientific_name and not any(item.get("taxid") == str(taxid) for item in lineage):
            lineage.append({"taxid": str(taxid), "name": scientific_name, "rank": rank})

        synonyms = [str(name) for name in node.get("OtherNames", {}).get("Synonym", []) or []]
        historical_names = [str(name) for name in node.get("OtherNames", {}).get("Name", []) or []]

        return TaxonRecord(
            taxid=str(taxid),
            name=scientific_name,
            rank=rank,
            lineage=lineage,
            synonyms=synonyms,
            historical_names=historical_names,
            provider="ncbi",
            metadata={"source": "ncbi"},
        )
