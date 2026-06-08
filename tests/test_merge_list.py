from pathlib import Path

import pytest

from yamlsed.patch import Patch
from yamlsed.template import Template

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "merge_list"


@pytest.fixture
def base() -> Template:
    return Template.load(FIXTURES_DIR / "base.yaml")


@pytest.fixture
def patch() -> Patch:
    return Patch.load(FIXTURES_DIR / f"{FIXTURES_DIR.name}.patch.yaml")


def test_merge_list(base: Template, patch: Patch) -> None:
    expected = Template.load(FIXTURES_DIR / "result.yaml")
    base.apply(patch)
    assert base.documents == expected.documents


def test_merge_value_scalar_returns_deepcopy() -> None:
    patch = Patch({"match": [], "patch": {}})
    assert patch._merge_value("original", "replacement", original="original") == "replacement"
