import pytest
import json
import os
from beatsync_core.utils import validate

FIXTURES = [
    os.path.join(os.path.dirname(__file__), "..", "expected", "click_120.beatsync.json"),
    os.path.join(os.path.dirname(__file__), "..", "expected", "midi_basic_100.beatsync.json"),
]

@pytest.mark.parametrize("json_path", FIXTURES)
def test_contract_schema(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    validate.validate_contract(data)
