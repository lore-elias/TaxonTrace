# Taxonomy Resolver Package

A lightweight Python package for resolving taxonomic names and identifiers, with support for fuzzy matching, synonyms, and historical names. It is designed to be extensible to different taxonomy providers.

The package is designed for bioinformatics workflows that requeire consistent taxonomic handling whilke remaining exdtensible through a provider-based architecture.

## Features

- 🔬 Resolve NCBI Taxonomy IDs into structured taxonomy records
- 🌳 Retrieve complete taxonomic lineages
- 💾 Local JSON caching with optional expiration and versioning
- 🧬 Normalize scientific names for consistent comparisons
- 🔎 Fuzzy matching using `rapidfuzz` (with a lightweight fallback)
- 📚 Support for synonyms and historical taxonomic names
- 🔌 Provider abstraction for future support of databases such as GTDB and ICTV

---

## Usage

```bash
pip install taxonomy-resolver
```

For development:

```bash
git clone https://github.com/lore-elias/Taxonomy-Resolver.git
cd taxonomy-resolver
pip install -e ".[dev]"
```

---

## Quick Start

### Resolve a Taxonomy ID

```python
from taxonomy_resolver import (
    TaxonomyResolver,
    NCBITaxonomyProvider,
)

provider = NCBITaxonomyProvider(
    email="your.email@example.com",
)

resolver = TaxonomyResolver(provider=provider)

record = resolver.resolve_taxid("562")

print(record.name)
print(record.rank)
print(record.lineage)
```

---

### Match organism names

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
```

---

### Normalize names

```python
from taxonomy_resolver import normalize_name

normalize_name("Escherichia coli (strain K12)")
# escherichia coli strain k12
```

---

## Main Components

### TaxonomyResolver

High-level interface for taxonomy resolution.

Responsibilities include:

- resolving TaxIDs
- coordinating taxonomy providers
- integrating lineage fetching and matching

---

### NCBITaxonomyProvider

Retrieves taxonomy records using BioPython's Entrez interface.

Currently supported:

- Scientific name
- Rank
- Complete lineage
- Synonyms
- Historical names

---

### PanelMatcher

Matches organism names against a user-defined reference panel using:

- exact matching
- TaxID-based matching
- genus fallback
- fuzzy matching

---

### TaxonRecord

Represents a resolved taxonomy record.

Includes:

- TaxID
- scientific name
- rank
- lineage
- synonyms
- historical names
- provider metadata

---

## Architecture

```
                TaxonomyResolver
                        │
        ┌───────────────┴───────────────┐
        │                               │
 TaxonomyLineageFetcher           PanelMatcher
        │
 TaxonomyProvider
        │
 NCBITaxonomyProvider
        │
     NCBI Entrez
```

The provider abstraction allows future implementations for additional taxonomy databases without changing the public API.

---

## Running Tests

```bash
pytest
```

or

```bash
pytest --cov=src
```

---

## Roadmap

Planned improvements include:

- GTDB provider
- ICTV provider
- Batch TaxID resolution
- Search by scientific name
- Configurable normalization rules
- Additional cache backends
- Command-line interface

---

## Contributing

Contributions are welcome.

If you encounter a bug or have a feature request, please open an issue or submit a pull request.

---

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
