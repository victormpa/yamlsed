from pathlib import Path

import pytest

from yamlsed.discover import discover
from yamlsed.patch import Patch
from yamlsed.template import Template


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    (root / "base.yaml").write_text("name: base\n", encoding="utf-8")
    (root / "changes.patch.yaml").write_text("match: []\npatch: {}\n", encoding="utf-8")
    (root / "notes.txt").write_text("ignored\n", encoding="utf-8")

    nested = root / "models"
    nested.mkdir()
    (nested / "model.yaml").write_text("name: model\n", encoding="utf-8")

    empty = root / "empty"
    empty.mkdir()

    return root


def test_discover_loads_yaml_and_patch_files(tree: Path) -> None:
    result = discover(str(tree))

    assert set(result) == {"base.yaml", "changes.patch.yaml", "models"}
    assert isinstance(result["base.yaml"], Template)
    assert result["base.yaml"].documents == [{"name": "base"}]
    assert isinstance(result["changes.patch.yaml"], Patch)
    assert result["changes.patch.yaml"]["match"] == []
    assert isinstance(result["models"]["model.yaml"], Template)
    assert result["models"]["model.yaml"].documents == [{"name": "model"}]


def test_discover_ignores_non_yaml_files(tree: Path) -> None:
    result = discover(str(tree))
    assert "notes.txt" not in result


def test_discover_omits_empty_directories(tree: Path) -> None:
    result = discover(str(tree))
    assert "empty" not in result


def test_discover_default_depth_is_unlimited(tree: Path) -> None:
    result = discover(str(tree))
    assert "models" in result
    assert "model.yaml" in result["models"]


def test_discover_depth_zero_returns_empty_tree(tree: Path) -> None:
    assert discover(str(tree), depth=0) == {}


def test_discover_depth_one_includes_only_top_level(tree: Path) -> None:
    result = discover(str(tree), depth=1)
    assert set(result) == {"base.yaml", "changes.patch.yaml"}
    assert "models" not in result


def test_discover_depth_two_includes_one_nested_level(tree: Path) -> None:
    result = discover(str(tree), depth=2)
    assert set(result) == {"base.yaml", "changes.patch.yaml", "models"}
    assert "model.yaml" in result["models"]
