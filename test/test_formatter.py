import json

from src.formatter import format_policy_json


def test_extract_from_fenced_json():
    raw = """
    Some text
    ```json
    {"policy": [{"sourceFunction": {"name": "foo", "events": ["E1"]}, "destinationFunction": {"name": "bar"}}]}
    ```
    """

    out = format_policy_json(raw)
    assert "policy" in out
    assert isinstance(out["policy"], list)
    assert out["policy"][0]["sourceFunction"]["name"] == "foo"


def test_merge_duplicates():
    raw = (
        '{"policy": ['
        '{"sourceFunction": {"name": "x", "events": ["A"]},'
        '"destinationFunction": {"name": "y"}},'
        '{"sourceFunction": {"name": "x", "events": ["B"]},'
        '"destinationFunction": {"name": "y"}}]}'
    )

    out = format_policy_json(raw)
    assert len(out["policy"]) == 1
    events = out["policy"][0]["sourceFunction"]["events"]
    assert "A" in events and "B" in events
