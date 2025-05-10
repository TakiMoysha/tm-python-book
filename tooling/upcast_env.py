import enum
import os
from pathlib import Path
from typing import Any, cast, overload
from collections.abc import Callable

TRUE_VALUES = ("1", "t", "T", "true", "True", "TRUE", "y", "Y", "yes", "Yes", "YES")
PATH_SEPARATOR = ":"
type TParse = str | bool | int | Path


type T = type


@overload
def get_upcast_env(key: str, default: str, type_hint: None = None) -> str: ...
@overload
def get_upcast_env(key: str, default: bool, type_hint: None = None) -> bool: ...
@overload
def get_upcast_env(key: str, default: int, type_hint: None = None) -> int: ...
@overload
def get_upcast_env(key: str, default: Path, type_hint: None = None) -> Path: ...
@overload
def get_upcast_env(key: str, default: None, type_hint: None = None) -> None: ...


def get_upcast_env(
    key: str,
    default: TParse | None,
    type_hint: type[T] | None = None,
) -> TParse | T | None:
    """Environement variable parser

    Args:
        key: environment variable
        default: default value
        type_hint: by default inferring from default value

    Raises:
        ValueError: value cannot be parsed

    Returns:
        parsed value of the specified type
    """

    str_value = os.getenv(key)

    if str_value is None:
        return cast("T", default) if type_hint is not None else default

    value: str = str_value

    if type(default) is str:
        return cast("T", value) if type_hint is not None else value

    if type(default) is bool:
        _v = value in TRUE_VALUES
        return cast("T", _v) if type_hint is not None else _v

    if type(default) is int:
        _v = int(value)
        return cast("T", _v) if type_hint is not None else _v

    if isinstance(default, Path):
        _v = Path(value)
        return cast("T", _v) if type_hint is not None else _v

    msg = f"Cannot parse value: [{key}<{type(default)}>]: {value}"
    raise ValueError(msg)
