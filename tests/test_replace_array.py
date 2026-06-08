from pathlib import Path

import pytest

from yamly.patch import Patch
from yamly.template import Template

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "replace_array"


@pytest.fixture
def base() -> Template:
    return Template.load(FIXTURES_DIR / "base.yaml")


@pytest.fixture
def patch() -> Patch:
    return Patch.load(FIXTURES_DIR / f"{FIXTURES_DIR.name}.patch.yaml")


def test_replace_array(base: Template, patch: Patch) -> None:
    expected = Template.load(FIXTURES_DIR / "result.yaml")
    base.apply(patch)
    assert base.documents == expected.documents
