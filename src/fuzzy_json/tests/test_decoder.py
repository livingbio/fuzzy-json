import json
from pathlib import Path
from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion

from ..decoder import loads, repair_json


def load_repaired_json(json_str: str) -> dict[str, Any]:
    return json.loads(repair_json(json_str))


def test_repaired_json_simple_case(snapshot: SnapshotAssertion) -> None:
    assert snapshot == load_repaired_json("{}")
    assert snapshot == load_repaired_json('{"foo": "bar"}')
    assert snapshot == load_repaired_json('{"foo": "bar", "baz": "qux"}')
    assert snapshot == load_repaired_json('{"foo": "bar", "baz": "qux", "quux": "corge"}')
    # add more nested objects
    assert snapshot == load_repaired_json('{"foo": {"bar": "baz"}}')
    assert snapshot == load_repaired_json('{"foo": {"bar": {"baz": "qux"}}}')
    assert snapshot == load_repaired_json('{"foo": {"bar": {"baz": {"qux": "quux"}}}}')


@pytest.mark.parametrize(
    "test_filename",
    (Path(__file__).parent / "test_data").glob("vaild/*.json"),
    ids=lambda x: x.name,
)
def test_repaired_json_vaild_case(snapshot: SnapshotAssertion, test_filename: Path) -> None:
    content = test_filename.read_text()
    parsed_by_std_json = json.loads(content)

    parsed_by_fixed_json = load_repaired_json(content)
    assert snapshot == parsed_by_fixed_json
    assert parsed_by_fixed_json == parsed_by_std_json


@pytest.mark.parametrize(
    "test_filename",
    (Path(__file__).parent / "test_data").glob("invaild/*.jsonx"),
    ids=lambda x: x.name,
)
def test_repaired_json_invaild_case(snapshot: SnapshotAssertion, test_filename: Path) -> None:
    content = test_filename.read_text()
    result = load_repaired_json(content)
    assert snapshot == result


def test_repair_json_fail() -> None:
    with pytest.raises(json.decoder.JSONDecodeError) as e:
        # test that it will raise JSONDecodeError if it can't fix the JSON
        loads("{", auto_repair=True)
