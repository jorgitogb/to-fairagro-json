import json
import yaml
from pathlib import Path
from pyld import jsonld

class DataverseConverter:
    def __init__(self, frame_path=None, mapping_path=None):
        base_path = Path(__file__).parent.parent
        self.frame_path = frame_path or base_path / 'config' / 'frame.json'
        self.mapping_path = mapping_path or base_path / 'config' / 'mapping.yaml'
        
        with open(self.frame_path, 'r') as f:
            self.frame = json.load(f)
        with open(self.mapping_path, 'r') as f:
            self.mapping = yaml.safe_load(f)
        self.entities = []

    def load(self, data):
        """Loads and frames the input data."""
        if isinstance(data, (str, Path)):
            with open(data, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        # Custom document loader to handle common contexts offline
        def custom_loader(url, options={}):
            # Basic context for schema.org and ro-crate
            standard_ctx = {
                "@context": {
                    "@vocab": "https://schema.org/",
                    "schema": "https://schema.org/",
                    "Dataset": "https://schema.org/Dataset"
                }
            }
            # Catch all schema.org and ro-crate URLs
            if "schema.org" in url or "w3id.org/ro/crate" in url:
                return {
                    'contextUrl': None,
                    'documentUrl': url,
                    'document': standard_ctx
                }
            # Default to pyld's default loader
            return jsonld.get_document_loader()(url)

        try:
            # Expand ensures all terms are absolute URIs
            expanded = jsonld.expand(data, options={'documentLoader': custom_loader})
        except Exception as e:
            # Fallback for very malformed or inaccessible contexts: treat as expanded if possible
            if isinstance(data, list): expanded = data
            elif isinstance(data, dict) and "@graph" in data: expanded = data["@graph"]
            else: expanded = [data]
        
        # Normalize http to https for schema.org URIs
        def normalize_schema(obj):
            if isinstance(obj, list):
                return [normalize_schema(i) for i in obj]
            if isinstance(obj, dict):
                new_obj = {}
                for k, v in obj.items():
                    new_k = k.replace("http://schema.org/", "https://schema.org/")
                    new_obj[new_k] = normalize_schema(v)
                return new_obj
            if isinstance(obj, str):
                return obj.replace("http://schema.org/", "https://schema.org/")
            return obj

        expanded = normalize_schema(expanded)

        # RO-Crates often nest everything under @graph
        if isinstance(expanded, list) and len(expanded) == 1 and "@graph" in expanded[0]:
            expanded = expanded[0]["@graph"]

        # Framing normalizes the graph into a tree structure
        self.framed = jsonld.frame(expanded, self.frame)
        self.entities = self.framed.get('@graph', [self.framed])
        if not isinstance(self.entities, list): self.entities = [self.entities]
        
        # Filter only Datasets
        def is_dataset(e):
            etype = e.get('@type', [])
            if isinstance(etype, str): etype = [etype]
            return any('Dataset' in t for t in etype)

        self.entities = [e for e in self.entities if is_dataset(e)]

    def _get_nested(self, data, path):
        """Helper to get value from nested dict using dot notation."""
        parts = path.split('.')
        for part in parts:
            if isinstance(data, dict):
                data = data.get(part)
            elif isinstance(data, list) and data:
                data = data[0].get(part) if isinstance(data[0], dict) else None
            else:
                return None
        return data

    def _resolve_source(self, entity, sources):
        for source in sources:
            val = self._get_nested(entity, source)
            if val:
                return val
        return None

    def convert(self, output_path=None):
        output_results = []
        for entity in self.entities:
            blocks = {}
            for block_name, block_cfg in self.mapping.get('blocks', {}).items():
                fields = []
                for field_cfg in block_cfg.get('fields', []):
                    field_name = list(field_cfg.keys())[0]
                    cfg = field_cfg[field_name]
                    
                    val = None
                    if 'source' in cfg:
                        val = self._resolve_source(entity, cfg['source'])
                    
                    if not val and 'default' in cfg:
                        val = cfg['default']

                    if val:
                        fields.append(self._format_field(field_name, val, cfg))
                
                blocks[block_name] = {
                    "displayName": block_cfg.get("displayName", block_name),
                    "fields": fields
                }
            
            dv_json = {
                "datasetVersion": {
                    "metadataBlocks": blocks
                }
            }
            output_results.append(dv_json)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_results, f, indent=2)
                
        return output_results

    def _format_field(self, name, val, cfg):
        ftype = cfg.get('type', 'single')
        
        def _get_literal(v):
            if isinstance(v, dict) and '@value' in v:
                return v['@value']
            return v

        if ftype == 'single':
            return {name: {"value": str(_get_literal(val))}}
        
        if ftype == 'list':
            item_key = cfg.get('item_key', 'value')
            if isinstance(val, str):
                vals = [v.strip() for v in val.split(',')]
            elif isinstance(val, list):
                vals = val
            else:
                vals = [val]
            
            vals = [_get_literal(v) for v in vals]
            flat_vals = []
            for v in vals:
                if isinstance(v, list):
                    flat_vals.extend(v)
                else: 
                    flat_vals.append(v)
            
            return {name: [{item_key: {"value": str(v)}} for v in flat_vals]}

        if ftype == 'complex_list':
            items = []
            if not isinstance(val, list): val = [val]
            for item in val:
                sub_fields = {}
                for sub_name, sub_sources in cfg.get('mapping', {}).items():
                    sub_val = self._resolve_source(item, sub_sources)
                    if sub_val:
                        sub_fields[sub_name] = {"value": str(_get_literal(sub_val))}
                if sub_fields:
                    items.append(sub_fields)
            return {name: items}

        return {name: {"value": str(_get_literal(val))}}
