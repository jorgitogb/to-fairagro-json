import re
from .cleaner import StringCleaner


class MetadataMapper:
    def __init__(self, mapping, all_entities=None):
        self.mapping = mapping
        self.cleaner = StringCleaner()
        self.all_entities = all_entities or []

    def _get_nested(self, data, path):
        """Helper to get value from nested dict using dot notation."""
        if path == "@":
            return data
        parts = path.split(".")
        for part in parts:
            if isinstance(data, dict):
                data = data.get(part)
            elif isinstance(data, list) and data:
                # Try to find in any list item if it's a list
                res = []
                for item in data:
                    if isinstance(item, dict):
                        val = item.get(part)
                        if val:
                            if isinstance(val, list):
                                res.extend(val)
                            else:
                                res.append(val)
                data = res if res else None
            else:
                return None
        return data

    def _resolve_source(self, entity, sources):
        for source in sources:
            val = self._get_nested(entity, source)
            if val:
                return val
        return None

    def _resolve_ref(self, ref):
        """Resolves a reference (@id) to an entity."""
        if not isinstance(ref, dict) or "@id" not in ref:
            return ref

        ref_id = ref["@id"]
        for entity in self.all_entities:
            if entity.get("@id") == ref_id:
                return entity
        return ref

    def _get_entities_by_type(self, etype, additional_types=None):
        results = []
        for e in self.all_entities:
            types = e.get("@type", [])
            if isinstance(types, str):
                types = [types]
            if etype in types:
                if additional_types:
                    add_types = e.get("additionalType", [])
                    if isinstance(add_types, str):
                        add_types = [add_types]
                    if any(t in add_types for t in additional_types):
                        results.append(e)
                else:
                    results.append(e)
        return results

    def _extract_authors(self, entity=None):
        authors = []
        seen = set()
        
        # In RO-Crate, authors might be on sub-datasets
        datasets = self._get_entities_by_type("Dataset", ["Investigation", "Study", "Assay"])
        # Always include the current entity we are mapping (which could be the only Dataset)
        if entity and entity not in datasets:
            datasets.append(entity)

        for ds in datasets:
            creators = self._resolve_source(ds, ["creator", "author"]) or []
            if not isinstance(creators, list):
                creators = [creators]
            for c in creators:
                person = self._resolve_ref(c)
                # Schemaorg authors might just be strings or lack @type=Person explicitly if unstructured
                name = self._get_literal(person)
                if not name and isinstance(person, dict):
                    name = self._resolve_source(person, ["name", "contactPoint.name", "givenName"])
                if name and name not in seen:
                    seen.add(name)
                    author_obj = {"authorName": {"value": str(name)}}

                    affiliation = self._resolve_source(
                        person, ["affiliation", "memberOf", "publisher"]
                    )
                    if affiliation:
                        author_obj["authorAffiliation"] = {
                            "value": str(self._get_literal(affiliation))
                        }

                    identifier = person.get("@id") if isinstance(person, dict) else None
                    if not identifier and isinstance(person, dict):
                        identifier = person.get("identifier")
                        
                    if identifier:
                        scheme = "ORCID" if "orcid.org" in identifier else "Other"
                        author_obj["authorIdentifier"] = {"value": str(identifier)}
                        author_obj["authorIdentifierScheme"] = {"value": scheme}
                    else:
                        # FAIRagro requires identifier but schemaorg examples might omit it
                        author_obj["authorIdentifier"] = {"value": "unknown"}
                        author_obj["authorIdentifierScheme"] = {"value": "unknown"}

                    authors.append(author_obj)
        return authors

    def _extract_crops(self):
        crops = []
        seen = set()
        studies = self._get_entities_by_type("Dataset", ["Study"])

        for study in studies:
            about = study.get("about", [])
            if not isinstance(about, list):
                about = [about]
            for proc_ref in about:
                proc = self._resolve_ref(proc_ref)
                if isinstance(proc, dict) and "LabProcess" in str(
                    proc.get("@type", "")
                ):
                    objects = proc.get("object", [])
                    if not isinstance(objects, list):
                        objects = [objects]
                    for obj_ref in objects:
                        sample = self._resolve_ref(obj_ref)
                        if isinstance(sample, dict) and "Sample" in str(
                            sample.get("@type", "")
                        ):
                            props = sample.get("additionalProperty", [])
                            if not isinstance(props, list):
                                props = [props]

                            crop_info = {}
                            for prop in props:
                                prop = self._resolve_ref(prop)
                                if isinstance(prop, dict):
                                    name = prop.get("name")
                                    if name == "Organism":
                                        crop_info["cropSpecies"] = {
                                            "value": str(prop.get("value", ""))
                                        }
                                        crop_info["cropSpeciesURI"] = {
                                            "value": str(prop.get("valueRef", ""))
                                        }
                                    elif name == "Infection Taxon":
                                        crop_info["cropPest"] = {
                                            "value": str(prop.get("value", ""))
                                        }
                                        crop_info["cropPestURI"] = {
                                            "value": str(prop.get("valueRef", ""))
                                        }

                            if crop_info:
                                # Create a unique key for deduplication
                                key = f"{crop_info.get('cropSpecies', {}).get('value')}|{crop_info.get('cropPest', {}).get('value')}"
                                if key not in seen:
                                    seen.add(key)
                                    crops.append(crop_info)
        return [{"crop": crops}] if crops else []

    def _extract_sensors(self):
        sensors = []
        seen = set()
        assays = self._get_entities_by_type("Dataset", ["Assay"])

        for assay in assays:
            about = assay.get("about", [])
            if not isinstance(about, list):
                about = [about]

            measurement_method = self._get_literal(assay.get("measurementMethod"))
            measurement_technique = self._get_literal(assay.get("measurementTechnique"))

            for proc_ref in about:
                proc = self._resolve_ref(proc_ref)
                if isinstance(proc, dict) and "LabProcess" in str(
                    proc.get("@type", "")
                ):
                    # Collect metadata from parameterValue of the LabProcess
                    params = proc.get("parameterValue", [])
                    if not isinstance(params, list):
                        params = [params]

                    manufacturer = ""
                    model = ""
                    for param_ref in params:
                        param = self._resolve_ref(param_ref)
                        if isinstance(param, dict):
                            if param.get("name") == "Drone Manufacturer":
                                manufacturer = self._get_literal(param.get("value"))
                            elif param.get("name") == "Drone Model":
                                model = self._get_literal(param.get("value"))

                    # Requirements: Create a sensor object for EACH object in proc
                    objects = proc.get("object", [])
                    if not isinstance(objects, list):
                        objects = [objects]
                    for obj in objects:
                        sensor_obj = {
                            "sensorType": {"value": measurement_method},
                            "sensorIsHostedBy": {
                                "sensorPlatformType": {"value": measurement_technique},
                                "sensorPlatformManufacturerName": {
                                    "value": manufacturer
                                },
                                "sensorPlatformModelName": {"value": model},
                            },
                        }
                        # Deduplicate by all fields
                        key = f"{measurement_method}|{measurement_technique}|{manufacturer}|{model}"
                        if key not in seen:
                            seen.add(key)
                            sensors.append(sensor_obj)
        return [{"sensor": sensors}] if sensors else []

    def _get_literal(self, v):
        if v is None:
            return ""
        if isinstance(v, list) and v:
            return self._get_literal(v[0])

        if isinstance(v, dict):
            # Handle Schema.org/JSON-LD name/value/literal patterns
            if v.get("@value"):
                return self._get_literal(v["@value"])
            if v.get("name"):
                return self._get_literal(v["name"])
            if v.get("value"):
                return self._get_literal(v["value"])
            # Support Schema.org Person names
            if "givenName" in v or "familyName" in v:
                given = self._get_literal(v.get("givenName", ""))
                family = self._get_literal(v.get("familyName", ""))
                full = f"{given} {family}".strip()
                if full:
                    return self.cleaner.clean(full)
            if "text" in v:
                return self._get_literal(v["text"])

        if isinstance(v, str):
            return self.cleaner.clean(v)
        return v

    def format_field(self, name, val, cfg):
        ftype = cfg.get("type", "single")

        # Specialized logic for Geo Bounding Boxes
        geo_fields = [
            "westLongitude",
            "eastLongitude",
            "northLatitude",
            "southLatitude",
        ]
        if name in geo_fields:
            lit_val = self._get_literal(val)
            if isinstance(lit_val, (str, bytes)):
                geo_vals = self._parse_geo_box(str(lit_val))
                if geo_vals and name in geo_vals:
                    return {name: {"value": str(geo_vals[name])}}

        if ftype == "single":
            lit = self._get_literal(val)
            return {name: {"value": str(lit)}}

        if ftype == "list":
            item_key = cfg.get("item_key")
            if isinstance(val, str):
                vals = [v.strip() for v in val.split(",")]
            elif isinstance(val, list):
                vals = val
            else:
                vals = [val]

            items = []
            for v in vals:
                lit = self._get_literal(v)
                lit_list = lit if isinstance(lit, list) else [lit]
                for item in lit_list:
                    str_val = str(self._get_literal(item))
                    if item_key:
                        items.append({item_key: {"value": str_val}})
                    else:
                        items.append(str_val)
            return {name: items}

        if ftype == "complex_list":
            items = []
            if not isinstance(val, list):
                val = [val]
            for item in val:
                sub_fields = {}
                for sub_name, sub_sources in cfg.get("mapping", {}).items():
                    sub_val = self._resolve_source(item, sub_sources)
                    if sub_val:
                        sub_fields[sub_name] = {
                            "value": str(self._get_literal(sub_val))
                        }
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
                    "westLongitude": min(lons),
                    "eastLongitude": max(lons),
                    "northLatitude": max(lats),
                    "southLatitude": min(lats),
                }
        except Exception:
            pass
        return {}

    def map_entity(self, entity):
        """Maps an entity to Dataverse blocks, with special handling for RO-Crate aggregations."""
        blocks = {}
        for block_name, block_cfg in self.mapping.get("blocks", {}).items():
            fields = []

            # Special Block Handling
            if block_name == "crop":
                fields = self._extract_crops()
                if fields:
                    blocks[block_name] = {
                        "displayName": block_cfg.get("displayName", "Crop Metadata"),
                        "fields": fields,
                    }
                continue

            if block_name == "sensor":
                fields = self._extract_sensors()
                if fields:
                    blocks[block_name] = {
                        "displayName": block_cfg.get("displayName", "Sensor Metadata"),
                        "fields": fields,
                    }
                continue

            for field_cfg in block_cfg.get("fields", []):
                field_name = list(field_cfg.keys())[0]
                cfg = field_cfg[field_name]

                val = None
                # Special Field Handling
                if block_name == "citation":
                    if field_name == "author":
                        val = self._extract_authors(entity)
                        if val:
                            fields.append({"author": val})
                        continue
                    elif field_name == "alternativeTitle":
                        # Visit Study | Assay, parse name
                        titles = []
                        datasets = self._get_entities_by_type(
                            "Dataset", ["Study", "Assay"]
                        )
                        for ds in datasets:
                            name = self._get_literal(ds.get("name"))
                            if name:
                                titles.append(name)
                        if titles:
                            fields.append(
                                {
                                    "alternativeTitle": titles
                                }
                            )
                        continue
                    elif field_name == "otherId":
                        val = self._resolve_source(entity, ["identifier"])
                        agency = "Other"
                        if val and "doi.org" in str(val):
                            agency = "DOI"
                        elif not val:
                            val = f"arc-rocrate-{entity.get('@id', 'unknown')}"
                            
                        fields.append(
                            {
                                "otherId": [
                                    {
                                        "otherIdValue": {"value": str(val)},
                                        "otherIdAgency": {"value": agency},
                                    }
                                ]
                            }
                        )
                        continue

                if "source" in cfg:
                    val = self._resolve_source(entity, cfg["source"])

                if not val and "default" in cfg:
                    val = cfg["default"]

                if val:
                    fields.append(self.format_field(field_name, val, cfg))

            if fields:
                blocks[block_name] = {
                    "displayName": block_cfg.get("displayName", block_name),
                    "fields": fields,
                }
        return blocks
