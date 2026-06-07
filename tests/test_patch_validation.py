from pathlib import Path

import pytest

from yamly.patch import Patch


def test_patch_rejects_missing_match_key() -> None:
    with pytest.raises(ValueError, match="match key"):
        Patch({"patch": {}})


def test_patch_rejects_missing_patch_key() -> None:
    with pytest.raises(ValueError, match="patch key"):
        Patch({"match": []})


def test_patch_rejects_non_list_match() -> None:
    with pytest.raises(ValueError, match="Match must be a list"):
        Patch({"match": "not-a-list", "patch": {}})


def test_patch_rejects_non_dict_patch() -> None:
    with pytest.raises(ValueError, match="Patch must be a dictionary"):
        Patch({"match": [], "patch": []})


def test_patch_load_rejects_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one document"):
        Patch.load(path)


def test_patch_load_rejects_multi_document_file(tmp_path: Path) -> None:
    path = tmp_path / "multi.yaml"
    path.write_text("---\nmatch: []\npatch: {}\n---\nmatch: []\npatch: {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one document"):
        Patch.load(path)
