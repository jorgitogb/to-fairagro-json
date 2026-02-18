from ..utils import get_value, resolve_entity

class GeospatialParser:
    @staticmethod
    def parse(entities):
        geo_items = []
        # Identify Root Dataset
        root = next((e for e in entities if get_value(e, 'additionalType') == 'Investigation'), None)
        if not root:
             root = next((e for e in entities if e.get('@id') == './' or e.get('id') == './'), None)
        if not root:
             root = next((e for e in entities if 'Dataset' in str(e.get('@type', ''))), None)

        if root:
            spatial = root.get('spatialCoverage', [])
            if not isinstance(spatial, list): spatial = [spatial]
            
            for s_ref in spatial:
                s = resolve_entity(s_ref, entities)
                if not isinstance(s, dict): continue
                
                name = get_value(s, 'name')
                geo = s.get('geo')
                if geo:
                    geo = resolve_entity(geo, entities)
                
                if isinstance(geo, dict):
                    # Dataverse expects bounding box or points
                    # box: "lat min, lon min, lat max, lon max"
                    box = get_value(geo, 'box')
                    if box:
                        parts = box.split()
                        if len(parts) == 4:
                            geo_items.append({
                                "geographicBoundingBox": [
                                    {
                                        "westLongitude": {"value": parts[1]},
                                        "eastLongitude": {"value": parts[3]},
                                        "northLatitude": {"value": parts[2]},
                                        "southLatitude": {"value": parts[0]}
                                    }
                                ]
                            })
                    
                    # Points or other geometries could be added here

        return {
            "displayName": "Geospatial Metadata",
            "fields": geo_items if geo_items else []
        }
