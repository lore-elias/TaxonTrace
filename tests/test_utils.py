from taxonomy_resolver.matcher import fuzzy_match
from taxonomy_resolver.normalization import extract_genus, normalize_name


def test_normalize_name_strips_punctuation():
    assert normalize_name("Escherichia coli (strain K12)") == "escherichia coli strain k12"


def test_extract_genus_returns_first_token():
    assert extract_genus("Staphylococcus aureus") == "staphylococcus"


def test_fuzzy_match_returns_close_candidate():
    matched, best = fuzzy_match("staphylococcus aureus", {"staphylococcus aureus", "escherichia coli"})
    assert matched is True
    assert best == "staphylococcus aureus"
