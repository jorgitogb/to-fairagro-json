from ..utils import get_value, resolve_entity

class CropParser:
    @staticmethod
    def parse(entities):
        crop_items = []
        for e in entities:
            etype = str(e.get('@type', e.get('type', '')))
            add_type = get_value(e, 'additionalType')

            if 'Dataset' in etype and add_type == 'Study':
                abouts = e.get('about', [])
                if not isinstance(abouts, list): abouts = [abouts]
                
                for about_ref in abouts:
                    about = resolve_entity(about_ref, entities)
                    if not isinstance(about, dict): continue
                    
                    if 'LabProcess' in str(about.get('@type', about.get('type', ''))):
                        objects = about.get('object', [])
                        if not isinstance(objects, list): objects = [objects]
                        
                        for obj_ref in objects:
                            obj = resolve_entity(obj_ref, entities)
                            if not isinstance(obj, dict): continue
                            
                            if 'Sample' in str(obj.get('@type', obj.get('type', ''))) and get_value(obj, 'additionalType') == 'Material':
                                crop_entry = {
                                    'cropSpecies': '', 'cropSpeciesURI': '',
                                    'cropPest': '', 'cropPestURI': ''
                                }
                                props = obj.get('additionalProperty', [])
                                if not isinstance(props, list): props = [props]
                                
                                for prop_ref in props:
                                    prop = resolve_entity(prop_ref, entities)
                                    if not isinstance(prop, dict): continue
                                    
                                    name = get_value(prop, 'name')
                                    value = get_value(prop, 'value')
                                    value_ref = get_value(prop, 'valueRef', '')
                                    
                                    if name == 'Organism':
                                        crop_entry['cropSpecies'] = value
                                        crop_entry['cropSpeciesURI'] = value_ref
                                    elif name == 'Infection Taxon':
                                        crop_entry['cropPest'] = value
                                        crop_entry['cropPestURI'] = value_ref
                                
                                if any(crop_entry.values()):
                                    crop_items.append(crop_entry)

        unique_crops = []
        seen_crops = set()
        for c in crop_items:
            key = f"{c['cropSpecies']}-{c['cropPest']}"
            if key not in seen_crops:
                unique_crops.append({
                    "cropSpecies": {"value": c['cropSpecies']},
                    "cropSpeciesURI": {"value": c['cropSpeciesURI']},
                    "cropPest": {"value": c['cropPest']},
                    "cropPestURI": {"value": c['cropPestURI']}
                })
                seen_crops.add(key)

        return {
            "displayName": "Crop Metadata",
            "fields": [{"crop": unique_crops}] if unique_crops else []
        }
