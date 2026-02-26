# metadata-to-fairagro-json

A modular Python tool to convert ARC RO-Crates and Schema.org JSON-LD metadata into FAIRagro-compliant JSON, following the [FAIRagro Core Metadata Specification](https://fairagro.net).

## Quick Start

The main entry point is `main.py`. You can run it using `uv`:

```bash
# Convert RO-Crate metadata
uv run python main.py data/arc-ro-crate-metadata.json --type rocrate

# Convert Schema.org JSON-LD samples
uv run python main.py data/schemaorg/bonares-schemaorg.json --type schemaorg
uv run python main.py data/schemaorg/thunen-schemaorg.json --type schemaorg
```

To run the full validation suite:

```bash
uv run test_output_all.py
```

## Features

- **Semantic Normalization**: Uses `pyld` for robust JSON-LD framing and expansion, ensuring consistent extraction across diverse sources.
- **FAIRagro Alignment**: Generates flat JSON structures that strictly adhere to the `fairagro-schema.json` specification.
- **Advanced Field Handling**:
  - **Citation**: Automated extraction of authors, affiliations, identifiers, and contacts with robust fallback mechanisms.
  - **Geospatial**: Robust regex-based extraction of bounding box coordinates (`west`, `east`, `north`, `south`).
  - **Domain-Specific**: Maps metadata to FAIRagro `Crop` and `Sensor` blocks.
- **Recursive Literal Extraction**: Handles nested JSON-LD values, including language-tagged strings and Person name components.

## Project Structure

- `main.py`: CLI entry point.
- `to_fairagro_json/`: Core package containing loader, converter, and mapper logic.
- `config/`: JSON-LD frames and YAML mapping profiles.
- `output/`: Successfully converted samples (JSON).
- `data/`: Sample input datasets (RO-Crate and Schema.org).

## Verification

The converter is verified against multiple real-world samples from:

- BonaRes
- EDAL
- Publisso
- Thünen Institute
- ARC RO-Crates

## Requirements

- Python 3.12+
- `uv` for dependency management
- Dependencies: `pyld`, `pyyaml`, `jsonschema`
