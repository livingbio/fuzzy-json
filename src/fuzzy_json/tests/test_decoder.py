import json
from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

from ..decoder import loads, repair_json


def test_repaired_json_simple_case(snapshot: SnapshotAssertion) -> None:
    assert snapshot(extension_class=JSONSnapshotExtension) == json.loads(repair_json("{}"))
    assert snapshot(extension_class=JSONSnapshotExtension) == json.loads(repair_json('{"foo": "bar"}'))
    assert snapshot(extension_class=JSONSnapshotExtension) == json.loads(repair_json('{"foo": "bar", "baz": "qux"}'))
    assert snapshot(extension_class=JSONSnapshotExtension) == json.loads(repair_json('{"foo": "bar", "baz": "qux", "quux": "corge"}'))
    # add more nested objects
    assert snapshot(extension_class=JSONSnapshotExtension) == json.loads(repair_json('{"foo": {"bar": "baz"}}'))
    assert snapshot(extension_class=JSONSnapshotExtension) == json.loads(repair_json('{"foo": {"bar": {"baz": "qux"}}}'))
    assert snapshot(extension_class=JSONSnapshotExtension) == json.loads(repair_json('{"foo": {"bar": {"baz": {"qux": "quux"}}}}'))


@pytest.mark.parametrize(
    "test_filename",
    (Path(__file__).parent / "test_data").glob("valid/*.json"),
    ids=lambda x: x.name,
)
def test_repaired_json_vaild_case(snapshot: SnapshotAssertion, test_filename: Path) -> None:
    content = test_filename.read_text()
    parsed_by_std_json = json.loads(content)

    parsed_by_fixed_json = json.loads(repair_json(content))
    assert snapshot(extension_class=JSONSnapshotExtension) == parsed_by_fixed_json
    assert parsed_by_fixed_json == parsed_by_std_json


@pytest.mark.parametrize(
    "test_filename",
    (Path(__file__).parent / "test_data").glob("invalid/*.jsonx"),
    ids=lambda x: x.name,
)
def test_repaired_json_invaild_case(snapshot: SnapshotAssertion, test_filename: Path) -> None:
    content = test_filename.read_text()
    result = loads(content, auto_repair=True)
    assert snapshot(extension_class=JSONSnapshotExtension) == result


def test_repaired_json_invalid_case_special(snapshot: SnapshotAssertion) -> None:
    content = '{"a": "\n"}'
    result = loads(content, auto_repair=True)
    assert snapshot(extension_class=JSONSnapshotExtension) == result
    assert json.loads(content, strict=False) == result


def test_repair_json_fail() -> None:
    with pytest.raises(json.decoder.JSONDecodeError) as _:
        # test that it will raise JSONDecodeError if it can't fix the JSON
        loads("{", auto_repair=True)


def test_missing_value_after_colon(snapshot: SnapshotAssertion) -> None:
    """Test handling of missing values after colon (e.g., {"key":})"""
    # Single missing value at end
    assert loads('{"missing_value":}') == {"missing_value": None}
    # Missing value with trailing comma
    assert loads('{"missing_value":,}') == {"missing_value": None}
    # Missing value in middle of object
    assert loads('{"a": 1, "missing_value":, "b": 2}') == {"a": 1, "missing_value": None, "b": 2}
    # Multiple missing values
    assert loads('{"x":, "y":}') == {"x": None, "y": None}
    # Nested object with missing value
    assert loads('{"obj": {"missing":}}') == {"obj": {"missing": None}}
