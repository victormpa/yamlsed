from pathlib import Path

import pytest

from yamlsed.patch import Patch


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
    path = tmp_path / "empty.patch.yaml"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="at least one document"):
        Patch.load(path)


def test_patch_load_accepts_multi_document_file(tmp_path: Path) -> None:
    path = tmp_path / "multi.patch.yaml"
    path.write_text("---\nmatch: []\npatch: {}\n---\nmatch: []\npatch: {}\n", encoding="utf-8")
    loaded = Patch.load(path)
    assert len(loaded) == 2
    assert loaded[0]["match"] == []
    assert loaded[1]["match"] == []


def test_patch_load_rejects_none_document(tmp_path: Path) -> None:
    path = tmp_path / "trailing.patch.yaml"
    path.write_text("---\nmatch: []\npatch: {}\n---\n", encoding="utf-8")
    with pytest.raises(ValueError, match="empty documents"):
        Patch.load(path)


def test_patch_load_rejects_non_patch_filename(tmp_path: Path) -> None:
    path = tmp_path / "patch.yaml"
    path.write_text("match: []\npatch: {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be named"):
        Patch.load(path)


def test_patch_load_rejects_empty_patch_prefix(tmp_path: Path) -> None:
    path = tmp_path / ".patch.yaml"
    path.write_text("match: []\npatch: {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be named"):
        Patch.load(path)


def test_patch_load_accepts_meaningful_patch_filename(tmp_path: Path) -> None:
    path = tmp_path / "approve.patch.yaml"
    path.write_text("match: []\npatch: {}\n", encoding="utf-8")
    assert isinstance(Patch.load(path), Patch)
