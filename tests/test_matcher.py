from taxonomy_resolver.models import MatchConfidence, TaxonRecord
from taxonomy_resolver.matcher import PanelMatcher
from taxonomy_resolver.extract import TaxonomyResolver
from taxonomy_resolver import normalize_name


class FakeProvider:
    def fetch_taxon(self, taxid: str) -> TaxonRecord | None:
        if taxid == "562":
            return TaxonRecord(
                taxid="562",
                name="Escherichia coli",
                rank="species",
                lineage=[
                    {"taxid": "2", "name": "Bacteria", "rank": "superkingdom"},
                    {"taxid": "1224", "name": "Proteobacteria", "rank": "phylum"},
                    {"taxid": "543", "name": "Enterobacterales", "rank": "order"},
                    {"taxid": "561", "name": "Escherichia", "rank": "genus"},
                    {"taxid": "562", "name": "Escherichia coli", "rank": "species"},
                ],
                synonyms=["Bacterium coli"],
                historical_names=["Bacillus coli"],
            )
        return None


def test_panel_matcher_exact_reported_name():
    matcher = PanelMatcher(reported_names={"escherichia coli"})
    result = matcher.match_name("Escherichia coli")
    assert result.matched is True
    assert result.confidence == MatchConfidence.EXACT


def test_panel_matcher_uses_fuzzy_fallback():
    matcher = PanelMatcher(reported_names={"escherichia coli"})
    result = matcher.match_name("escherichia colli")
    assert result.matched is False
    assert result.confidence == MatchConfidence.FUZZY


def test_taxonomy_resolver_resolves_taxid_via_provider():
    resolver = TaxonomyResolver(provider=FakeProvider())
    record = resolver.resolve_taxid("562")
    assert record is not None
    assert record.name == "Escherichia coli"
    assert record.ancestor_by_rank("genus") is not None


def test_normalize_name_handles_taxonomic_qualifiers():
    assert normalize_name("Escherichia coli subsp. enterica") == "escherichia coli subsp enterica"
