import json
import jsonschema
from pathlib import Path


def validate():
    schema_text = """
{
  "$schema": "http://json-schema.org/draft-04/schema",
  "title": "FAIRagro Core Metadata Specification Schema",
  "description": "JSON-schema representing the FAIRagro Core Metadata Specification",
  "type": "object",
  "version": "0.7.7",
  "versionDate": "2026-02-11",
  "required": [
    "citation"
  ],
  "properties": {
    "identifier": {
      "type": "string",
      "description": "Primary identifier of the dataset within the FAIRagro Search Hub",
      "display_name": "ID"
    },
    "citation": {
      "status": "release",
      "type": "object",
      "required": [
        "otherId",
        "title",
        "author",
        "datasetContact",
        "dsDescription",
        "subject",
        "keyword"
      ],
      "description": "A set of generic metadata for datasets",
      "display_name": "General metadata",
      "properties": {
        "otherId": {
          "status": "release",
          "type": "array",
          "description": "Another unique identifier for the Dataset (e.g. producer's or another repository's identifier)",
          "display_name": "Alternative identifier(s)",
          "items": {
            "type": "object",
            "required": [
              "otherIdValue",
              "otherIdAgency"
            ],
            "properties": {
              "otherIdValue": {
                "status": "release",
                "type": "string",
                "description": "Another identifier uniquely identifies the Dataset",
                "display_name": "Alternative identifier value"
              },
              "otherIdAgency": {
                "status": "release",
                "type": "string",
                "description": "The name of the agency that generated the other identifier",
                "display_name": "Alternative identifier registration agency"
              }
            }
          }
        },
        "title": {
          "status": "release",
          "type": "string",
          "description": "The main title of the Dataset",
          "display_name": "Title"
        },
        "alternativeTitle": {
          "status": "release",
          "type": "array",
          "description": "Either 1) a title commonly used to refer to the Dataset or 2) an abbreviation of the main title",
          "display_name": "Alternative Title",
          "items": {
            "type": "string"
          }
        },
        "author": {
          "status": "release",
          "type": "array",
          "description": "The entity, e.g. a person or organization, that created the Dataset",
          "display_name": "Author(s)",
          "items": {
            "type": "object",
            "required": [
              "authorName",
              "authorAffiliation",
              "authorIdentifier"
            ],
            "properties": {
              "authorName": {
                "status": "release",
                "type": "string",
                "description": "The name of the author, such as the person's name or the name of an organization",
                "display_name": "Author name"
              },
              "authorAffiliation": {
                "status": "release",
                "type": "string",
                "description": "The name of the entity affiliated with the author, e.g. an organization's name",
                "display_name": "Author affiliation"
              },
              "authorIdentifier": {
                "status": "release",
                "type": "string",
                "description": "Uniquely identifies the author when paired with an identifier type",
                "display_name": "Author identifier"
              },
              "authorIdentifierScheme": {
                "status": "release",
                "type": "string",
                "description": "The type of identifier that uniquely identifies the author (e.g. ORCID, ISNI)",
                "display_name": "Author identifier scheme"
              }
            }
          }
        },
        "contributor": {
          "status": "release",
          "type": "array",
          "description": "The entity, such as a person or organization, responsible for collecting, managing, or otherwise contributing to the development of the Dataset",
          "display_name": "Contributor(s)",
          "items": {
            "type": "object",
            "properties": {
              "contributorName": {
                "status": "release",
                "type": "string",
                "description": "The name of the contributor, e.g. the person's name or the name of an organization",
                "display_name": "Contributor name"
              },
              "contributorType": {
                "status": "release",
                "type": "string",
                "description": "Indicates the type of contribution made to the dataset",
                "display_name": "Contributor type"
              }
            }
          }
        },
        "datasetContact": {
          "status": "release",
          "type": "array",
          "description": "The entity, e.g. a person or organization, that users of the Dataset can contact with questions",
          "display_name": "Contact(s)",
          "items": {
            "type": "object",
            "required": [
              "datasetContactEmail"
            ],
            "properties": {
              "datasetContactName": {
                "status": "release",
                "type": "string",
                "description": "The name of the point of contact, e.g. the person's name or the name of an organization",
                "display_name": "Contact name"
              },
              "datasetContactAffiliation": {
                "status": "release",
                "type": "string",
                "description": "The name of the entity affiliated with the point of contact, e.g. an organization's name",
                "display_name": "Contact affiliation"
              },
              "datasetContactEmail": {
                "status": "release",
                "type": "string",
                "description": "The point of contact's email address",
                "display_name": "Contact email"
              }
            }
          }
        },
        "dsDescription": {
          "status": "release",
          "type": "array",
          "description": "A summary describing the purpose, nature, and scope of the Dataset",
          "display_name": "Description(s)",
          "items": {
            "type": "object",
            "required": [
              "dsDescriptionValue"
            ],
            "properties": {
              "dsDescriptionValue": {
                "status": "release",
                "type": "string",
                "description": "A summary describing the purpose, nature, and scope of the Dataset",
                "display_name": "Description text"
              }
            }
          }
        },
        "subject": {
          "status": "release",
          "type": "array",
          "description": "The area of study relevant to the Dataset",
          "display_name": "Subject(s)",
          "items": {
            "type": "string"
          }
        },
        "keyword": {
          "status": "release",
          "type": "array",
          "description": "A key term that describes an important aspect of the Dataset and information about any controlled vocabulary used",
          "display_name": "Keyword(s)",
          "items": {
            "type": "object",
            "required": [
              "keywordValue"
            ],
            "properties": {
              "keywordValue": {
                "status": "release",
                "type": "string",
                "description": "A key term that describes important aspects of the Dataset",
                "display_name": "Keyword text"
              },
              "keywordTermURI": {
                "status": "release",
                "type": "string",
                "description": "A URI that points to the web presence of the Keyword Term",
                "display_name": "Keyword term URI"
              },
              "keywordVocabulary": {
                "status": "release",
                "type": "string",
                "description": "The controlled vocabulary used for the keyword term (e.g. LCSH, MeSH)",
                "display_name": "Keyword vocabulary"
              },
              "keywordVocabularyURI": {
                "status": "release",
                "type": "string",
                "description": "The URL where one can access information about the term's controlled vocabulary",
                "display_name": "Keyword vocabulary URI"
              }
            }
          }
        },
        "language": {
          "status": "release",
          "type": "array",
          "description": "A language that the Dataset's files are written in",
          "display_name": "Language(s)",
          "items": {
            "type": "string"
          }
        },
        "productionDate": {
          "status": "release",
          "type": "string",
          "description": "The date when the data were produced (not distributed, published, or archived)",
          "display_name": "Production date"
        },
        "distributionDate": {
          "status": "release",
          "type": "string",
          "description": "The date when the Dataset was made available for distribution/presentation",
          "display_name": "Distribution date"
        },
        "publication": {
          "status": "release",
          "type": "array",
          "description": "The article or report that uses the data in the Dataset. The full list of related publications will be displayed on the metadata tab",
          "display_name": "Related publication(s)",
          "items": {
            "type": "object",
            "properties": {
              "publicationCitation": {
                "status": "release",
                "type": "string",
                "description": "The full bibliographic citation for the related publication",
                "display_name": "Related publication citation"
              },
              "publicationIDType": {
                "status": "release",
                "type": "string",
                "description": "The type of identifier that uniquely identifies a related publication",
                "display_name": "Related publication identifier type"
              },
              "publicationIDNumber": {
                "status": "release",
                "type": "string",
                "description": "The identifier for a related publication",
                "display_name": "Related publication identifier"
              },
              "publicationURL": {
                "status": "release",
                "type": "string",
                "description": "The URL form of the identifier entered in the Identifier field, e.g. the DOI URL if a DOI was entered in the Identifier field. Used to display what was entered in the ID Type and ID Number fields as a link. If what was entered in the Identifier field has no URL form, the URL of the publication webpage is used, e.g. a journal article",
                "display_name": "Related publication link"
              }
            }
          }
        },
        "relatedDatasets": {
          "status": "release",
          "type": "array",
          "description": "Information, such as a persistent ID or citation, about a related dataset, such as previous research on the Dataset's subject",
          "display_name": "Related dataset(s)",
          "items": {
            "type": "string"
          }
        },
        "timePeriodCovered": {
          "status": "release",
          "type": "array",
          "description": "The time period that the data refer to. Also known as span. This is the time period covered by the data, not the dates of coding, collecting data, or making documents machine-readable",
          "display_name": "Time Period",
          "items": {
            "type": "object",
            "properties": {
              "timePeriodCoveredStart": {
                "status": "release",
                "type": "string",
                "description": "The start date of the time period that the data refer to",
                "display_name": "Start Date"
              },
              "timePeriodCoveredEnd": {
                "status": "release",
                "type": "string",
                "description": "The end date of the time period that the data refer to",
                "display_name": "End Date"
              }
            }
          }
        }
      }
    },
    "generalExtended": {
      "status": "in testing",
      "type": "object",
      "required": [
        "license",
        "sourceDatasetURI",
        "sourceRDI"
      ],
      "description": "A set of generic metadata for datasets",
      "display_name": "General metadata",
      "properties": {
        "resourceType": {
          "status": "in testing",
          "type": "string",
          "description": "The nature or genre of the resource.",
          "display_name": "Resource type"
        },
        "accessRights": {
          "status": "in testing",
          "type": "array",
          "description": "Information about who access the resource or an indication of its security status.",
          "display_name": "Access rights",
          "items": {
            "type": "string"
          }
        },
        "accessType": {
          "status": "release",
          "type": "string",
          "description": "A flag to signal that the item, event, or place is accessible for free.",
          "display_name": "Access type"
        },
        "yieldMeasurementMethod": {
          "status": "draft",
          "type": "string",
          "description": "Information on how the yield measurement of the dataset was generated.",
          "display_name": "Yield measurement method"
        },
        "dataSource": {
          "status": "release",
          "type": "string",
          "description": "Experiment type or data source from which the dataset was generated.",
          "display_name": "Data source"
        },
        "sourceRDI": {
          "status": "release",
          "type": "object",
          "description": "The original Research Data Infrastructure that the dataset was published by.",
          "display_name": "Source Research Data Infrastructure",
          "required": [
            "sourceRDIName",
            "sourceRDIURI"
          ],
          "properties": {
            "sourceRDIName": {
              "status": "release",
              "type": "string",
              "description": "The name of the original Research Data Infrastructure that the dataset was published by.",
              "display_name": "Source Research Data Infrastructure name"
            },
            "sourceRDIURI": {
              "status": "release",
              "type": "string",
              "description": "The landing page of the original Research Data Infrastructure that the dataset was published by.",
              "display_name": "Source Research Data Infrastructure URI"
            },
            "sourceRDIID": {
              "status": "in testing",
              "type": "object",
              "description": "A persistent identifier of the Research Data Infrastructure",
              "display_name": "Source Research Data Infrastructure ID",
              "properties": {
                "sourceRDIIDvalue": {
                  "status": "release",
                  "type": "string",
                  "description": "The value of a Research Data Infrastructure identifier",
                  "display_name": "Source Research Data Infrastructure identifier value"
                },
                "sourceRDIIDscheme": {
                  "status": "release",
                  "type": "string",
                  "description": "The scheme of a Research Data Infrastructure identifier",
                  "display_name": "Source Research Data Infrastructure identifier scheme"
                }
              }
            }
          }
        },
        "sourceDatasetURI": {
          "status": "release",
          "type": "string",
          "description": "A link to the original landing page of the dataset.",
          "display_name": "Source dataset link"
        },
        "license": {
          "status": "release",
          "type": "string",
          "description": "The terms under which this dataset has been published.",
          "display_name": "License"
        },
        "format": {
          "status": "release",
          "type": "array",
          "description": "The file format(s) of the dataset.",
          "display_name": "Format",
          "items": {
            "type": "string"
          }
        },
        "dateModified": {
          "status": "release",
          "type": "string",
          "description": "The date on which the Dataset was most recently modified or when the item's entry was modified.",
          "display_name": "Update date"
        },
        "spatialResolution": {
          "status": "release",
          "type": "string",
          "description": "Minimum spatial separation resolvable in a dataset, measured in meters.",
          "display_name": "Spatial resolution"
        },
        "versionNumber": {
          "status": "release",
          "type": "string",
          "description": "The version number of the dataset.",
          "display_name": "Version number"
        },
        "variableMeasured": {
          "status": "draft",
          "type": "array",
          "description": "Variables measured in a dataset",
          "display_name": "Measured variable(s)",
          "items": {
            "type": "object",
            "properties": {
              "variableMeasuredName": {
                "status": "draft",
                "type": "string",
                "description": "The name of a variable measured in the dataset.",
                "display_name": "Measured variable name"
              },
              "variableMeasuredAbbreviation": {
                "status": "draft",
                "type": "string",
                "description": "Abbreviation or short name of a variable measured in the dataset.",
                "display_name": "Measured variable abbreviation"
              },
              "variableMeasuredDescription": {
                "status": "draft",
                "type": "string",
                "description": "The description of a variable measured in the dataset.",
                "display_name": "Measured variable description"
              },
              "variableMeasuredURI": {
                "status": "draft",
                "type": "string",
                "description": "Reference to a resource (e.g. a terminology concept) representing a variable measured in the dataset.",
                "display_name": "Measured variable URI"
              },
              "variableMeasuredValue": {
                "status": "draft",
                "type": "string",
                "description": "The value of a variable measured in the dataset.",
                "display_name": "Measured variable value"
              },
              "variableMeasuredValueURI": {
                "status": "draft",
                "type": "string",
                "description": "Reference to a resource (e.g. a terminology concept) representing a value of a variable measured in the dataset.",
                "display_name": "Measured variable value URI"
              },
              "variableMeasuredUnit": {
                "status": "draft",
                "type": "string",
                "description": "The unit of a variable measured in the dataset.",
                "display_name": "Measured variable value unit"
              },
              "variableMeasuredUnitURI": {
                "status": "draft",
                "type": "string",
                "description": "Reference to a resource (e.g. a terminology concept) representing a unit of a variable measured in the dataset.",
                "display_name": "Measured variable value unit URI"
              },
              "variableMeasuredMeasurementTechnique": {
                "status": "draft",
                "type": "string",
                "description": "The technique used to measure a variable measured in the dataset.",
                "display_name": "Measured variable measurement technique"
              }
            }
          }
        }
      }
    },
    "geographic": {
      "status": "in testing",
      "type": "object",
      "description": "A set of geographic metadata",
      "display_name": "Geographic metadata",
      "properties": {
        "geographicCoverage": {
          "status": "release",
          "type": "array",
          "description": "Information on the geographic coverage of the data. Includes the total geographic scope of the data.",
          "display_name": "Geographic coverage(s)",
          "items": {
            "type": "object",
            "properties": {
              "city": {
                "status": "release",
                "type": "object",
                "description": "The name of the city that the Dataset is about. Use GeoNames for correct spelling and avoid abbreviations.",
                "display_name": "City",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "country": {
                "status": "release",
                "type": "object",
                "description": "The country or nation that the Dataset is about.",
                "display_name": "Country",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "state": {
                "status": "release",
                "type": "object",
                "description": "The state or province that the Dataset is about. Use GeoNames for correct spelling and avoid abbreviations.",
                "display_name": "State / Province",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              }
            }
          }
        },
        "geographicBoundingBox": {
          "status": "release",
          "type": "array",
          "description": "The fundamental geometric description for any Dataset that models geography is the geographic bounding box. It describes the minimum box, defined by west and east longitudes and north and south latitudes, which includes the largest geographic extent of the  Dataset's geographic coverage. This element is used in the first pass of a coordinate-based search. Inclusion of this element in the codebook is recommended, but is required if the bound polygon box is included.",
          "display_name": "Bounding box(es)",
          "items": {
            "type": "object",
            "properties": {
              "westLongitude": {
                "status": "release",
                "type": "object",
                "description": "Westernmost coordinate delimiting the geographic extent of the Dataset. A valid range of values,  expressed in decimal degrees, is -180.0 <= West  Bounding Longitude Value <= 180.0.",
                "display_name": "Bounding box western longitude",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "eastLongitude": {
                "status": "release",
                "type": "object",
                "description": "Easternmost coordinate delimiting the geographic extent of the Dataset. A valid range of values,  expressed in decimal degrees, is -180.0 <= East Bounding Longitude Value <= 180.0.",
                "display_name": "Bounding box eastern longitude",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "northLatitude": {
                "status": "release",
                "type": "object",
                "description": "Northernmost coordinate delimiting the geographic extent of the Dataset. A valid range of values,  expressed in decimal degrees, is -90.0 <= North Bounding Latitude Value <= 90.0.",
                "display_name": "Bounding box northern latitude",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "southLatitude": {
                "status": "release",
                "type": "object",
                "description": "Southernmost coordinate delimiting the geographic extent of the Dataset. A valid range of values,  expressed in decimal degrees, is -90.0 <= South Bounding Latitude Value <= 90.0.",
                "display_name": "Bounding box southern latitude",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              }
            }
          }
        }
      }
    },
    "crop": {
      "status": "in testing",
      "type": "object",
      "description": "A set of metadata describing crops.",
      "display_name": "Crop(s)",
      "properties": {
        "crop": {
          "status": "in testing",
          "type": "array",
          "description": "A crop entity represents a sample of a speficic plant or group of plants, sharing the same taxonomic species, that are described in a dataset.",
          "display_name": "Crop(s)",
          "items": {
            "type": "object",
            "properties": {
              "cropSpecies": {
                "status": "in testing",
                "type": "object",
                "description": "Taxonomic crop species that is part of the dataset.",
                "display_name": "Species",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "cropSpeciesURI": {
                "status": "in testing",
                "type": "object",
                "description": "Reference to a resource (e.g. a terminology concept) representing a crop species that is part of the dataset.",
                "display_name": "Species URI",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "cropVariety": {
                "status": "in testing",
                "type": "array",
                "description": "A plant variety that is part of the dataset and that is a member of a defined group of plants, selected from within a species, with a common set of characteristics.",
                "display_name": "Variety",
                "items": {
                  "type": "object",
                  "required": [
                    "value",
                    "aiGenerated"
                  ],
                  "properties": {
                    "value": {
                      "type": "string"
                    },
                    "aiGenerated": {
                      "type": "boolean"
                    },
                    "aiConfidence": {
                      "type": "number"
                    },
                    "aiModelName": {
                      "type": "string"
                    },
                    "aiModelURI": {
                      "type": "string"
                    },
                    "aiEnrichmentTimestamp": {
                      "type": "string"
                    }
                  }
                }
              },
              "cropVarietyURI": {
                "status": "in testing",
                "type": "object",
                "description": "Reference to a resource (e.g. a terminology concept) representing a crop variety that is part of the dataset.",
                "display_name": "Variety URI",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "cropSowingDate": {
                "status": "in testing",
                "type": "object",
                "description": "Date of sowing when the described crop was planted.",
                "display_name": "Sowing date",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "cropHarvestingDate": {
                "status": "in testing",
                "type": "object",
                "description": "Date when the described crop was harvested.",
                "display_name": "Harvesting date",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "cropPestName": {
                "status": "draft",
                "type": "object",
                "description": "Name of a pest (e.g. insects, fungi, microorganisms) that has affected a crop.",
                "display_name": "Pest name",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "cropPestURI": {
                "status": "draft",
                "type": "object",
                "description": "Reference to a resource (e.g. a terminology concept) representing a pest that is part of the dataset.",
                "display_name": "Pest URI",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              }
            }
          }
        }
      }
    },
    "soil": {
      "status": "in testing",
      "type": "object",
      "description": "A set of metadata describing soils.",
      "display_name": "Soil(s)",
      "properties": {
        "soil": {
          "status": "in testing",
          "type": "array",
          "description": "A soil entity represents a speficic soil sample, that is described in a dataset, representative for a bigger unit of land.",
          "display_name": "Soil(s)",
          "items": {
            "type": "object",
            "properties": {
              "soilTexture": {
                "status": "in testing",
                "type": "object",
                "description": "Indication of relative contents of particles in the soil described in the dataset.",
                "display_name": "Texture",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "soilTextureURI": {
                "status": "in testing",
                "type": "object",
                "description": "Reference to a resource (e.g. a terminology concept) representing a soil texture that is part of the dataset.",
                "display_name": "Texture URI",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "soilReferenceGroup": {
                "status": "in testing",
                "type": "object",
                "description": "Reference Soil Groups are distinguished by the presence (or absence) of specific diagnostic horizons, properties and/or materials.",
                "display_name": "Reference soil group",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "soilReferenceGroupURI": {
                "status": "in testing",
                "type": "object",
                "description": "Reference to a resource (e.g. a terminology concept) representing a soil reference group that is part of the dataset.",
                "display_name": "Reference soil group URI",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "soilPH": {
                "status": "in testing",
                "type": "object",
                "description": "Hydrogen ion concentration in the soil.",
                "display_name": "pH value",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "soilBulkDensity": {
                "status": "in testing",
                "type": "object",
                "description": "The mass of material particles divided by the bulk volume in g/cm³.",
                "display_name": "Bulk density",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "soilDepth": {
                "status": "in testing",
                "type": "object",
                "description": "The depth at which a sample of soil is collected during a soil sampling process in centimeters.",
                "display_name": "Sampling depth",
                "properties": {
                  "soilTopDepth": {
                    "status": "in testing",
                    "type": "object",
                    "description": "The top depth at which a sample of soil is collected during a soil sampling process.",
                    "display_name": "Sampling top depth",
                    "required": [
                      "value",
                      "aiGenerated"
                    ],
                    "properties": {
                      "value": {
                        "type": "string"
                      },
                      "aiGenerated": {
                        "type": "boolean"
                      },
                      "aiConfidence": {
                        "type": "number"
                      },
                      "aiModelName": {
                        "type": "string"
                      },
                      "aiModelURI": {
                        "type": "string"
                      },
                      "aiEnrichmentTimestamp": {
                        "type": "string"
                      }
                    }
                  },
                  "soilBottomDepth": {
                    "status": "in testing",
                    "type": "object",
                    "description": "The bottom depth at which a sample of soil is collected during a soil sampling process.",
                    "display_name": "Sampling bottom depth",
                    "required": [
                      "value",
                      "aiGenerated"
                    ],
                    "properties": {
                      "value": {
                        "type": "string"
                      },
                      "aiGenerated": {
                        "type": "boolean"
                      },
                      "aiConfidence": {
                        "type": "number"
                      },
                      "aiModelName": {
                        "type": "string"
                      },
                      "aiModelURI": {
                        "type": "string"
                      },
                      "aiEnrichmentTimestamp": {
                        "type": "string"
                      }
                    }
                  }
                }
              },
              "soilAvailableWaterContent": {
                "status": "in testing",
                "type": "object",
                "description": "Quantity of water present in the soil and usable by plants, classically defined as the difference between moisture at field capacity and moisture at wilting point in m³/m³.",
                "display_name": "Available water",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "soilOrganicCarbon": {
                "status": "in testing",
                "type": "object",
                "description": "Percentual share of solid carbon in the soil.",
                "display_name": "Organic carbon",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "soilTotalCarbon": {
                "status": "in testing",
                "type": "object",
                "description": "Percentual total amount of carbon in the soil.",
                "display_name": "Total carbon",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "soilTotalNitrogen": {
                "status": "in testing",
                "type": "object",
                "description": "Percentual total amount of nitrogen in the soil.",
                "display_name": "Total nitrogen",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              }
            }
          }
        }
      }
    },
    "plot": {
      "status": "in testing",
      "type": "object",
      "description": "A set of metadata describing plots.",
      "display_name": "Plot(s)",
      "properties": {
        "plot": {
          "status": "in testing",
          "type": "array",
          "description": "A plot of land is an area of land with a particular ownership, land use, or other characteristic. A plot is frequently used as the basis for a cadastre or land registration system.",
          "display_name": "Plot(s)",
          "items": {
            "type": "object",
            "properties": {
              "plotLocation": {
                "status": "in testing",
                "description": "The geolocation of the plot.",
                "display_name": "Plot location",
                "type": "object",
                "properties": {
                  "plotLocationDescription": {
                    "type": "object",
                    "description": "A description of the plot's location",
                    "display_name": "Plot location description",
                    "required": [
                      "value",
                      "aiGenerated"
                    ],
                    "properties": {
                      "value": {
                        "type": "string"
                      },
                      "aiGenerated": {
                        "type": "boolean"
                      },
                      "aiConfidence": {
                        "type": "number"
                      },
                      "aiModelName": {
                        "type": "string"
                      },
                      "aiModelURI": {
                        "type": "string"
                      },
                      "aiEnrichmentTimestamp": {
                        "type": "string"
                      }
                    }
                  },
                  "plotLocationBoundingBox": {
                    "type": "object",
                    "properties": {
                      "plotLocationWestLongitude": {
                        "status": "in testing",
                        "type": "object",
                        "description": "Westernmost coordinate delimiting the geographic extent of the plot. A valid range of values,  expressed in decimal degrees, is -180.0 <= West  Bounding Longitude Value <= 180.0.",
                        "display_name": "Plot location bounding box western longitude",
                        "required": [
                          "value",
                          "aiGenerated"
                        ],
                        "properties": {
                          "value": {
                            "type": "string"
                          },
                          "aiGenerated": {
                            "type": "boolean"
                          },
                          "aiConfidence": {
                            "type": "number"
                          },
                          "aiModelName": {
                            "type": "string"
                          },
                          "aiModelURI": {
                            "type": "string"
                          },
                          "aiEnrichmentTimestamp": {
                            "type": "string"
                          }
                        }
                      },
                      "plotLocationEastLongitude": {
                        "status": "in testing",
                        "type": "object",
                        "description": "Easternmost coordinate delimiting the geographic extent of the plot. A valid range of values,  expressed in decimal degrees, is -180.0 <= East Bounding Longitude Value <= 180.0.",
                        "display_name": "Plot location bounding box eastern longitude",
                        "required": [
                          "value",
                          "aiGenerated"
                        ],
                        "properties": {
                          "value": {
                            "type": "string"
                          },
                          "aiGenerated": {
                            "type": "boolean"
                          },
                          "aiConfidence": {
                            "type": "number"
                          },
                          "aiModelName": {
                            "type": "string"
                          },
                          "aiModelURI": {
                            "type": "string"
                          },
                          "aiEnrichmentTimestamp": {
                            "type": "string"
                          }
                        }
                      },
                      "plotLocationNorthLatitude": {
                        "status": "in testing",
                        "type": "object",
                        "description": "Northernmost coordinate delimiting the geographic extent of the plot. A valid range of values,  expressed in decimal degrees, is -90.0 <= North Bounding Latitude Value <= 90.0.",
                        "display_name": "Plot location bounding box northern latitude",
                        "required": [
                          "value",
                          "aiGenerated"
                        ],
                        "properties": {
                          "value": {
                            "type": "string"
                          },
                          "aiGenerated": {
                            "type": "boolean"
                          },
                          "aiConfidence": {
                            "type": "number"
                          },
                          "aiModelName": {
                            "type": "string"
                          },
                          "aiModelURI": {
                            "type": "string"
                          },
                          "aiEnrichmentTimestamp": {
                            "type": "string"
                          }
                        }
                      },
                      "plotLocationSouthLatitude": {
                        "status": "in testing",
                        "type": "object",
                        "description": "Southernmost coordinate delimiting the geographic extent of the plot. A valid range of values,  expressed in decimal degrees, is -90.0 <= South Bounding Latitude Value <= 90.0.",
                        "display_name": "Plot location bounding box southern latitude",
                        "required": [
                          "value",
                          "aiGenerated"
                        ],
                        "properties": {
                          "value": {
                            "type": "string"
                          },
                          "aiGenerated": {
                            "type": "boolean"
                          },
                          "aiConfidence": {
                            "type": "number"
                          },
                          "aiModelName": {
                            "type": "string"
                          },
                          "aiModelURI": {
                            "type": "string"
                          },
                          "aiEnrichmentTimestamp": {
                            "type": "string"
                          }
                        }
                      }
                    }
                  }
                },
                "anyOf": [
                  {
                    "required": [
                      "plotLocationDescription"
                    ]
                  },
                  {
                    "required": [
                      "plotLocationBoundingBox"
                    ]
                  }
                ]
              },
              "plotCropYield": {
                "status": "in testing",
                "type": "object",
                "description": "The amount of plant crop (such as cereal, grain or legume) harvested per unit area for a given time in dt/ha.",
                "display_name": "Crop yield",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "plotElevation": {
                "status": "in testing",
                "type": "object",
                "description": "Altitude, like elevation, is the distance above sea level in meters.",
                "display_name": "Elevation",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "plotSize": {
                "status": "in testing",
                "type": "object",
                "description": "The size of a specific plot measured in m².",
                "display_name": "Plot size",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "plotSpatialReferenceSystem": {
                "status": "in testing",
                "type": "object",
                "description": "The spatial reference system (SRS) or coordinate reference system (CRS) used to express the geographic information of a plot.",
                "display_name": "Spatial reference system",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              }
            }
          }
        }
      }
    },
    "sensor": {
      "status": "draft",
      "type": "object",
      "description": "A set of metadata describing sensors.",
      "display_name": "Sensor(s)",
      "properties": {
        "sensor": {
          "status": "draft",
          "type": "array",
          "description": "A sensor entity represents a specific sensor, that is described in a dataset, or was used to create measurements in it.",
          "display_name": "Sensor(s)",
          "items": {
            "type": "object",
            "properties": {
              "sensorIsHostedBy": {
                "status": "draft",
                "type": "object",
                "description": "Relation between a sensor and the platform that it is mounted on or hosted by.",
                "display_name": "Is hosted by",
                "properties": {
                  "sensorPlatformType": {
                    "status": "draft",
                    "type": "object",
                    "description": "The specific type of a platform a sensor is hosted by.",
                    "display_name": "Platform type",
                    "required": [
                      "value",
                      "aiGenerated"
                    ],
                    "properties": {
                      "value": {
                        "type": "string"
                      },
                      "aiGenerated": {
                        "type": "boolean"
                      },
                      "aiConfidence": {
                        "type": "number"
                      },
                      "aiModelName": {
                        "type": "string"
                      },
                      "aiModelURI": {
                        "type": "string"
                      },
                      "aiEnrichmentTimestamp": {
                        "type": "string"
                      }
                    }
                  },
                  "sensorPlatformTypeURI": {
                    "status": "draft",
                    "type": "object",
                    "description": "Reference to a resource (e.g. a terminology concept) representing a platform type that is part of the dataset.",
                    "display_name": "Platform type URI",
                    "required": [
                      "value",
                      "aiGenerated"
                    ],
                    "properties": {
                      "value": {
                        "type": "string"
                      },
                      "aiGenerated": {
                        "type": "boolean"
                      },
                      "aiConfidence": {
                        "type": "number"
                      },
                      "aiModelName": {
                        "type": "string"
                      },
                      "aiModelURI": {
                        "type": "string"
                      },
                      "aiEnrichmentTimestamp": {
                        "type": "string"
                      }
                    }
                  },
                  "sensorPlatformModelName": {
                    "status": "draft",
                    "type": "object",
                    "description": "Name of a specific platform model.",
                    "display_name": "Platform model name",
                    "required": [
                      "value",
                      "aiGenerated"
                    ],
                    "properties": {
                      "value": {
                        "type": "string"
                      },
                      "aiGenerated": {
                        "type": "boolean"
                      },
                      "aiConfidence": {
                        "type": "number"
                      },
                      "aiModelName": {
                        "type": "string"
                      },
                      "aiModelURI": {
                        "type": "string"
                      },
                      "aiEnrichmentTimestamp": {
                        "type": "string"
                      }
                    }
                  },
                  "sensorPlatformManufacturerName": {
                    "status": "draft",
                    "type": "object",
                    "description": "Name of the manufacturer of a specific platform.",
                    "display_name": "Platform manufacturer name",
                    "required": [
                      "value",
                      "aiGenerated"
                    ],
                    "properties": {
                      "value": {
                        "type": "string"
                      },
                      "aiGenerated": {
                        "type": "boolean"
                      },
                      "aiConfidence": {
                        "type": "number"
                      },
                      "aiModelName": {
                        "type": "string"
                      },
                      "aiModelURI": {
                        "type": "string"
                      },
                      "aiEnrichmentTimestamp": {
                        "type": "string"
                      }
                    }
                  }
                }
              },
              "sensorActivityType": {
                "status": "draft",
                "type": "object",
                "description": "Describes if the sensor is an active or a passive sensor.",
                "display_name": "Activity type",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "sensorSensorType": {
                "status": "draft",
                "type": "object",
                "description": "Describes what type of information the sensor measures.",
                "display_name": "Sensor type",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "sensorBandCategory": {
                "status": "draft",
                "type": "object",
                "description": "Describes if a sensor uses single, multi or hyper spectral bands.",
                "display_name": "Band category",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "sensorSpectralBand": {
                "status": "draft",
                "type": "array",
                "description": "Describes a specific spectral band(s) of a sensor.",
                "display_name": "Spectral band(s)",
                "items": {
                  "type": "object",
                  "required": [
                    "value",
                    "aiGenerated"
                  ],
                  "properties": {
                    "value": {
                      "type": "string"
                    },
                    "aiGenerated": {
                      "type": "boolean"
                    },
                    "aiConfidence": {
                      "type": "number"
                    },
                    "aiModelName": {
                      "type": "string"
                    },
                    "aiModelURI": {
                      "type": "string"
                    },
                    "aiEnrichmentTimestamp": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "agriculturalProcess": {
      "status": "in testing",
      "type": "object",
      "description": "A set of metadata describing planned processes which occur in an agricultural field.",
      "display_name": "Agricultural process(es)",
      "properties": {
        "agriculturalProcess": {
          "type": "array",
          "status": "draft",
          "description": "An agricultural process entity represents a specific agricultural process, that is described in a dataset.",
          "display_name": "Agricultural process",
          "items": {
            "type": "object",
            "properties": {
              "agriculturalProcessName": {
                "status": "in testing",
                "type": "object",
                "description": "The name of a planned process which occurs in an agricultural field.",
                "display_name": "Agricultural process name",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              }
            }
          }
        }
      }
    },
    "chemicalSubstance": {
      "status": "draft",
      "type": "object",
      "description": "A set of metadata describing chemical substances such as fertilizers and pesticides.",
      "display_name": "Chemical substance(s)",
      "properties": {
        "chemicalSubstance": {
          "status": "draft",
          "type": "array",
          "description": "A specific chemical substance described in the dataset.",
          "display_name": "Chemical substance(s)",
          "items": {
            "type": "object",
            "properties": {
              "chemicalSubstanceName": {
                "status": "draft",
                "type": "object",
                "description": "The name of a chemical substance.",
                "display_name": "Name",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              },
              "chemicalSubstanceApprovalNumber": {
                "status": "draft",
                "type": "object",
                "description": "The approval number if a chemical substance registered by an approval agency.",
                "display_name": "Approval number",
                "required": [
                  "value",
                  "aiGenerated"
                ],
                "properties": {
                  "value": {
                    "type": "string"
                  },
                  "aiGenerated": {
                    "type": "boolean"
                  },
                  "aiConfidence": {
                    "type": "number"
                  },
                  "aiModelName": {
                    "type": "string"
                  },
                  "aiModelURI": {
                    "type": "string"
                  },
                  "aiEnrichmentTimestamp": {
                    "type": "string"
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "additionalProperties": false
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
