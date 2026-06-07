import pytest

from yamly.patch import Patch


def test_append_to_non_array_field_raises() -> None:
    patch = Patch({"match": [{}], "patch": {"version+": [1]}})
    with pytest.raises(ValueError, match="non-array"):
        patch.apply({"version": 1})


def test_append_non_list_value_raises() -> None:
    patch = Patch({"match": [{}], "patch": {"tags+": "single"}})
    with pytest.raises(ValueError, match="must be a list"):
        patch.apply({"tags": []})
