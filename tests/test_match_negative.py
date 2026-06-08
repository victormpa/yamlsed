from pathlib import Path

import pytest

from yamlsed.patch import Patch
from yamlsed.template import Template

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "no_match"


@pytest.fixture
def base() -> Template:
    return Template.load(FIXTURES_DIR / "base.yaml")


@pytest.fixture
def patch() -> Patch:
    return Patch.load(FIXTURES_DIR / f"{FIXTURES_DIR.name}.patch.yaml")


def test_no_match_is_no_op(base: Template, patch: Patch) -> None:
    expected = Template.load(FIXTURES_DIR / "result.yaml")
    base.apply(patch)
    assert base.documents == expected.documents


def test_matches_returns_false_when_document_is_not_dict() -> None:
    patch = Patch({"match": [{"metadata": {"key": 1}}], "patch": {}})
    assert patch.matches({"metadata": "string"}) is False


def test_matches_returns_false_when_key_missing() -> None:
    patch = Patch({"match": [{"name": "x", "extra": 1}], "patch": {}})
    assert patch.matches({"name": "x"}) is False


def test_matches_returns_false_when_nested_value_mismatch() -> None:
    patch = Patch({"match": [{"labels": {"os": "linux"}}], "patch": {}})
    assert patch.matches({"labels": {"os": "windows"}}) is False


def test_matches_returns_false_when_list_selector_on_non_list() -> None:
    patch = Patch({"match": [{"tags": ["yaml", "templates"]}], "patch": {}})
    assert patch.matches({"tags": "not-a-list"}) is False


def test_matches_returns_false_when_list_selector_wrong_length() -> None:
    patch = Patch({"match": [{"tags": ["yaml", "templates"]}], "patch": {}})
    assert patch.matches({"tags": ["yaml"]}) is False


def test_matches_returns_false_when_list_selector_item_mismatch() -> None:
    patch = Patch({"match": [{"tags": ["yaml", "templates"]}], "patch": {}})
    assert patch.matches({"tags": ["yaml", "other"]}) is False


def test_matches_returns_true_for_list_selector() -> None:
    patch = Patch({"match": [{"tags": ["yaml", "templates"]}], "patch": {}})
    assert patch.matches({"tags": ["yaml", "templates"]}) is True


def test_matches_returns_false_when_no_selector_matches() -> None:
    patch = Patch({"match": [{"name": "other"}], "patch": {"version": 2}})
    assert patch.matches({"name": "example", "version": 1}) is False
