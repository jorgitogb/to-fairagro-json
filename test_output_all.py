import json
import jsonschema
from pathlib import Path


def test_json(filename):
    schema = json.loads(Path("fairagro-schema.json").read_text())
    out_file = Path(f"output/{filename}")

    if not out_file.exists():
        print(f"Output {filename} not found.")
        return

    data = json.loads(out_file.read_text())
    if not isinstance(data, list):
        data = [data]

    validator = jsonschema.Draft4Validator(schema)

    has_issues = False
    for i, obj in enumerate(data):
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
    for f in [
        "bonares-schemaorg.fairagro.json",
        "edal-schemaorg.fairagro.json",
        "publisso-schemaorg.fairagro.json",
        "thunen-schemaorg.fairagro.json",
    ]:
        test_json(f)
