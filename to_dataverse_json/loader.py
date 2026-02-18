import json
from pathlib import Path
from rocrate.rocrate import ROCrate

class MetadataLoader:
    @staticmethod
    def load(path, input_type):
        """Loads entities based on input type."""
        if input_type == 'rocrate':
            return MetadataLoader.load_rocrate(path)
        elif input_type == 'schemaorg':
            return MetadataLoader.load_schemaorg(path)
        else:
            raise ValueError(f"Unknown input type: {input_type}")

    @staticmethod
    def load_rocrate(path):
        """Loads entities from an RO-Crate directory or metadata file."""
        input_path = Path(path)
        if input_path.is_file():
            return MetadataLoader.load_schemaorg(path)
        else:
            crate = ROCrate(path)
            return list(crate.entities)

    @staticmethod
    def load_schemaorg(path):
        """Loads Schema.org JSON-LD and flattens it if it has a @graph."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if '@graph' in data:
            return data['@graph']
        else:
            return [data]
