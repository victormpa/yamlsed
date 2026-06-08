from pathlib import Path

import pytest

from yamlsed.patch import Patch
from yamlsed.template import Template

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "wildcard_match"


@pytest.fixture
def base() -> Template:
    return Template.load(FIXTURES_DIR / "base.yaml")


@pytest.fixture
def patch() -> Patch:
    return Patch.load(FIXTURES_DIR / f"{FIXTURES_DIR.name}.patch.yaml")


def test_wildcard_match(base: Template, patch: Patch) -> None:
    expected = Template.load(FIXTURES_DIR / "result.yaml")
    base.apply(patch)
    assert base.documents == expected.documents


def test_matches_returns_true_for_wildcard_selector() -> None:
    patch = Patch({"match": [{"labels": {"os": "*"}}], "patch": {}})
    assert patch.matches({"labels": {"os": "linux"}}) is True
    assert patch.matches({"labels": {"os": "windows"}}) is True
