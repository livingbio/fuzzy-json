import json
from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion

from ..decoder import loads, repair_json


def test_repaired_json_simple_case(snapshot: SnapshotAssertion) -> None:
    assert snapshot == json.loads(repair_json("{}"))
    assert snapshot == json.loads(repair_json('{"foo": "bar"}'))
    assert snapshot == json.loads(repair_json('{"foo": "bar", "baz": "qux"}'))
    assert snapshot == json.loads(repair_json('{"foo": "bar", "baz": "qux", "quux": "corge"}'))
    # add more nested objects
    assert snapshot == json.loads(repair_json('{"foo": {"bar": "baz"}}'))
    assert snapshot == json.loads(repair_json('{"foo": {"bar": {"baz": "qux"}}}'))
    assert snapshot == json.loads(repair_json('{"foo": {"bar": {"baz": {"qux": "quux"}}}}'))


@pytest.mark.parametrize(
    "test_filename",
    (Path(__file__).parent / "test_data").glob("valid/*.json"),
    ids=lambda x: x.name,
)
def test_repaired_json_vaild_case(snapshot: SnapshotAssertion, test_filename: Path) -> None:
    content = test_filename.read_text()
    parsed_by_std_json = json.loads(content)

    parsed_by_fixed_json = json.loads(repair_json(content))
    assert snapshot == parsed_by_fixed_json
    assert parsed_by_fixed_json == parsed_by_std_json


@pytest.mark.parametrize(
    "test_filename",
    (Path(__file__).parent / "test_data").glob("invalid/*.jsonx"),
    ids=lambda x: x.name,
)
def test_repaired_json_invaild_case(snapshot: SnapshotAssertion, test_filename: Path) -> None:
    content = test_filename.read_text()
    result = loads(content, auto_repair=True)
    assert snapshot == result


def test_repaired_json_invalid_case_special(snapshot: SnapshotAssertion) -> None:
    content = '{"a": "\n"}'
    result = loads(content, auto_repair=True)
    assert snapshot == result
    assert json.loads(content, strict=False) == result


def test_repair_json_fail() -> None:
    with pytest.raises(json.decoder.JSONDecodeError) as _:
        # test that it will raise JSONDecodeError if it can't fix the JSON
        loads("{", auto_repair=True)
