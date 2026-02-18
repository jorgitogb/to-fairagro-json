import json
from pathlib import Path
from .loader import MetadataLoader
from .blocks.citation import CitationParser
from .blocks.crop import CropParser
from .blocks.sensor import SensorParser
from .blocks.geospatial import GeospatialParser

class DataverseConverter:
    def __init__(self):
        self.entities = []

    def load(self, path, input_type):
        """Loads entities using the MetadataLoader."""
        self.entities = MetadataLoader.load(path, input_type)

    def convert(self, output_path):
        """Converts entities to Dataverse JSON and writes to output_path."""
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        dataverse_json = {
            "datasetVersion": {
                "metadataBlocks": {
                    "citation": CitationParser.parse(self.entities),
                    "crop": CropParser.parse(self.entities),
                    "sensor": SensorParser.parse(self.entities),
                    "geospatial": GeospatialParser.parse(self.entities)
                }
            }
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataverse_json, f, indent=2)
        return dataverse_json
