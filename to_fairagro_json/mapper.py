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

    def _extract_person(self, person, seen):
        """Extracts an author object from a Person entity. Returns None if already seen."""
        if not isinstance(person, dict):
            return None

        # Try to get the name: prefer explicit 'name', then givenName+familyName, then contactPoint
        name = None
        if person.get("name"):
            name = self._get_literal(person["name"])
        elif person.get("givenName") or person.get("familyName"):
            given = self._get_literal(person.get("givenName", ""))
            family = self._get_literal(person.get("familyName", ""))
            name = f"{given} {family}".strip()
        elif isinstance(person.get("contactPoint"), dict):
            # Schema.org Organization with contactPoint as the actual person
            cp = person["contactPoint"]
            name = self._get_literal(cp.get("name"))

        if not name or name in seen:
            return None
        seen.add(name)

        author_obj = {"authorName": name}

        affiliation = self._resolve_source(person, ["affiliation", "memberOf"])
        if affiliation:
            author_obj["authorAffiliation"] = (
                self._get_literal(affiliation) or "Unknown"
            )
        elif "Organization" in str(person.get("@type", "")) and person.get("name"):
            # The entity itself is the organization — use its name as affiliation
            author_obj["authorAffiliation"] = (
                self._get_literal(person.get("name")) or "Unknown"
            )
        else:
            author_obj["authorAffiliation"] = "Unknown"

        identifier = person.get("@id")
        if (
            identifier
            and not identifier.startswith("#")
            or (identifier and "orcid.org" in identifier)
        ):
            author_obj["authorIdentifier"] = identifier
            if "orcid.org" in identifier:
                author_obj["authorIdentifierScheme"] = "ORCID"
            else:
                author_obj["authorIdentifierScheme"] = "Other"
        else:
            author_obj["authorIdentifier"] = "Unknown"
            author_obj["authorIdentifierScheme"] = "Other"

        return author_obj

    def _extract_authors(self):
        authors = []
        seen = set()

        # First pass: ARC-typed entities (Investigation / Study / Assay)
        arc_datasets = self._get_entities_by_type(
            "Dataset", ["Investigation", "Study", "Assay"]
        )

        for ds in arc_datasets:
            for field in ["creator", "author"]:
                persons = ds.get(field, [])
                if not isinstance(persons, list):
                    persons = [persons]
                for raw in persons:
                    person = self._resolve_ref(raw)
                    if isinstance(person, dict):
                        obj = self._extract_person(person, seen)
                        if obj:
                            authors.append(obj)

        # Second pass: plain Dataset entities (Schema.org) if nothing found yet
        if not authors:
            plain_datasets = self._get_entities_by_type("Dataset")
            for ds in plain_datasets:
                for field in ["author", "creator"]:
                    persons = ds.get(field)
                    if persons is None:
                        continue
                    if not isinstance(persons, list):
                        persons = [persons]
                    for raw in persons:
                        person = self._resolve_ref(raw)
                        if isinstance(person, dict):
                            # Handle Organization-as-author with nested contactPoint
                            if "Organization" in str(
                                person.get("@type", "")
                            ) and isinstance(person.get("contactPoint"), dict):
                                cp = person["contactPoint"]
                                cp_name = self._get_literal(cp.get("name"))
                                if cp_name and cp_name not in seen:
                                    seen.add(cp_name)
                                    obj = {
                                        "authorName": cp_name,
                                        "authorAffiliation": self._get_literal(
                                            person.get("name")
                                        )
                                        or "Unknown",
                                        "authorIdentifier": "Unknown",
                                        "authorIdentifierScheme": "Other",
                                    }
                                    email = self._get_literal(cp.get("email"))
                                    if email:
                                        obj["authorEmail"] = email
                                    authors.append(obj)
                            else:
                                obj = self._extract_person(person, seen)
                                if obj:
                                    authors.append(obj)

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
                                        crop_info["_crop_species"] = str(
                                            prop.get("value", "")
                                        )
                                        crop_info["_crop_species_uri"] = str(
                                            prop.get("valueRef", "")
                                        )
                                    elif name == "Infection Taxon":
                                        crop_info["_crop_pest_name"] = str(
                                            prop.get("value", "")
                                        )
                                        crop_info["_crop_pest_uri"] = str(
                                            prop.get("valueRef", "")
                                        )

                            if crop_info:
                                # Create a unique key for deduplication
                                key = f"{crop_info.get('_crop_species')}|{crop_info.get('_crop_pest_name')}"
                                if key not in seen:
                                    seen.add(key)
                                    crops.append(crop_info)
        return crops

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
                            "_sensor_type": measurement_method,
                            "sensorIsHostedBy": {
                                "_platform_type": measurement_technique,
                                "_manufacturer": manufacturer,
                                "_model": model,
                            },
                        }
                        # Deduplicate by all fields
                        key = f"{measurement_method}|{measurement_technique}|{manufacturer}|{model}"
                        if key not in seen:
                            seen.add(key)
                            sensors.append(sensor_obj)
        return sensors

    def _get_literal(self, v):
        if v is None:
            return ""
        if isinstance(v, list) and v:
            return self._get_literal(v[0])

        if isinstance(v, dict):
            # Resolve reference if it's just an @id
            if len(v) == 1 and "@id" in v:
                resolved = self._resolve_ref(v)
                if isinstance(resolved, dict) and resolved != v:
                    return self._get_literal(resolved)

            # Handle Schema.org/JSON-LD name/value/literal patterns
            if "@value" in v:
                return self._get_literal(v["@value"])
            if "name" in v:
                return self._get_literal(v["name"])
            if "value" in v:
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

            # If it's a dict but we can't find a literal, stringify it as fallback (or return empty if preferred)
            return str(v)

        if isinstance(v, str):
            return self.cleaner.clean(v)
        return str(v)

    def format_field(self, name, val, cfg):
        ftype = cfg.get("type", "string")

        # Specialized logic for Geo Bounding Boxes
        geo_fields = [
            "westLongitude",
            "eastLongitude",
            "northLatitude",
            "southLatitude",
        ]
        if name in geo_fields or any(
            k in str(cfg.get("mapping", {})) for k in ["_geo_"]
        ):
            lit_val = self._get_literal(val)
            if isinstance(lit_val, (str, bytes)):
                geo_vals = self._parse_geo_box(str(lit_val))
                if geo_vals:
                    # If we are inside a complex_list mapping, return the dict
                    return geo_vals

        if ftype == "string":
            lit = str(self._get_literal(val))
            if cfg.get("wrap"):
                return {name: {"value": lit, "aiGenerated": False}}
            return {name: lit}

        if ftype == "string_array":
            if isinstance(val, str):
                vals = [v.strip() for v in val.split(",")]
            elif isinstance(val, list):
                vals = [str(self._get_literal(v)) for v in val]
            else:
                vals = [str(self._get_literal(val))]
            return {name: vals}

        if ftype == "complex_list":
            items = []
            if not isinstance(val, list):
                val = [val]
            for item in val:
                sub_fields = {}
                # If no mapping, and item is a dict, just use it (pass-through for defaults)
                if not cfg.get("mapping"):
                    if isinstance(item, dict):
                        items.append(item)
                    continue

                # Special cases for geo/crop/sensor where we use placeholders
                if isinstance(item, dict):
                    # Check for geo box mapping
                    if "_geo_west" in str(cfg.get("mapping", {})):
                        geo = self._parse_geo_box(self._get_literal(item))
                        if geo:
                            for k, v in geo.items():
                                sub_cfg = cfg["mapping"].get(k, {})
                                if sub_cfg.get("wrap"):
                                    sub_fields[k] = {
                                        "value": str(v),
                                        "aiGenerated": False,
                                    }
                                else:
                                    sub_fields[k] = str(v)
                    else:
                        for sub_name, sub_cfg in cfg.get("mapping", {}).items():
                            if isinstance(sub_cfg, dict):
                                sub_sources = sub_cfg.get("source", [])
                                # Handle placeholders from special extractions
                                if sub_sources and sub_sources[0].startswith("_"):
                                    sub_val = item.get(sub_sources[0])
                                else:
                                    sub_val = self._resolve_source(item, sub_sources)

                                if sub_val:
                                    lit = str(self._get_literal(sub_val))
                                    if sub_cfg.get("wrap"):
                                        sub_fields[sub_name] = {
                                            "value": lit,
                                            "aiGenerated": False,
                                        }
                                    else:
                                        sub_fields[sub_name] = lit
                            elif isinstance(sub_cfg, list):
                                # Simple mapping
                                sub_val = self._resolve_source(item, sub_cfg)
                                if sub_val:
                                    sub_fields[sub_name] = str(
                                        self._get_literal(sub_val)
                                    )
                else:
                    # Item is a literal (e.g. from dsDescription or keyword)
                    for sub_name, sub_cfg in cfg.get("mapping", {}).items():
                        sub_sources = (
                            sub_cfg
                            if isinstance(sub_cfg, list)
                            else sub_cfg.get("source", [])
                        )
                        if "@" in sub_sources:
                            sub_fields[sub_name] = str(self._get_literal(item))

                if sub_fields:
                    items.append(sub_fields)
            return {name: items}

        if ftype == "complex":
            # If no mapping, and item is a dict, just use it (pass-through for defaults)
            if not cfg.get("mapping"):
                if isinstance(val, dict):
                    return {name: val}
                return {name: {}}

            # Nested object (like sensorIsHostedBy)
            obj = {}
            for sub_name, sub_cfg in cfg.get("mapping", {}).items():
                if isinstance(sub_cfg, dict):
                    sub_sources = sub_cfg.get("source", [])
                    sub_val = self._resolve_source(val, sub_sources)
                    if sub_sources and sub_sources[0].startswith("_"):
                        sub_val = val.get(sub_sources[0])

                    if sub_val:
                        lit = str(self._get_literal(sub_val))
                        if sub_cfg.get("wrap"):
                            obj[sub_name] = {"value": lit, "aiGenerated": False}
                        else:
                            obj[sub_name] = lit
            return {name: obj}

        return {name: str(self._get_literal(val))}

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
        """Maps an entity to FAIRagro Core spec blocks."""
        result = {}
        for block_name, block_cfg in self.mapping.get("blocks", {}).items():
            block_data = {}

            # Special Block Handling
            if block_name == "crop":
                crops = self._extract_crops()
                if crops:
                    formatted = self.format_field(
                        "crop", crops, block_cfg["fields"][0]["crop"]
                    )
                    block_data.update(formatted)
            elif block_name == "sensor":
                sensors = self._extract_sensors()
                if sensors:
                    formatted = self.format_field(
                        "sensor", sensors, block_cfg["fields"][0]["sensor"]
                    )
                    block_data.update(formatted)
            else:
                for field_cfg in block_cfg.get("fields", []):
                    field_name = list(field_cfg.keys())[0]
                    cfg = field_cfg[field_name]
                    val = None

                    # Special Field Handling
                    if block_name == "citation":
                        if field_name == "author":
                            val = self._extract_authors()
                            if not val:
                                val = [
                                    {
                                        "authorName": "Unknown",
                                        "authorAffiliation": "Unknown",
                                        "authorIdentifier": "Unknown",
                                        "authorIdentifierScheme": "Other",
                                    }
                                ]
                            block_data["author"] = val
                            continue
                        elif field_name == "alternativeTitle":
                            titles = []
                            datasets = self._get_entities_by_type(
                                "Dataset", ["Study", "Assay"]
                            )
                            for ds in datasets:
                                name = self._get_literal(ds.get("name"))
                                if name:
                                    titles.append(name)
                            if titles:
                                block_data["alternativeTitle"] = titles
                            continue
                        elif field_name == "datasetContact":
                            # Try to extract contact from entity
                            contacts = self._resolve_source(
                                entity, ["contactPoint", "maintainer"]
                            )
                            if not contacts:
                                # Default internal FAIRagro contact if nothing found
                                val = cfg.get("default")
                            else:
                                if not isinstance(contacts, list):
                                    contacts = [contacts]
                                val = []
                                for c_raw in contacts:
                                    c = self._resolve_ref(c_raw)
                                    c_name = self._get_literal(
                                        c.get("name") or c.get("givenName")
                                    )
                                    c_email = self._get_literal(c.get("email"))
                                    if c_email:
                                        val.append(
                                            {
                                                "datasetContactName": c_name
                                                or "Unknown",
                                                "datasetContactEmail": c_email,
                                            }
                                        )
                                if not val:
                                    val = cfg.get("default")

                            if val:
                                block_data["datasetContact"] = val
                            continue
                        elif field_name == "dsDescription":
                            # Try top-level description first
                            desc = self._resolve_source(
                                entity, ["description", "comment"]
                            )
                            if not desc:
                                # Fall back to aggregating descriptions from Study/Assay parts
                                seen_descs = set()
                                desc_items = []
                                for ds in self._get_entities_by_type(
                                    "Dataset", ["Study", "Assay"]
                                ):
                                    d = self._get_literal(
                                        ds.get("description") or ds.get("comment")
                                    )
                                    if d and d not in seen_descs:
                                        seen_descs.add(d)
                                        desc_items.append({"dsDescriptionValue": d})
                                if desc_items:
                                    block_data["dsDescription"] = desc_items
                                continue
                            # Otherwise let the normal format_field path handle it
                        elif field_name == "otherId":
                            identifiers = self._resolve_source(entity, ["identifier"])
                            if identifiers:
                                if not isinstance(identifiers, list):
                                    identifiers = [identifiers]
                                other_ids = []
                                for ident in identifiers:
                                    ident_str = str(self._get_literal(ident))
                                    if not ident_str or ident_str in ("None", ""):
                                        continue
                                    agency = (
                                        "DOI" if "doi.org" in ident_str else "Other"
                                    )
                                    other_ids.append(
                                        {
                                            "otherIdValue": ident_str,
                                            "otherIdAgency": agency,
                                        }
                                    )
                                if other_ids:
                                    block_data["otherId"] = other_ids
                            continue

                    if "source" in cfg:
                        val = self._resolve_source(entity, cfg["source"])

                    if (val is None or val == "" or val == []) and "default" in cfg:
                        val = cfg["default"]

                    if val is not None:
                        formatted = self.format_field(field_name, val, cfg)
                        block_data.update(formatted)

            # Ensure mandatory fields are present in the block
            mandatory_fallbacks = {
                "citation": {
                    "dsDescription": [
                        {"dsDescriptionValue": "No description available"}
                    ],
                    "otherId": [{"otherIdValue": "Unknown", "otherIdAgency": "Other"}],
                }
            }
            if block_name in mandatory_fallbacks:
                for field, fallback_val in mandatory_fallbacks[block_name].items():
                    if field not in block_data:
                        block_data[field] = fallback_val

            if block_data:
                result[block_name] = block_data

        # Add identifier if present
        identifier = self._get_literal(entity.get("identifier")) or self._get_literal(
            entity.get("@id")
        )
        if identifier:
            result["identifier"] = str(identifier)

        return result
