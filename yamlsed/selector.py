from __future__ import annotations

import re
from typing import Any

WILDCARD = "*"


class Selector:
    """A match selector that tests whether a document satisfies a query."""

    def __init__(self, query: Any) -> None:
        self.query = query

    def eval(self, document: Any) -> bool:
        """Return True if the document matches this selector."""
        if isinstance(self.query, dict):
            if not isinstance(document, dict):
                return False

            for key, value in self.query.items():
                if key not in document:
                    return False

                if not Selector(value).eval(document[key]):
                    return False

            return True

        if isinstance(self.query, list):
            if not isinstance(document, list) or len(document) != len(self.query):
                return False

            return all(
                Selector(query_item).eval(document_item) for document_item, query_item in zip(document, self.query)
            )

        if self.query == WILDCARD:
            return True

        if isinstance(self.query, str):
            if not isinstance(document, str):
                return False

            try:
                return re.fullmatch(self.query, document) is not None
            except re.error as error:
                raise ValueError(f"Invalid regex in selector: {self.query!r}") from error

        return document == self.query
