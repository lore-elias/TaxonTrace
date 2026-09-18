from pathlib import Path

from taxonomy_resolver.cache import JsonTaxidCache
from taxonomy_resolver.extract import TaxonomyResolver
from taxonomy_resolver.matcher import PanelMatcher
from taxonomy_resolver.models import MatchConfidence, TaxonRecord
from taxonomy_resolver.normalization import normalize_name

from tests.mock_data import MOCK_TAXA


class MockTaxonomyProvider:
    def fetch_taxon(self, taxid: str) -> TaxonRecord | None:
        payload = MOCK_TAXA.get(str(taxid))
        if payload is None:
            return None
        return TaxonRecord.from_dict(payload)


def test_taxon_record_round_trip_serialization():
    record = TaxonRecord.from_dict(MOCK_TAXA["562"])
    recreated = TaxonRecord.from_dict(record.to_dict())

    assert recreated.taxid == "562"
    assert recreated.name == "Escherichia coli"
    assert recreated.ancestor_by_rank("genus")["name"] == "Escherichia"


def test_cache_stores_and_reads_taxa(tmp_path: Path):
    cache = JsonTaxidCache(tmp_path / "taxon_cache.json")
    cache.set("562", MOCK_TAXA["562"])
    cache.save()

    reloaded = JsonTaxidCache(tmp_path / "taxon_cache.json")
    assert reloaded.get("562")["name"] == "Escherichia coli"


def test_taxonomy_resolver_uses_mock_provider_and_returns_lineage():
    resolver = TaxonomyResolver(provider=MockTaxonomyProvider())
    record = resolver.resolve_taxid("1280")

    assert record is not None
    assert record.rank == "species"
    assert record.ancestor_by_rank("family")["name"] == "Staphylococcaceae"


def test_panel_match_uses_taxid_based_resolution_case():
    resolver = TaxonomyResolver(
        provider=MockTaxonomyProvider(),
        matcher=PanelMatcher(reported_names={"escherichia coli"}),
    )
    result = resolver.match_name("escherichia coli strain k12", taxon=resolver.resolve_taxid("562"))

    assert result.matched is True
    assert result.confidence == MatchConfidence.TAXID


def test_normalize_name_keeps_key_taxonomic_tokens():
    assert normalize_name("Escherichia coli subsp. enterica") == "escherichia coli subsp enterica"
    assert normalize_name("Staphylococcus aureus") == "staphylococcus aureus"
