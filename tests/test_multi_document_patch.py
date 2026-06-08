from pathlib import Path

import pytest

from yamlsed.patch import Patch
from yamlsed.template import Template

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "multi_document_patch"


@pytest.fixture
def base() -> Template:
    return Template.load(FIXTURES_DIR / "base.yaml")


@pytest.fixture
def patch() -> Patch:
    return Patch.load(FIXTURES_DIR / f"{FIXTURES_DIR.name}.patch.yaml")


def test_multi_document_patch(base: Template, patch: Patch) -> None:
    expected = Template.load(FIXTURES_DIR / "result.yaml")
    assert len(patch) == 2
    base.apply(patch)
    assert base.documents == expected.documents
