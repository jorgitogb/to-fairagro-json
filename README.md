# RO-Crate and Schema.org to Dataverse JSON Converter

A modular Python tool to convert ARC RO-Crates and Schema.org JSON-LD metadata into Dataverse-compatible JSON, following the FAIRagro specification and UC13 instructions.

## Quick Start

The main entry point is `main.py`. You can run it using `uv`:

```bash
# Convert RO-Crate metadata
uv run python main.py data/bonares-arccrate.json --type rocrate

# Convert Schema.org JSON-LD
uv run python main.py data/bonares-jsonld.json --type schemaorg

# Convert large Schema.org collections (e.g., Publisso)
uv run python main.py data/publisso-schemaorg.json --type schemaorg
```

## Features

- **Semantic Normalization**: Uses `pyld` for robust JSON-LD framing and expansion, ensuring consistent extraction across diverse sources.
- **Profile-Based Mapping**: Declarative YAML profiles define mappings for different metadata standards (RO-Crate, Schema.org).
- **Advanced Field Handling**:
  - **Citation**: Deep extraction of authors, affiliations, identifiers (DOIs), and keywords.
  - **Geospatial**: Robust regex-based extraction of bounding box coordinates (`west`, `east`, `north`, `south`).
  - **FAIRagro Blocks**: Maps specific metadata to FAIRagro `Crop` and `Sensor` blocks.
- **Recursive Literal Extraction**: Handles nested JSON-LD values, including language-tagged strings and Person name components (`givenName`/`familyName`).
- **Output Management**: Automatically generates Dataverse-compatible JSON in the `output/` directory.

## Project Structure

The tool is organized as a modular Python package `to_dataverse_json`:

- `loader.py`: Handles fetching and initial processing of metadata sources.
- `converter.py`: Orchestrator class that manages the conversion pipeline using JSON-LD framing.
- `config/`: Contains JSON-LD frames and YAML mapping profiles for each supported type.
- `output/`: Successfully converted samples are stored here.

## JSON-LD Core Concepts

This tool relies on two powerful JSON-LD features to normalize diverse metadata:

### 1. Expansion

JSON-LD data can come in many shapes. **Expansion** converts it into a canonical, "verbose" form where every property is a full URI. This removes ambiguity caused by different `@context` definitions.

**Before:**

```json
{ "@context": "https://schema.org", "@type": "Dataset", "name": "Study A" }
```

**Expanded (Canonical):**

```json
[
  {
    "@type": ["https://schema.org/Dataset"],
    "https://schema.org/name": [{ "@value": "Study A" }]
  }
]
```

### 2. Framing

Once expanded, we use **Framing** to re-shape the graph into a predictable tree structure defined in `config/<profile>/frame.json`. This ensures that even if a property was deeply nested or linked by ID in the source, it always appears at the same path in our "Framed" result.

**Framed Result (Ready for Mapping):**

```json
{ "@type": "Dataset", "name": "Study A", "creator": [...] }
```

## Profiles & Mapping

Mappings are defined in `config/` and handle standard Dataverse metadata blocks:

- **Citation Metadata**: Title, authors, description, keywords, publication date, etc.
- **Geospatial Metadata**: Bounding boxes for spatial coverage.
- **FAIRagro Metadata**: Specialized blocks for agricultural data (Crops, Sensors).

## Requirements

- Python 3.12+
- `uv` for dependency management
- Dependencies: `pyld`, `pyyaml`

## Verification

The converter has been verified against multiple real-world samples:

- `bonares-schemaorg.json` (Schema.org)
- `bonares-arccrate.json` (RO-Crate)
- `edal-schemaorg.json` (Schema.org)
- `publisso-schemaorg.json` (Schema.org)
