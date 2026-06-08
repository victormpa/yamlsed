import pytest

from yamly.patch import Patch


def test_append_to_non_array_field_raises() -> None:
    patch = Patch({"match": [{}], "patch": {"version+": [1]}})
    with pytest.raises(ValueError, match="non-array"):
        patch.eval({"version": 1})


def test_append_non_list_non_dict_value_raises() -> None:
    patch = Patch({"match": [{}], "patch": {"tags+": "single"}})
    with pytest.raises(ValueError, match="must be a list or dict"):
        patch.eval({"tags": []})


def test_append_to_non_object_field_raises() -> None:
    patch = Patch({"match": [{}], "patch": {"version+": {"key": "value"}}})
    with pytest.raises(ValueError, match="non-object"):
        patch.eval({"version": 1})


def test_append_partial_suffix_missing_object_key_skips() -> None:
    patch = Patch({"match": [{}], "patch": {"labels+?": {"key": "value"}}})
    assert patch.eval({"name": "example"}) == {"name": "example"}
