import json
import jsonschema
from pathlib import Path


def test_json():
    schema = json.loads(Path("fairagro-schema.json").read_text())

    out_file = Path("output/arc-ro-crate-metadata.fairagro.json")
    if not out_file.exists():
        print("Output not found.")
        return

    data = json.loads(out_file.read_text())
    if not isinstance(data, list):
        data = [data]

    validator = jsonschema.Draft4Validator(schema)

    has_issues = False
    for i, obj in enumerate(data):
        print(f"\nEvaluating dataset {i+1}...")

        errors = sorted(validator.iter_errors(obj), key=lambda e: e.path)
        for error in errors:
            has_issues = True
            path = ".".join([str(p) for p in error.path])
            print(f"Error at {path}: {error.message}")

    if not has_issues:
        print("\nAll passed!")


if __name__ == "__main__":
    test_json()
