from pathlib import Path

from yamlsed.patch import Patch
from yamlsed.selector import Selector
from yamlsed.template import Template

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "append_array"


def test_template_str() -> None:
    template = Template.load(FIXTURES_DIR / "base.yaml")
    rendered = str(template)
    assert "example" in rendered


def test_template_save_roundtrip(tmp_path: Path) -> None:
    template = Template.load(FIXTURES_DIR / "base.yaml")
    path = tmp_path / "out.yaml"
    template.save(path)
    reloaded = Template.load(path)
    assert reloaded.documents == template.documents


def test_patch_str() -> None:
    patch = Patch.load(FIXTURES_DIR / f"{FIXTURES_DIR.name}.patch.yaml")
    rendered = str(patch)
    assert "match" in rendered


def test_patch_match_property() -> None:
    patch = Patch.load(FIXTURES_DIR / f"{FIXTURES_DIR.name}.patch.yaml")
    assert isinstance(patch.match, list)
    assert isinstance(patch.match[0], Selector)
    assert patch.match[0].query["name"] == "example"
