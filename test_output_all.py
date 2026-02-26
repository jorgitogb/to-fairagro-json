import json
import jsonschema
from pathlib import Path

def test_json(filename):
    schema = json.loads(Path('fairagro-schema.json').read_text())
    out_file = Path(f'output/{filename}')
    
    if not out_file.exists():
        print(f"Output {filename} not found.")
        return
        
    data = json.loads(out_file.read_text())
    validator = jsonschema.Draft4Validator(schema)
    
    has_issues = False
    for i, version in enumerate(data):
        blocks = version.get("datasetVersion", {}).get("metadataBlocks", {})
        
        obj = {}
        for block_name, block_content in blocks.items():
            fields = block_content.get("fields", [])
            block_obj = {}
            for field in fields:
                for fname, fval in field.items():
                    if isinstance(fval, dict) and "value" in fval:
                        block_obj[fname] = fval["value"]
                    elif isinstance(fval, list):
                        arr = []
                        for item in fval:
                            if isinstance(item, dict) and "value" in item and len(item) == 1:
                                arr.append(item["value"])
                            elif isinstance(item, dict):
                                flat = {}
                                for sub_fname, sub_fval in item.items():
                                    if "value" in sub_fval:
                                        flat[sub_fname] = sub_fval["value"]
                                arr.append(flat)
                        block_obj[fname] = arr
                    else:
                        block_obj[fname] = fval
            obj[block_name] = block_obj
            
        errors = sorted(validator.iter_errors(obj), key=lambda e: e.path)
        if errors:
            print(f"--- Issues in {filename} dataset {i+1} ---")
            for error in errors:
                has_issues = True
                path = ".".join([str(p) for p in error.path])
                print(f"Error at {path}: {error.message}")
            
    if not has_issues:
        print(f"{filename} All passed!")

if __name__ == "__main__":
    for f in ['bonares-schemaorg.dataverse.json', 'edal-schemaorg.dataverse.json', 'publisso-schemaorg.dataverse.json', 'thunen-schemaorg.dataverse.json']:
        test_json(f)
