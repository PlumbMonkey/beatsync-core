import jsonschema
import os
import json

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "schema", "v0_1.json")
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    _SCHEMA = jsonschema.Draft7Validator(json.load(f))

def validate_contract(data):
    _SCHEMA.validate(data)
