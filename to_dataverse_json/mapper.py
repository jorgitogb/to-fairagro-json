import re
from .cleaner import StringCleaner

class MetadataMapper:
    def __init__(self, mapping):
        self.mapping = mapping
        self.cleaner = StringCleaner()

    def _get_nested(self, data, path):
        """Helper to get value from nested dict using dot notation."""
        if path == "@": return data
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

    def _get_literal(self, v):
        if v is None:
            return ""
        if isinstance(v, list) and v:
            return self._get_literal(v[0])
            
        if isinstance(v, dict):
            # Handle Schema.org/JSON-LD name/value/literal patterns
            if v.get('@value'): return self._get_literal(v['@value'])
            if v.get('name'): return self._get_literal(v['name'])
            if v.get('value'): return self._get_literal(v['value'])
            # Support Schema.org Person names
            if 'givenName' in v or 'familyName' in v:
                given = self._get_literal(v.get('givenName', ''))
                family = self._get_literal(v.get('familyName', ''))
                full = f"{given} {family}".strip()
                if full: return self.cleaner.clean(full)
        
        if isinstance(v, str):
            return self.cleaner.clean(v)
        return v

    def format_field(self, name, val, cfg):
        ftype = cfg.get('type', 'single')
        
        # Specialized logic for Geo Bounding Boxes
        geo_fields = ['westLongitude', 'eastLongitude', 'northLatitude', 'southLatitude']
        if name in geo_fields:
            lit_val = self._get_literal(val)
            if isinstance(lit_val, (str, bytes)):
                geo_vals = self._parse_geo_box(str(lit_val))
                if geo_vals and name in geo_vals:
                    return {name: {"value": str(geo_vals[name])}}

        if ftype == 'single':
            lit = self._get_literal(val)
            return {name: {"value": str(lit)}}
        
        if ftype == 'list':
            item_key = cfg.get('item_key', 'value')
            if isinstance(val, str):
                vals = [v.strip() for v in val.split(',')]
            elif isinstance(val, list):
                vals = val
            else:
                vals = [val]
            
            items = []
            for v in vals:
                lit = self._get_literal(v)
                if isinstance(lit, list):
                    for item in lit:
                        items.append({item_key: {"value": str(self._get_literal(item))}})
                else:
                    items.append({item_key: {"value": str(lit)}})
            return {name: items}

        if ftype == 'complex_list':
            items = []
            if not isinstance(val, list): val = [val]
            for item in val:
                sub_fields = {}
                for sub_name, sub_sources in cfg.get('mapping', {}).items():
                    sub_val = self._resolve_source(item, sub_sources)
                    if sub_val:
                        sub_fields[sub_name] = {"value": str(self._get_literal(sub_val))}
                if sub_fields:
                    items.append(sub_fields)
            return {name: items}

        return {name: {"value": str(self._get_literal(val))}}

    def _parse_geo_box(self, box_str):
        """Parses a Schema.org box string into a dict using regex."""
        try:
            nums = [float(n) for n in re.findall(r"[-+]?\d*\.?\d+", box_str)]
            if len(nums) >= 4:
                lats = [nums[0], nums[2]]
                lons = [nums[1], nums[3]]
                return {
                    'westLongitude': min(lons),
                    'eastLongitude': max(lons),
                    'northLatitude': max(lats),
                    'southLatitude': min(lats)
                }
        except Exception:
            pass
        return {}

    def map_entity(self, entity):
        """Maps a single entity to Dataverse blocks based on the profile mapping."""
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
                    fields.append(self.format_field(field_name, val, cfg))
            
            if fields:
                blocks[block_name] = {
                    "displayName": block_cfg.get("displayName", block_name),
                    "fields": fields
                }
        return blocks
