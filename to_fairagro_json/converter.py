import json
import yaml
from pathlib import Path
from .loader import DocumentLoader
from .mapper import MetadataMapper


class FairagroConverter:
    def __init__(self, profile="schemaorg", target="fairagro"):
        base_path = Path(__file__).parent.parent
        self.profile = profile
        self.target = target

        self.config_dir = base_path / "config"
        self.frame_path = self.config_dir / profile / "frame.json"
        self.mapping_path = self.config_dir / target / "mapping.yaml"

        # Ensure config files exist
        if not self.frame_path.exists():
            raise FileNotFoundError(f"Frame not found: {self.frame_path}")
        if not self.mapping_path.exists():
            raise FileNotFoundError(f"Mapping not found: {self.mapping_path}")

        with open(self.frame_path, "r", encoding="utf-8") as f:
            self.frame = json.load(f)
        with open(self.mapping_path, "r", encoding="utf-8") as f:
            self.mapping = yaml.safe_load(f)

        self.entities = []
        self.mapper = MetadataMapper(self.mapping, all_entities=self.entities)

    def load(self, data):
        """Loads and frames the input data using DocumentLoader."""
        self.entities = DocumentLoader.frame_data(data, self.frame)
        self.mapper.all_entities = self.entities

        # Filter only Datasets
        def is_dataset(e):
            etype = e.get("@type", [])
            if isinstance(etype, str):
                etype = [etype]
            return any("Dataset" in t for t in etype)

        self.entities = [e for e in self.entities if is_dataset(e)]

        # Prioritize Investigation over Study/Assay
        def get_rank(e):
            atype = e.get("additionalType", [])
            if isinstance(atype, str):
                atype = [atype]
            if "Investigation" in atype:
                return 0
            if "Study" in atype:
                return 1
            if "Assay" in atype:
                return 2
            return 3

        self.entities.sort(key=get_rank)

    def convert(self, output_path=None):
        """Orchestrates the conversion of all entities to FAIRagro Core Spec.

        - If the input has an ARC Investigation hierarchy, outputs a single JSON object.
        - If the input is a flat list of independent datasets, outputs a JSON array.
        """
        # Check if any entity is ARC-typed (Investigation/Study/Assay)
        has_arc_hierarchy = any(
            atype in str(e.get("additionalType", ""))
            for e in self.entities
            for atype in ["Investigation", "Study", "Assay"]
        )

        output_results = []
        if has_arc_hierarchy:
            # For ARC inputs: only map the primary entity (Investigation or first)
            primary = self.entities[0]
            blocks = self.mapper.map_entity(primary)
            if blocks:
                output_results.append(blocks)
        else:
            # For flat inputs (Schema.org arrays): map each entity independently
            for entity in self.entities:
                # Give mapper a single-entity view so extraction is scoped to this dataset
                single_mapper = MetadataMapper(self.mapping, all_entities=[entity])
                blocks = single_mapper.map_entity(entity)
                if blocks:
                    output_results.append(blocks)

        if not output_results:
            return None

        # Return array for multiple independent datasets, single object for ARC
        final_output = output_results[0] if len(output_results) == 1 else output_results

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(final_output, f, indent=2)

        return final_output
