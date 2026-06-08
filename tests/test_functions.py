from pathlib import Path

import pytest

from yamly.functions import _eval_expression, _format_now, eval_expression, expression_context, is_expression
from yamly.patch import Patch
from yamly.template import Template

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "functions"


@pytest.fixture
def base() -> Template:
    return Template.load(FIXTURES_DIR / "base.yaml")


@pytest.fixture
def patch() -> Patch:
    return Patch.load(FIXTURES_DIR / f"{FIXTURES_DIR.name}.patch.yaml")


@pytest.fixture
def mock_functions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("yamly.functions._format_now", lambda fmt: "2026-01-01 12:00:00")
    monkeypatch.setattr("yamly.functions.random.randint", lambda minimum, maximum: 42)
    monkeypatch.setenv("HOME", "/tmp/home")


def test_is_expression() -> None:
    assert is_expression("{{random(1, 100)}}") is True
    assert is_expression("prefix {{random(1, 100)}}") is False
    assert is_expression("plain") is False


def test_eval_string_functions() -> None:
    assert eval_expression('{{uppercase("hello")}}') == "HELLO"
    assert eval_expression('{{lowercase("HELLO")}}') == "hello"
    assert eval_expression('{{capitalize("hello")}}') == "Hello"
    assert eval_expression('{{reverse("hello")}}') == "olleh"
    assert eval_expression('{{length("hello")}}') == 5
    assert eval_expression('{{substring("hello", 0, 3)}}') == "hel"
    assert eval_expression('{{replace("hello", "l", "w")}}') == "hewwo"
    assert eval_expression('{{split("hello,world", ",")}}') == ["hello", "world"]
    assert eval_expression('{{join(["hello", "world"], ",")}}') == "hello,world"
    assert eval_expression('{{trim(" hello ")}}') == "hello"


def test_eval_now(mock_functions: None) -> None:
    assert eval_expression("{{now('YYYY-MM-DD HH:mm:ss')}}") == "2026-01-01 12:00:00"


def test_eval_random(mock_functions: None) -> None:
    assert eval_expression("{{random(1, 100)}}") == 42


def test_eval_env(mock_functions: None) -> None:
    assert eval_expression('{{env("HOME")}}') == "/tmp/home"


def test_eval_unknown_function() -> None:
    with pytest.raises(ValueError, match="Unknown function 'missing'"):
        eval_expression("{{missing('value')}}")


def test_eval_invalid_expression() -> None:
    with pytest.raises(ValueError, match="Invalid function expression"):
        eval_expression("{{not a call}}")


def test_eval_expression_requires_wrapped_syntax() -> None:
    with pytest.raises(ValueError, match="Invalid function expression"):
        eval_expression("random(1, 100)")


def test_format_now_uses_datetime_tokens() -> None:
    result = _format_now("YYYY-MM-DD HH:mm:ss")
    assert len(result) == 19
    assert result[4] == "-"
    assert result[7] == "-"


def test_eval_negative_number_argument(mock_functions: None) -> None:
    assert eval_expression("{{random(-10, -1)}}") == 42


def test_eval_tuple_argument() -> None:
    assert eval_expression('{{join(("hello", "world"), ",")}}') == "hello,world"


def test_eval_expression_rejects_non_call() -> None:
    with pytest.raises(ValueError, match="Invalid function expression"):
        _eval_expression("42")


def test_eval_expression_rejects_non_name_root() -> None:
    with pytest.raises(ValueError, match="Invalid function expression"):
        _eval_expression("(lambda: 1)()")


def test_eval_expression_rejects_keyword_arguments() -> None:
    with pytest.raises(ValueError, match="Keyword arguments are not supported"):
        _eval_expression("random(minimum=1, maximum=100)")


def test_eval_expression_rejects_unsupported_unary_operand() -> None:
    with pytest.raises(ValueError, match="Unsupported unary operand"):
        _eval_expression("random(-[], 1)")


def test_eval_expression_rejects_unsupported_argument_type() -> None:
    with pytest.raises(ValueError, match="Unsupported expression argument"):
        _eval_expression('missing({"key": "value"})')


def test_eval_env_missing_variable() -> None:
    with pytest.raises(KeyError):
        eval_expression('{{env("YAMLY_MISSING_ENV_VAR")}}')


def test_patch_requires_document() -> None:
    with pytest.raises(ValueError, match="Patch must contain at least one document"):
        Patch([])


def test_patch_load_quotes_bare_expressions(tmp_path: Path) -> None:
    path = tmp_path / "sample.patch.yaml"
    path.write_text(
        "match:\n  - name: example\npatch:\n  random: {{random(1, 100)}}\n",
        encoding="utf-8",
    )

    loaded = Patch.load(path)

    assert loaded.patch["random"] == "{{random(1, 100)}}"


def test_functions(base: Template, patch: Patch, mock_functions: None) -> None:
    expected = Template.load(FIXTURES_DIR / "result.yaml")
    base.apply(patch)
    assert base.documents == expected.documents


def test_cast_float(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LABEL", "3.14")
    assert eval_expression('{{env("LABEL").float()}}') == 3.14


def test_cast_int(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COUNT", "7")
    assert eval_expression('{{env("COUNT").int()}}') == 7


def test_cast_str(mock_functions: None) -> None:
    assert eval_expression("{{random(1, 100).str()}}") == "42"


def test_cast_bool_yaml_strings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLAG", "yes")
    assert eval_expression('{{env("FLAG").bool()}}') is True
    monkeypatch.setenv("FLAG", "false")
    assert eval_expression('{{env("FLAG").bool()}}') is False


def test_cast_object_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JSON", '{"name": "example"}')
    assert eval_expression('{{env("JSON").object()}}') == {"name": "example"}


def test_cast_array_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIST", '["a", "b"]')
    assert eval_expression('{{env("LIST").array()}}') == ["a", "b"]


def test_string_method_chain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NAME", " hello ")
    assert eval_expression('{{env("NAME").trim().upper()}}') == "HELLO"


def test_string_split_join_chain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAGS", "a,b,c")
    assert eval_expression('{{env("TAGS").split(",").join("-")}}') == "a-b-c"


def test_array_methods() -> None:
    assert eval_expression('{{split("b,a,b", ",").unique().sort().join(":")}}') == "a:b"


def test_array_first_last() -> None:
    assert eval_expression('{{split("a,b,c", ",").first()}}') == "a"
    assert eval_expression('{{split("a,b,c", ",").last()}}') == "c"


def test_number_round_chain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCORE", "3.14159")
    assert eval_expression('{{env("SCORE").float().round(2)}}') == 3.14


def test_number_abs(mock_functions: None) -> None:
    assert eval_expression("{{random(-10, -1).abs()}}") == 42


def test_object_methods(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JSON", '{"a": 1, "b": 2}')
    assert eval_expression('{{env("JSON").object().keys()}}') == ["a", "b"]
    assert eval_expression('{{env("JSON").object().values()}}') == [1, 2]


def test_object_get(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JSON", '{"name": "example"}')
    assert eval_expression('{{env("JSON").object().get("name")}}') == "example"


def test_cast_with_arguments_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LABEL", "3.14")
    with pytest.raises(ValueError, match="Cast 'float' takes no arguments"):
        eval_expression('{{env("LABEL").float(2)}}')


def test_unknown_method() -> None:
    with pytest.raises(ValueError, match="Method 'missing' is not supported"):
        eval_expression('{{trim(" hello ").missing()}}')


def test_method_on_wrong_type() -> None:
    with pytest.raises(ValueError, match="Method 'join' is not supported for str"):
        eval_expression('{{trim("hello").join(",")}}')


def test_array_first_on_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMPTY", "[]")
    with pytest.raises(ValueError, match="first\\(\\) cannot be called on an empty array"):
        eval_expression('{{env("EMPTY").array().first()}}')


def test_object_get_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JSON", '{"name": "example"}')
    with pytest.raises(ValueError, match="Key 'missing' not found"):
        eval_expression('{{env("JSON").object().get("missing")}}')


def test_cast_bool_invalid_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLAG", "maybe")
    with pytest.raises(ValueError, match="Cannot convert 'maybe' to bool"):
        eval_expression('{{env("FLAG").bool()}}')


def test_cast_bool_on_number(mock_functions: None) -> None:
    assert eval_expression("{{random(1, 100).bool()}}") is True


def test_cast_bool_on_unsupported_type() -> None:
    with pytest.raises(ValueError, match="Cannot convert list to bool"):
        eval_expression('{{split("a,b", ",").bool()}}')


def test_cast_object_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JSON", "{bad")
    with pytest.raises(ValueError, match="Cannot parse object"):
        eval_expression('{{env("JSON").object()}}')


def test_cast_object_requires_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JSON", '["a"]')
    with pytest.raises(ValueError, match="Expected object"):
        eval_expression('{{env("JSON").object()}}')


def test_cast_object_on_unsupported_type() -> None:
    with pytest.raises(ValueError, match="Cannot convert list to object"):
        eval_expression('{{split("a,b", ",").object()}}')


def test_cast_array_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIST", "[bad")
    with pytest.raises(ValueError, match="Cannot parse array"):
        eval_expression('{{env("LIST").array()}}')


def test_cast_array_requires_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIST", '{"a": 1}')
    with pytest.raises(ValueError, match="Expected array"):
        eval_expression('{{env("LIST").array()}}')


def test_cast_array_on_unsupported_type(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JSON", '{"a": 1}')
    with pytest.raises(ValueError, match="Cannot convert dict to array"):
        eval_expression('{{env("JSON").object().array()}}')


def test_number_round_without_decimals(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCORE", "3.7")
    assert eval_expression('{{env("SCORE").float().round()}}') == 4.0


def test_number_round_rejects_extra_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCORE", "3.14")
    with pytest.raises(ValueError, match="round\\(\\) takes at most one argument"):
        eval_expression('{{env("SCORE").float().round(1, 2)}}')


def test_number_round_requires_integer_decimals(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCORE", "3.14")
    with pytest.raises(ValueError, match="round\\(\\) decimals must be an integer"):
        eval_expression('{{env("SCORE").float().round(1.5)}}')


def test_object_get_requires_single_argument(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JSON", '{"name": "example"}')
    with pytest.raises(ValueError, match="get\\(\\) takes exactly one argument"):
        eval_expression('{{env("JSON").object().get()}}')


def test_array_last_on_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMPTY", "[]")
    with pytest.raises(ValueError, match="last\\(\\) cannot be called on an empty array"):
        eval_expression('{{env("EMPTY").array().last()}}')


def test_bool_has_no_primitive_methods(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLAG", "true")
    with pytest.raises(ValueError, match="Method 'upper' is not supported for bool"):
        eval_expression('{{env("FLAG").bool().upper()}}')


def test_cast_bool_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLAG", "true")
    assert eval_expression('{{env("FLAG").bool().bool()}}') is True


def test_cast_object_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JSON", '{"a": 1}')
    assert eval_expression('{{env("JSON").object().object()}}') == {"a": 1}


def test_cast_array_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIST", '["a"]')
    assert eval_expression('{{env("LIST").array().array()}}') == ["a"]


def test_cast_int_type_error() -> None:
    with pytest.raises(ValueError):
        eval_expression('{{split("a,b", ",").int()}}')


def test_method_type_error() -> None:
    with pytest.raises(ValueError):
        eval_expression('{{substring("hello", 0, 3).substring("bad", 0, 1)}}')


def test_method_on_none_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JSON", '{"value": null}')
    with pytest.raises(ValueError, match="Method 'upper' is not supported for NoneType"):
        eval_expression('{{env("JSON").object().get("value").upper()}}')


def test_old_outside_patch_context() -> None:
    with pytest.raises(ValueError, match="old\\(\\) can only be used within a patch expression"):
        eval_expression("{{old()}}")


def test_old_requires_dict_context() -> None:
    with expression_context("not a dict", "field"):
        with pytest.raises(ValueError, match="old\\(\\) is not available in this context"):
            eval_expression("{{old()}}")


def test_old_returns_original_field_value() -> None:
    patch = Patch({"match": [{"name": "example"}], "patch": {"version": "{{old()}}"}})
    result = patch.eval({"name": "example", "version": 1})
    assert result["version"] == 1


def test_old_returns_none_for_missing_field() -> None:
    patch = Patch({"match": [{"name": "example"}], "patch": {"version": "{{old()}}"}})
    result = patch.eval({"name": "example"})
    assert result["version"] is None


def test_old_with_method_chain() -> None:
    patch = Patch({"match": [{"name": "example"}], "patch": {"name": "{{old().upper()}}"}})
    result = patch.eval({"name": "example"})
    assert result["name"] == "EXAMPLE"


def test_old_in_nested_patch_value() -> None:
    patch = Patch(
        {
            "match": [{"name": "example"}],
            "patch": {"labels": {"version": "{{old()}}"}},
        }
    )
    result = patch.eval({"name": "example", "labels": {"version": "20.04", "os": "linux"}})
    assert result["labels"] == {"version": "20.04"}


def test_old_in_nested_append_merge() -> None:
    patch = Patch(
        {
            "match": [{"name": "example"}],
            "patch": {"labels+": {"version": "{{old()}}"}},
        }
    )
    result = patch.eval({"name": "example", "labels": {"version": "20.04", "os": "linux"}})
    assert result["labels"] == {"version": "20.04", "os": "linux"}
