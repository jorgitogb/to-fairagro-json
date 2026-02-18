# RO-Crate and Schema.org to Dataverse JSON Converter

A modular Python tool to convert ARC RO-Crates and Schema.org JSON-LD metadata into Dataverse-compatible JSON, following the FAIRagro specification and UC13 instructions.

## Quick Start

The main entry point is `main.py`. You can run it using `uv`:

```bash
# Convert RO-Crate metadata or directory
uv run python main.py data/bonares-arccrate.json --type rocrate

# Convert Schema.org JSON-LD
uv run python main.py data/bonares-jsonld.json --type schemaorg

# Specify custom output path
uv run python main.py data/edal-jsonld.json --type schemaorg --output output/my_result.json
```

## Features

- **Multi-format Support**: Handles both RO-Crate (direct metadata or directories) and Schema.org JSON-LD.
- **Semantic Mapping**: Implemented mapping for **Citation** (including keywords and IDs), **Crop**, **Sensor**, and **Geospatial** blocks.
- **Entity Resolution**: Robustly resolves references between entities (e.g., mapping Authors to Organizations/People).
- **Deduplication**: Automatically deduplicates authors, crops, and sensors while maintaining affiliation context.
- **Output Management**: Automatically creates an `output/` directory and generates descriptive filenames based on the input.

## Features & Mapping Details

### Citation Block

- **Title/Description**: Extracted from the root dataset.
- **Authors**: Resolved from `creator`/`author` with full affiliation mapping.
- **Contacts**: Dynamically extracted from `contactPoint` or `creator` email/name.
- **Identifiers**: Parses and classifies `identifier` fields (DOI vs. Other).
- **Keywords**: Handles both comma-separated strings and list formats.

### Geospatial Block

- Extracts `spatialCoverage` bounding boxes (`westLongitude`, `eastLongitude`, `northLatitude`, `southLatitude`).

### Crop and Sensor Blocks

- Implements the UC13 ARC logic by parsing `LabProcess` and `Sample` entities.
- Maps `additionalProperty` (Organism, Infection Taxon, Drone Manufacturer, etc.) to specific metadata fields.

## Project Structure

The tool is organized as a modular Python package `to_dataverse_json`:

- `loader.py`: Handles fetching and initial processing of metadata sources.
- `blocks/`: Contains specialized parsers for each Dataverse metadata block.
- `utils.py`: Shared utilities for entity resolution and deep value extraction.
- `converter.py`: Orchestrator class that manages the conversion pipeline.

## Requirements

- Python 3.12+
- `uv` for dependency management
- Dependencies: `rocrate`, `pyld`
