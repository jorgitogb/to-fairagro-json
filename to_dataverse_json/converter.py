import json
import yaml
from pathlib import Path
from .loader import DocumentLoader
from .mapper import MetadataMapper


class DataverseConverter:
    def __init__(self, profile="schemaorg", target="dataverse"):
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

        dataset_entities = [e for e in self.entities if is_dataset(e)]
        
        # In RO-Crate, there's usually a Root Dataset and multiple sub-datasets.
        # We try to identify the Root Dataset to use as the primary entity
        self.root_entity = None
        if dataset_entities:
            # If the profile is rocrate, the root dataset often has hasPart
            root_candidates = [e for e in dataset_entities if "hasPart" in e]
            if root_candidates:
                self.root_entity = root_candidates[0]
            else:
                self.root_entity = dataset_entities[0]

    def convert(self, output_path=None):
        """Orchestrates the conversion of the root entity."""
        output_results = []
        if self.root_entity:
            blocks = self.mapper.map_entity(self.root_entity)
            if blocks:
                dv_json = {"datasetVersion": {"metadataBlocks": blocks}}
                output_results = [dv_json]

        if output_path and output_results:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_results, f, indent=2)

        return output_results
