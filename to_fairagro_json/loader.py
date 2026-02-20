import json
from pathlib import Path
from pyld import jsonld

class DocumentLoader:
    @staticmethod
    def load_json(data):
        if isinstance(data, (str, Path)):
            with open(data, 'r', encoding='utf-8') as f:
                return json.load(f)
        return data

    @staticmethod
    def custom_document_loader(url, options={}):
        """Handles common contexts offline or using local fallbacks."""
        standard_ctx = {
            "@context": {
                "@vocab": "https://schema.org/",
                "schema": "https://schema.org/",
                "Dataset": "https://schema.org/Dataset"
            }
        }
        if "schema.org" in url or "w3id.org/ro/crate" in url:
            return {
                'contextUrl': None,
                'documentUrl': url,
                'document': standard_ctx
            }
        return jsonld.get_document_loader()(url)

    @staticmethod
    def normalize_schema(obj):
        """Ensures consistent https usage for schema.org terms."""
        if isinstance(obj, list):
            return [DocumentLoader.normalize_schema(i) for i in obj]
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                new_k = k.replace("http://schema.org/", "https://schema.org/")
                new_obj[new_k] = DocumentLoader.normalize_schema(v)
            return new_obj
        if isinstance(obj, str):
            return obj.replace("http://schema.org/", "https://schema.org/")
        return obj

    @classmethod
    def frame_data(cls, data, frame):
        """Expands, normalizes, and frames the input data."""
        data = cls.load_json(data)
        
        try:
            expanded = jsonld.expand(data, options={'documentLoader': cls.custom_document_loader})
        except Exception:
            # Fallback for inaccessible contexts
            if isinstance(data, list): expanded = data
            elif isinstance(data, dict) and "@graph" in data: expanded = data["@graph"]
            else: expanded = [data]
            
        expanded = cls.normalize_schema(expanded)
        
        # Flatten graph if necessary
        if isinstance(expanded, list) and len(expanded) == 1 and "@graph" in expanded[0]:
            expanded = expanded[0]["@graph"]
            
        framed = jsonld.frame(expanded, frame)
        entities = framed.get('@graph', [framed])
        if not isinstance(entities, list): entities = [entities]
        return entities
