import pytest

from yamlsed.patch import Patch


def test_delete_exact_skips_non_dict_elements() -> None:
    patch = Patch({"match": [{}], "patch": {"values-": [{"key": 1}]}})
    result = patch.eval({"values": [1, 2]})
    assert result == {"values": [1, 2]}


def test_delete_partial_skips_non_dict_elements() -> None:
    patch = Patch({"match": [{}], "patch": {"values-?": [{"key": 1}]}})
    result = patch.eval({"values": [1, 2]})
    assert result == {"values": [1, 2]}


def test_unknown_operation_raises() -> None:
    patch = Patch({"match": [], "patch": {}})
    with pytest.raises(ValueError, match="Unknown patch operation"):
        patch._apply_operation({}, "field", "bogus", None, original_document={})
