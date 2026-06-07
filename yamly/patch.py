from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

WILDCARD = "*"


class Patch:
    """A validated YAML patch document with match selectors and patch payload."""

    def __init__(self, document: dict) -> None:
        self._document = self._validate(document)

    def __str__(self) -> str:
        """Return a string representation of the patch."""
        return yaml.dump(self._document, sort_keys=False)

    @classmethod
    def load(cls, path: str | Path) -> Patch:
        """Load and validate a patch from a YAML file."""
        with Path(path).open(encoding="utf-8") as stream:
            documents = list(yaml.safe_load_all(stream))

        if len(documents) != 1:
            raise ValueError("Patch must contain exactly one document")

        return cls(documents[0])

    @staticmethod
    def _validate(document: Any) -> dict:
        """Raises an error if the patch is invalid."""
        if "match" not in document:
            raise ValueError("Patch must contain a match key")

        if "patch" not in document:
            raise ValueError("Patch must contain a patch key")

        if not isinstance(document["match"], list):
            raise ValueError("Match must be a list")

        if not isinstance(document["patch"], dict):
            raise ValueError("Patch must be a dictionary")

        return document

    def _check_query(self, document: Any, query: Any) -> bool:
        """Check if a document matches a query."""
        if isinstance(query, dict):
            if not isinstance(document, dict):
                return False

            for key, value in query.items():
                if key not in document:
                    return False

                if not self._check_query(document[key], value):
                    return False

            return True

        if isinstance(query, list):
            if not isinstance(document, list) or len(document) != len(query):
                return False

            return all(
                self._check_query(document_item, query_item) for document_item, query_item in zip(document, query)
            )

        return document == query

    def matches(self, document: Any) -> bool:
        """Check if a document matches this patch's selectors."""
        for query in self._document["match"]:
            if self._check_query(document, query):
                return True

        return False

    def apply(self, document: dict) -> dict:
        """Apply patch mutations to a document and return the result."""
        result = copy.deepcopy(document)

        for key, value in self.patch.items():
            field, operation = self._parse_key(key)
            self._apply_operation(result, field, operation, value)

        return result

    @staticmethod
    def _parse_key(key: str) -> tuple[str, str]:
        if key.endswith("-?"):
            return key[:-2], "delete_partial"

        if key.endswith("+"):
            return key[:-1], "append"

        if key.endswith("-"):
            return key[:-1], "delete"

        return key, "replace"

    def _apply_operation(self, document: dict, field: str, operation: str, value: Any) -> None:
        match operation:
            case "replace":
                document[field] = copy.deepcopy(value)

            case "append":
                if field not in document:
                    document[field] = []

                if not isinstance(document[field], list):
                    raise ValueError(f"Cannot append to non-array field {field!r}")

                if not isinstance(value, list):
                    raise ValueError(f"Append value for {field!r} must be a list")

                document[field].extend(copy.deepcopy(value))

            case "delete":
                self._apply_delete(document, field, value, partial=False)

            case "delete_partial":
                self._apply_delete(document, field, value, partial=True)

            case _:
                raise ValueError(f"Unknown patch operation {operation!r}")

    def _apply_delete(self, document: dict, field: str, value: Any, *, partial: bool) -> None:
        if value == WILDCARD:
            document.pop(field, None)
            return

        if value is None:
            if document.get(field) is None:
                document.pop(field, None)
            return

        if isinstance(value, list):
            if field not in document or not isinstance(document[field], list):
                return

            match = self._partial_match if partial else self._exact_match
            selectors = value

            document[field] = [
                element for element in document[field] if not any(match(element, selector) for selector in selectors)
            ]
            return

        if field in document and document[field] == value:
            del document[field]

    @staticmethod
    def _exact_match(element: Any, selector: Any) -> bool:
        if not isinstance(element, dict) or not isinstance(selector, dict):
            return False

        if set(element.keys()) != set(selector.keys()):
            return False

        return all(element[key] == selector[key] for key in selector)

    @staticmethod
    def _partial_match(element: Any, selector: Any) -> bool:
        if not isinstance(element, dict) or not isinstance(selector, dict):
            return False

        return all(key in element and element[key] == value for key, value in selector.items())

    @property
    def match(self) -> list:
        return self._document["match"]

    @property
    def patch(self) -> dict:
        return self._document["patch"]
