from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

import yaml

from yamlsed.functions import eval_expression, expression_context, is_expression
from yamlsed.selector import WILDCARD, Selector

PATCH_SUFFIX = ".patch.yaml"
_BARE_EXPRESSION_PATTERN = re.compile(
    r"^(\s*[\w+-?]+:)\s+(\{\{.+?\}\})\s*$",
    re.MULTILINE,
)


class Patch(list):
    """A validated YAML patch file with one or more match/patch documents."""

    def __init__(self, documents: dict | list[dict] | None = None) -> None:
        if isinstance(documents, dict):
            docs = [documents]
        else:
            docs = list(documents or [])

        if not docs:
            raise ValueError("Patch must contain at least one document")

        super().__init__(self._validate(doc) for doc in docs)

    def __getitem__(self, key: int | slice | str) -> Any:
        if isinstance(key, (int, slice)):
            return super().__getitem__(key)
        return self._doc[key]

    def __str__(self) -> str:
        """Return a string representation of the patch."""
        return yaml.dump_all(list(self), sort_keys=False)

    @property
    def _doc(self) -> dict:
        return self[0]

    @classmethod
    def load(cls, path: str | Path) -> Patch:
        """Load and validate a patch from a ``{name}.patch.yaml`` file."""
        path = Path(path)
        cls._validate_name(path)

        with path.open(encoding="utf-8") as stream:
            source = cls._preprocess_source(stream.read())
            documents = list(yaml.safe_load_all(source))

        if not documents:
            raise ValueError("Patch must contain at least one document")

        if any(doc is None for doc in documents):
            raise ValueError("Patch must not contain empty documents")

        return cls(documents)

    @staticmethod
    def _preprocess_source(source: str) -> str:
        def quote_expression(match: re.Match[str]) -> str:
            key_part = match.group(1)
            expression = match.group(2).replace("'", "''")
            return f"{key_part} '{expression}'"

        return _BARE_EXPRESSION_PATTERN.sub(quote_expression, source)

    @staticmethod
    def _validate_name(path: Path) -> None:
        """Raises an error unless the file is named ``{name}.patch.yaml``."""
        name = path.name
        if not name.endswith(PATCH_SUFFIX) or len(name) <= len(PATCH_SUFFIX):
            raise ValueError(f"Patch file must be named '{{name}}.patch.yaml' with a meaningful name, got {name!r}")

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

    def matches(self, document: Any) -> bool:
        """Check if a document matches this patch's selectors."""
        return any(selector.eval(document) for selector in self.match)

    def eval(self, document: dict) -> dict:
        """Apply patch mutations to a document and return the result."""
        original_document = copy.deepcopy(document)
        result = copy.deepcopy(document)

        for key, value in self.patch.items():
            field, operation = self._parse_key(key)
            self._apply_operation(result, field, operation, value, original_document=original_document)

        return result

    def _resolve(self, value: Any, *, original: Any, field: str) -> Any:
        with expression_context(original, field):
            if isinstance(value, str) and is_expression(value):
                return eval_expression(value)

            if isinstance(value, dict):
                parent_original = original.get(field) if isinstance(original, dict) else None
                if not isinstance(parent_original, dict):
                    parent_original = {}
                return {key: self._resolve(item, original=parent_original, field=key) for key, item in value.items()}

            if isinstance(value, list):
                return [self._resolve(item, original=original, field=field) for item in value]

            return copy.deepcopy(value)

    @staticmethod
    def _parse_key(key: str) -> tuple[str, str]:
        if key.endswith("-?"):
            return key[:-2], "delete_partial"

        if key.endswith("+?"):
            return key[:-2], "append_partial"

        if key.endswith("+"):
            return key[:-1], "append"

        if key.endswith("-"):
            return key[:-1], "delete"

        return key, "replace"

    @staticmethod
    def _is_append_key(key: str) -> bool:
        return key.endswith("+") and not key.endswith("+?")

    @staticmethod
    def _is_append_partial_key(key: str) -> bool:
        return key.endswith("+?")

    @classmethod
    def _has_operation_suffix(cls, key: str) -> bool:
        return key.endswith(("-?", "-", "+")) or key.endswith("+?")

    @classmethod
    def _contains_append_suffix(cls, value: Any) -> bool:
        if isinstance(value, dict):
            if any(cls._is_append_key(key) or cls._is_append_partial_key(key) for key in value):
                return True
            return any(cls._contains_append_suffix(item) for item in value.values())
        if isinstance(value, list):
            return any(cls._contains_append_suffix(item) for item in value)
        return False

    def _merge_dict(self, into: dict, updates: dict, *, original: dict) -> None:
        for key, value in updates.items():
            into[key] = self._resolve(value, original=original, field=key)

    @staticmethod
    def _selector_keys(patch_item: dict) -> dict:
        return {key: value for key, value in patch_item.items() if not Patch._has_operation_suffix(key)}

    def _find_partial_match_indices(self, elements: list, selector: dict) -> list[int]:
        return [index for index, element in enumerate(elements) if self._partial_match(element, selector)]

    def _apply_append(self, container: dict, field: str, value: Any, *, guarded: bool, original: Any) -> None:
        if isinstance(value, dict):
            if guarded and field not in container:
                return
            if field not in container:
                container[field] = {}
            elif not isinstance(container[field], dict):
                raise ValueError(f"Cannot append to non-object field {field!r}")
            original_sub = original if isinstance(original, dict) else {}
            self._merge_dict(container[field], value, original=original_sub)
        elif isinstance(value, list):
            if field not in container:
                container[field] = []
            elif not isinstance(container[field], list):
                raise ValueError(f"Cannot append to non-array field {field!r}")
            container[field].extend(self._resolve(value, original=original, field=field))
        else:
            raise ValueError(f"Append value for {field!r} must be a list or dict")

    def _merge_value(self, target: Any, patch: Any, *, original: Any) -> Any:
        if isinstance(patch, dict):
            result = copy.deepcopy(target) if isinstance(target, dict) else {}
            original_dict = original if isinstance(original, dict) else {}
            for key, value in patch.items():
                field, operation = self._parse_key(key)
                nested_original = original_dict.get(field)
                if operation in ("append", "append_partial"):
                    self._apply_append(
                        result,
                        field,
                        value,
                        guarded=operation == "append_partial",
                        original=nested_original,
                    )
                elif self._contains_append_suffix(value):
                    result[field] = self._merge_value(result.get(field), value, original=nested_original)
                else:
                    result[field] = self._resolve(value, original=original_dict, field=field)
            return result

        if isinstance(patch, list):
            result = copy.deepcopy(target) if isinstance(target, list) else []
            original_list = original if isinstance(original, list) else []
            for index, patch_item in enumerate(patch):
                item_original = original_list[index] if index < len(original_list) else None
                if isinstance(patch_item, dict):
                    selector = self._selector_keys(patch_item)
                    match_indices = self._find_partial_match_indices(result, selector) if selector else []
                    if match_indices:
                        for match_index in match_indices:
                            element_original = original_list[match_index] if match_index < len(original_list) else None
                            result[match_index] = self._merge_value(
                                result[match_index],
                                patch_item,
                                original=element_original,
                            )
                    elif self._contains_append_suffix(patch_item):
                        result.append(self._merge_value(None, patch_item, original=None))
                    else:
                        result.append(self._resolve(patch_item, original=original, field=str(index)))
                else:
                    result.append(self._resolve(patch_item, original=original, field=str(index)))
            return result

        return self._resolve(patch, original=original, field="")

    def _apply_operation(
        self,
        document: dict,
        field: str,
        operation: str,
        value: Any,
        *,
        original_document: dict,
    ) -> None:
        original_field = original_document.get(field)
        if operation not in ("delete", "delete_partial"):
            value = self._resolve(value, original=original_document, field=field)

        match operation:
            case "replace":
                if self._contains_append_suffix(value):
                    document[field] = self._merge_value(document.get(field), value, original=original_field)
                else:
                    document[field] = value

            case "append":
                self._apply_append(document, field, value, guarded=False, original=original_field)

            case "append_partial":
                self._apply_append(document, field, value, guarded=True, original=original_field)

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
    def match(self) -> list[Selector]:
        return [Selector(query) for query in self._doc["match"]]

    @property
    def patch(self) -> dict:
        return self._doc["patch"]
