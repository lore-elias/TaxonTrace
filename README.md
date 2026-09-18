# TaxonTrace

A lightweight Python toolkit for resolving taxonomic names and identifiers across heterogeneous metadata sources. The package is designed for bioinformatics workflows that require consistent taxonomic normalization, lineage retrieval, and fuzzy name matching.

## Why this package exists

Taxonomic metadata are often inconsistent across sequence repositories: organism names may vary in spelling, abbreviations may differ, and ranks may be reported with inconsistent terminology. This package provides a simple abstraction for resolving such metadata into a normalized representation that can be used downstream in pathogen identification, reference annotation, and taxonomic comparison workflows.

## Features

- Resolve NCBI Taxonomy identifiers into structured taxonomy records
- Retrieve taxonomic lineage information for a given taxid
- Normalize taxonomic names for consistent comparison
- Match reported names against a known reference panel
- Use fuzzy matching when exact matches are unavailable
- Persist cached taxonomy results locally in JSON format
- Provide a provider-based architecture for future taxonomy sources

---

## Installation

```bash
pip install taxonomy-resolver
```

For local development:

```bash
git clone https://github.com/lore-elias/taxonomy_resolver.git
cd taxonomy_resolver
pip install -e ".[dev]"
```

---

## Quick start

### Resolve a taxid

```python
from taxonomy_resolver import TaxonomyResolver, NCBITaxonomyProvider

provider = NCBITaxonomyProvider(email="your.email@example.com")
resolver = TaxonomyResolver(provider=provider)

record = resolver.resolve_taxid("562")

print(record.name)
print(record.rank)
print(record.lineage)
```

### Match a reported organism name

```python
from taxonomy_resolver import PanelMatcher

matcher = PanelMatcher(
    reported_names={
        "Escherichia coli",
        "Staphylococcus aureus",
    }
)

result = matcher.match_name("Escherichia colli")
print(result.confidence)
print(result.matched_name)
```

### Normalize a name

```python
from taxonomy_resolver import normalize_name

normalize_name("Escherichia coli (strain K12)")
# 'escherichia coli strain k12'
```

---

## Package structure

```text
taxonomy_resolver/
├── __init__.py
├── cache.py
├── extract.py
├── lineage.py
├── matcher.py
├── models.py
├── normalization.py
├── providers.py
└── ...
```

### Core components

#### TaxonomyResolver
High-level entry point for resolving taxids and matching names.

#### NCBITaxonomyProvider
NCBI-backed provider using Biopython Entrez to fetch taxonomy records.

#### TaxonomyLineageFetcher
Fetches and caches taxonomy records through the selected provider.

#### PanelMatcher
Matches reported names against a reference panel using exact, genus-based, and fuzzy matching logic.

#### TaxonRecord
Normalized representation of a resolved taxon with taxid, scientific name, rank, lineage, and metadata.

---

## Architecture

```text
TaxonomyResolver
    ├── TaxonomyLineageFetcher
    │   └── TaxonomyProvider
    │       └── NCBITaxonomyProvider
    │           └── NCBI Entrez
    └── PanelMatcher
```

The design intentionally separates taxonomy retrieval, normalization, and matching so that new providers can be added without changing the public API.

---

## Development

Run the tests:

```bash
pytest
```

Or collect coverage:

```bash
pytest --cov=src
```

---

## Roadmap

Planned improvements include:

- additional taxonomy providers such as GTDB and ICTV
- batch resolution of multiple taxids
- improved normalization rules for strain and cultivar names
- CLI support for command-line use
- extended cache strategies and persistence options

---

## Contributing

Contributions are welcome. If you find a bug or want to propose an enhancement, please open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License.
