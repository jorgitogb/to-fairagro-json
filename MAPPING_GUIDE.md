# Mapping Guide: From RO-Crate to FAIRagro Core JSON

This document explains how the mapping system is structured and how to extend it with new metadata blocks and fields.

## Core Components

The mapping process follows three main steps:

1. **Framing**: RO-Crate (JSON-LD) is reshaped into a predictable tree using `config/rocrate/frame.json`.
2. **Mapping Configuration**: `config/fairagro/mapping.yaml` defines which fields to extract and how to format them.
3. **Mapper Logic**: `to_fairagro_json/mapper.py` implements the traversal, reference resolution, and aggregation logic.

---

## How to Add a New Block

To add a new metadata block (e.g., "Project Metadata"), follow these steps:

### 1. Update `mapping.yaml`

Add the new block under the `blocks` key. Use `type: string`, `string_array`, or `complex_list` for fields.

```yaml
blocks:
  project:
    fields:
      - projectName:
          source: ["name"]
          type: "string"
      - projectLead:
          type: "complex_list"
          mapping:
            leadName: ["name"]
```

### 2. Extend `mapper.py`

If the block requires complex logic (like aggregating data from multiple entities), add a specialized extraction method in the `MetadataMapper` class.

#### Example Extraction Method

```python
def _extract_project_leads(self):
    leads = []
    projects = self._get_entities_by_type("Project")
    for p in projects:
        lead_ref = p.get("funder") 
        lead = self._resolve_ref(lead_ref)
        if lead:
            leads.append({"leadName": self._get_literal(lead)})
    return leads
```

#### Register the Block in `map_entity`

Update the `map_entity` method to call your new extraction logic.

```python
def map_entity(self, entity):
    # ...
    if block_name == "project":
        fields = self._extract_project_leads()
        if fields:
            block_data["project"] = fields
        continue
    # ...
```

---

## Technical Details

### Reference Resolution

Use `self._resolve_ref(item)` to automatically follow `@id` references. This allows the mapper to access full object properties even if they are defined elsewhere in the RO-Crate `@graph`.

### List Traversal

The `_get_nested` helper supports deep path lookups. If a property in the path is a list, it will automatically search through all items in that list.

### Metadata Mapping

The mapper uses the `type` property in `mapping.yaml` to determine the output format.

#### 1. `string`

Used for fields that contain a single string value.

- **Format**: `"value"`

#### 2. `string_array`

Used for simple lists of strings.

- **Format**: `["val1", "val2"]`

#### 3. `complex_list`

Used for nested fields where each item is an object with its own sub-fields.

- **Format**: `[{"subField1": "...", "subField2": "..."}]`

#### 4. `complex`

Used for a single nested object.

- **Format**: `{"subField1": "...", "subField2": "..."}`

---

## The `blocks` Key

The `blocks` section in `mapping.yaml` organizes fields into logical groups.

- **`fields`**: A list of field definitions.

### Example Block Structure

```yaml
blocks:
  blockName: # e.g., citation, crop, sensor
    fields:
      - fieldName:
          source: ["path.to.value"] # Path in the framed JSON
          type: "string"            # string | string_array | complex_list | complex
          default: "optional"       # Default value if source is missing
```
