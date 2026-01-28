import json
import os
import pytest
import jsonschema

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema_v0_1.json")

@pytest.fixture
def schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)

def test_output_schema(schema):
    # Example output for validation
    output_path = os.path.join(os.path.dirname(__file__), "example_output.json")
    if not os.path.exists(output_path):
        pytest.skip("No example_output.json present")
    with open(output_path) as f:
        data = json.load(f)
    jsonschema.validate(instance=data, schema=schema)
