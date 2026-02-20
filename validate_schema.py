import json
import jsonschema
from pathlib import Path


def validate():
    schema_text = """
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "citation": {
      "type": "object",
      "properties": {
        "title": { "type": "string" },
        "alternativeTitle": { "type": "array", "items": { "type": "string" } },
        "dsDescription": { 
          "type": "array", 
          "items": { 
            "type": "object",
            "properties": { "dsDescriptionValue": { "type": "string" } }
          }
        },
        "author": { 
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "authorName": { "type": "string" },
              "authorAffiliation": { "type": "string" },
              "authorIdentifier": { "type": "string" },
              "authorIdentifierScheme": { "type": "string" }
            }
          }
        },
        "datasetContact": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "datasetContactName": { "type": "string" },
              "datasetContactEmail": { "type": "string" }
            }
          }
        },
        "subject": { "type": "array", "items": { "type": "string" } },
        "productionDate": { "type": "string" },
        "distributionDate": { "type": "string" }
      }
    },
    "generalExtended": {
      "type": "object",
      "properties": {
        "license": { "type": "string" },
        "sourceDatasetURI": { "type": "string" }
      }
    },
    "geographic": {
      "type": "object",
      "properties": {
        "geographicBoundingBox": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "westLongitude": { "$ref": "#/definitions/valueObject" },
              "eastLongitude": { "$ref": "#/definitions/valueObject" },
              "northLatitude": { "$ref": "#/definitions/valueObject" },
              "southLatitude": { "$ref": "#/definitions/valueObject" }
            }
          }
        }
      }
    },
    "crop": {
      "type": "object",
      "properties": {
        "crop": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "cropSpecies": { "$ref": "#/definitions/valueObject" },
              "cropSpeciesURI": { "$ref": "#/definitions/valueObject" },
              "cropPestName": { "$ref": "#/definitions/valueObject" },
              "cropPestURI": { "$ref": "#/definitions/valueObject" }
            }
          }
        }
      }
    },
    "sensor": {
      "type": "object",
      "properties": {
        "sensor": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "sensorSensorType": { "$ref": "#/definitions/valueObject" },
              "sensorIsHostedBy": {
                "type": "object",
                "properties": {
                  "sensorPlatformType": { "$ref": "#/definitions/valueObject" },
                  "sensorPlatformManufacturerName": { "$ref": "#/definitions/valueObject" },
                  "sensorPlatformModelName": { "$ref": "#/definitions/valueObject" }
                }
              }
            }
          }
        }
      }
    },
    "identifier": { "type": "string" }
  },
  "definitions": {
    "valueObject": {
      "type": "object",
      "properties": {
        "value": { "type": "string" },
        "aiGenerated": { "type": "boolean" }
      },
      "required": ["value", "aiGenerated"]
    }
  }
}
"""
    schema = json.loads(schema_text)

    output_files = Path("output").glob("*.json")
    for output_file in output_files:
        print(f"Validating {output_file}...")
        with open(output_file, "r") as f:
            data = json.load(f)

        # Converter might return a list or a dict
        if isinstance(data, list):
            for i, item in enumerate(data):
                try:
                    jsonschema.validate(instance=item, schema=schema)
                    print(f"  Item {i}: OK")
                except jsonschema.ValidationError as e:
                    print(f"  Item {i}: FAILED - {e.message}")
        else:
            try:
                jsonschema.validate(instance=data, schema=schema)
                print(f"  OK")
            except jsonschema.ValidationError as e:
                print(f"  FAILED - {e.message}")


if __name__ == "__main__":
    validate()
