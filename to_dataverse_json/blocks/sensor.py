from ..utils import get_value, resolve_entity

class SensorParser:
    @staticmethod
    def parse(entities):
        sensor_items = []
        for e in entities:
            etype = str(e.get('@type', e.get('type', '')))
            add_type = get_value(e, 'additionalType')

            if 'Dataset' in etype and add_type == 'Assay':
                m_method = get_value(e, 'measurementMethod')
                m_technique = get_value(e, 'measurementTechnique')
                
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
                            
                            sensor_entry = {
                                'sensorType': m_method,
                                'sensorPlatformType': m_technique,
                                'sensorPlatformManufacturerName': '',
                                'sensorPlatformModelName': ''
                            }
                            
                            props = obj.get('additionalProperty', [])
                            if not isinstance(props, list): props = [props]
                            
                            for prop_ref in props:
                                prop = resolve_entity(prop_ref, entities)
                                if not isinstance(prop, dict): continue
                                
                                name = get_value(prop, 'name')
                                value = get_value(prop, 'value')
                                
                                if name == 'Drone Manufacturer':
                                    sensor_entry['sensorPlatformManufacturerName'] = value
                                elif name == 'Drone Model':
                                    sensor_entry['sensorPlatformModelName'] = value
                            
                            sensor_items.append(sensor_entry)

        unique_sensors = []
        seen_sensors = set()
        for s in sensor_items:
            key = f"{s['sensorType']}-{s['sensorPlatformType']}-{s['sensorPlatformManufacturerName']}-{s['sensorPlatformModelName']}"
            if key not in seen_sensors:
                unique_sensors.append({
                    "sensorType": {"value": s['sensorType']},
                    "sensorIsHostedBy": [{
                        "sensorPlatformType": {"value": s['sensorPlatformType']},
                        "sensorPlatformManufacturerName": {"value": s['sensorPlatformManufacturerName']},
                        "sensorPlatformModelName": {"value": s['sensorPlatformModelName']}
                    }]
                })
                seen_sensors.add(key)

        return {
            "displayName": "Sensor Metadata",
            "fields": [{"sensor": unique_sensors}] if unique_sensors else []
        }
