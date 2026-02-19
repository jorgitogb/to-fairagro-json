# Mapping Guide: From RO-Crate to Dataverse JSON

This document explains how the mapping system is structured and how to extend it with new metadata blocks and fields.

## Core Components

The mapping process follows three main steps:

1. **Framing**: RO-Crate (JSON-LD) is reshaped into a predictable tree using `config/rocrate/frame.json`.
2. **Mapping Configuration**: `config/dataverse/mapping.yaml` defines which fields to extract and how to format them.
3. **Mapper Logic**: `to_dataverse_json/mapper.py` implements the traversal, reference resolution, and aggregation logic.

---

## How to Add a New Block

To add a new metadata block (e.g., "Project Metadata"), follow these steps:

### 1. Update `mapping.yaml`

Add the new block under the `blocks` key. Use `type: single`, `list`, or `complex_list` for fields.

```yaml
blocks:
  project:
    displayName: "Project Metadata"
    fields:
      - projectName:
          source: ["name"]
          type: "single"
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
    # 1. Gather relevant entities
    projects = self._get_entities_by_type("Project")
    for p in projects:
        # 2. Resolve references
        lead_ref = p.get("funder") 
        lead = self._resolve_ref(lead_ref)
        # 3. Format according to Dataverse requirements
        if lead:
            leads.append({"leadName": {"value": self._get_literal(lead)}})
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
            blocks[block_name] = {"displayName": "Project Metadata", "fields": fields}
        continue
    # ...
```

---

## Technical Details

### Reference Resolution

Use `self._resolve_ref(item)` to automatically follow `@id` references. This allows the mapper to access full object properties even if they are defined elsewhere in the RO-Crate `@graph`.

### List Traversal

The `_get_nested` helper supports deep path lookups. If a property in the path is a list, it will automatically search through all items in that list.

### Deduplication

When aggregating data (like Authors or Sensors), use a `set()` or a unique key to avoid duplicate entries in the Dataverse JSON output.

### Field Types

The `type` property in `mapping.yaml` determines how the extracted value is wrapped for the Dataverse API.

#### 1. `single`

Used for fields that contain a single string or literal value.

- **Dataverse Format**: `{"value": "..."}`
- **Usage**:

  ```yaml
  titleValue:
    source: ["name"]
    type: "single"
  ```

#### 2. `list`

Used for fields that are arrays of simple strings (e.g., Keywords or Subjects).

- **Dataverse Format**: `[{"value": "val1"}, {"value": "val2"}]`
- **Optional `item_key`**: If the Dataverse field expects a different key than `value` inside the list items, specify it with `item_key` (default is `value`).
- **Usage**:

  ```yaml
  keyword:
    source: ["keywords"]
    type: "list"
    item_key: "keywordValue"
  ```

#### 3. `complex_list`

Used for nested fields where each item in the list is an object with its own sub-fields (e.g., Authors or Contacts).

- **Dataverse Format**: `[{"subField1": {"value": "..."}, "subField2": {"value": "..."}}]`
- **`mapping`**: Defines how to extract sub-fields from the resolved object.
- **Usage**:

  ```yaml
  author:
    type: "complex_list"
    mapping:
      authorName: ["name"]
      authorAffiliation: ["affiliation", "memberOf"]
  ```

---

## The `blocks` Key

The `blocks` section in `mapping.yaml` organizes fields into logical groups corresponding to Dataverse Metadata Blocks.

- **`displayName`**: The label shown in the Dataverse UI.
- **`fields`**: A list of field definitions. Each field name must match a valid field in that Dataverse block's TSV definition.

### Example Block Structure

```yaml
blocks:
  blockName: # e.g., citation, crop, sensor
    displayName: "Human Readable Label"
    fields:
      - fieldName:
          source: ["path.to.value"] # Path in the framed JSON
          type: "single"            # single | list | complex_list
          default: "optional"       # Default value if source is missing
```
