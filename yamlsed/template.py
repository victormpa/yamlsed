from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from yamlsed.patch import Patch


class Template(list):
    """A YAML template backed by one or more parsed documents."""

    def __init__(self, documents: list[Any] | None = None) -> None:
        super().__init__(documents or [])

    @property
    def documents(self) -> list[Any]:
        return self

    def __str__(self) -> str:
        """Return a string representation of the template."""
        return yaml.dump(list(self), sort_keys=False)

    @classmethod
    def load(cls, path: str | Path) -> Template:
        """Load YAML from a file. Multi-document files are supported."""
        with Path(path).open(encoding="utf-8") as stream:
            documents = list(yaml.safe_load_all(stream))
        return cls(documents)

    def save(self, path: str | Path) -> None:
        """Write this template's documents to a YAML file."""
        with Path(path).open("w", encoding="utf-8") as stream:
            yaml.safe_dump_all(
                list(self),
                stream,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
            )

    def apply(self, patch: Patch) -> Template:
        """Apply a patch to the template."""
        for patch_doc in patch:
            fragment = Patch(patch_doc)
            for i, document in enumerate(self.documents):
                if fragment.matches(document):
                    self.documents[i] = fragment.eval(document)

        return self
