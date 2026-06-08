from __future__ import annotations

import ast
import copy
import json
import os
import random
import re
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Iterator

EXPRESSION_PATTERN = re.compile(r"^\{\{(.+)\}\}$", re.DOTALL)

_FORMAT_TOKENS = (
    ("YYYY", "%Y"),
    ("MM", "%m"),
    ("DD", "%d"),
    ("HH", "%H"),
    ("mm", "%M"),
    ("ss", "%S"),
)

_TRUTHY = frozenset({"true", "yes", "1"})
_FALSY = frozenset({"false", "no", "0"})


@dataclass(frozen=True)
class ExpressionContext:
    original: Any
    field: str


_expression_context: ContextVar[ExpressionContext | None] = ContextVar("expression_context", default=None)


@contextmanager
def expression_context(original: Any, field: str) -> Iterator[None]:
    token = _expression_context.set(ExpressionContext(original=original, field=field))
    try:
        yield
    finally:
        _expression_context.reset(token)


def _func_old() -> Any:
    context = _expression_context.get()
    if context is None:
        raise ValueError("old() can only be used within a patch expression")
    if not isinstance(context.original, dict):
        raise ValueError("old() is not available in this context")
    return copy.deepcopy(context.original.get(context.field))


def is_expression(value: str) -> bool:
    return EXPRESSION_PATTERN.match(value.strip()) is not None


def _format_now(value: str) -> str:
    formatted = value
    for token, directive in _FORMAT_TOKENS:
        formatted = formatted.replace(token, directive)
    return datetime.now().strftime(formatted)


def _cast_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _TRUTHY:
            return True
        if normalized in _FALSY:
            return False
        raise ValueError(f"Cannot convert {value!r} to bool")
    raise ValueError(f"Cannot convert {type(value).__name__} to bool")


def _cast_object(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"Cannot parse object from {value!r}") from error
        if not isinstance(parsed, dict):
            raise ValueError(f"Expected object, got {type(parsed).__name__}")
        return parsed
    raise ValueError(f"Cannot convert {type(value).__name__} to object")


def _cast_array(value: Any) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"Cannot parse array from {value!r}") from error
        if not isinstance(parsed, list):
            raise ValueError(f"Expected array, got {type(parsed).__name__}")
        return parsed
    raise ValueError(f"Cannot convert {type(value).__name__} to array")


def _method_round(value: int | float, *args: Any) -> float:
    if len(args) > 1:
        raise ValueError("round() takes at most one argument")
    decimals = 0 if not args else args[0]
    if not isinstance(decimals, int):
        raise ValueError("round() decimals must be an integer")
    return round(value, decimals)


def _method_get(value: dict, *args: Any) -> Any:
    if len(args) != 1:
        raise ValueError("get() takes exactly one argument")
    key = args[0]
    if key not in value:
        raise ValueError(f"Key {key!r} not found")
    return value[key]


def _method_first(value: list, *_args: Any) -> Any:
    if not value:
        raise ValueError("first() cannot be called on an empty array")
    return value[0]


def _method_last(value: list, *_args: Any) -> Any:
    if not value:
        raise ValueError("last() cannot be called on an empty array")
    return value[-1]


def _parse_literal(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        operand = _parse_literal(node.operand)
        if isinstance(operand, (int, float)):
            return -operand
        raise ValueError(f"Unsupported unary operand: {operand!r}")

    if isinstance(node, ast.List):
        return [_parse_literal(element) for element in node.elts]

    if isinstance(node, ast.Tuple):
        return tuple(_parse_literal(element) for element in node.elts)

    raise ValueError(f"Unsupported expression argument: {ast.dump(node)}")


def _parse_call_args(node: ast.Call, *, context: str) -> list[Any]:
    if node.keywords:
        raise ValueError(f"Keyword arguments are not supported: {context}")
    return [_parse_literal(arg) for arg in node.args]


def _eval_call(node: ast.Call) -> Any:
    if isinstance(node.func, ast.Name):
        return call(node.func.id, _parse_call_args(node, context=node.func.id))

    if isinstance(node.func, ast.Attribute):
        value = _eval_call(node.func.value)
        return apply_method(value, node.func.attr, _parse_call_args(node, context=node.func.attr))

    raise ValueError(f"Invalid function expression: {ast.dump(node)}")


def _eval_expression(expression: str) -> Any:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ValueError(f"Invalid function expression: {expression!r}") from error

    if not isinstance(tree.body, ast.Call):
        raise ValueError(f"Invalid function expression: {expression!r}")

    return _eval_call(tree.body)


def call(name: str, args: list[Any]) -> Any:
    try:
        function = FUNCTIONS[name]
    except KeyError as error:
        raise ValueError(f"Unknown function {name!r}") from error

    return function(*args)


def apply_method(value: Any, name: str, args: list[Any]) -> Any:
    if name in CASTS:
        if args:
            raise ValueError(f"Cast {name!r} takes no arguments")
        try:
            return CASTS[name](value)
        except ValueError:
            raise
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError(str(error)) from error

    methods = _methods_for_type(value)
    if name not in methods:
        raise ValueError(f"Method {name!r} is not supported for {type(value).__name__}")

    try:
        return methods[name](value, *args)
    except ValueError:
        raise
    except (TypeError, KeyError, IndexError, json.JSONDecodeError) as error:
        raise ValueError(str(error)) from error


def _methods_for_type(value: Any) -> dict[str, Callable[..., Any]]:
    if isinstance(value, bool):
        return {}
    if isinstance(value, str):
        return STRING_METHODS
    if isinstance(value, list):
        return ARRAY_METHODS
    if isinstance(value, (int, float)):
        return NUMBER_METHODS
    if isinstance(value, dict):
        return OBJECT_METHODS
    return {}


def eval_expression(value: str) -> Any:
    match = EXPRESSION_PATTERN.match(value.strip())
    if match is None:
        raise ValueError(f"Invalid function expression: {value!r}")

    return _eval_expression(match.group(1).strip())


CASTS: dict[str, Callable[[Any], Any]] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": _cast_bool,
    "object": _cast_object,
    "array": _cast_array,
}

STRING_METHODS: dict[str, Callable[..., Any]] = {
    "split": lambda value, separator: value.split(separator),
    "replace": lambda value, old, new: value.replace(old, new),
    "trim": lambda value: value.strip(),
    "upper": lambda value: value.upper(),
    "lower": lambda value: value.lower(),
    "capitalize": lambda value: value.capitalize(),
    "substring": lambda value, start, end: value[start:end],
    "reverse": lambda value: value[::-1],
    "length": lambda value: len(value),
}

ARRAY_METHODS: dict[str, Callable[..., Any]] = {
    "join": lambda value, separator: separator.join(value),
    "reverse": lambda value: list(reversed(value)),
    "sort": lambda value: sorted(value),
    "unique": lambda value: list(dict.fromkeys(value)),
    "first": _method_first,
    "last": _method_last,
    "length": lambda value: len(value),
}

NUMBER_METHODS: dict[str, Callable[..., Any]] = {
    "round": _method_round,
    "abs": lambda value: abs(value),
}

OBJECT_METHODS: dict[str, Callable[..., Any]] = {
    "keys": lambda value: list(value.keys()),
    "values": lambda value: list(value.values()),
    "get": _method_get,
}

FUNCTIONS: dict[str, Callable[..., Any]] = {
    "now": lambda fmt: _format_now(fmt),
    "random": lambda minimum, maximum: random.randint(minimum, maximum),
    "uppercase": lambda value: value.upper(),
    "lowercase": lambda value: value.lower(),
    "capitalize": lambda value: value.capitalize(),
    "reverse": lambda value: value[::-1],
    "length": lambda value: len(value),
    "substring": lambda value, start, end: value[start:end],
    "replace": lambda value, old, new: value.replace(old, new),
    "split": lambda value, separator: value.split(separator),
    "join": lambda items, separator: separator.join(items),
    "trim": lambda value: value.strip(),
    "env": lambda name: os.environ[name],
    "old": lambda: _func_old(),
}
