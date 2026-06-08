import pytest

from yamlsed.selector import Selector


def test_eval_matches_string_literal() -> None:
    assert Selector("example").eval("example") is True
    assert Selector("example").eval("example2") is False
    assert Selector("example").eval(123) is False


def test_eval_matches_regex_pattern() -> None:
    assert Selector("Example.*?").eval("Example model") is True
    assert Selector("Example.*?").eval("Not Example") is False


def test_eval_rejects_invalid_regex() -> None:
    with pytest.raises(ValueError, match="Invalid regex"):
        Selector("[").eval("value")


def test_eval_wildcard_matches_any_string() -> None:
    assert Selector("*").eval("anything") is True
    assert Selector("*").eval("") is True
