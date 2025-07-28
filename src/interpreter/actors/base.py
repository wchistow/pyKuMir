from dataclasses import dataclass, field
from collections.abc import Callable
from typing import Any, TypeAlias

from ..exceptions import RuntimeException
from ..value import Value

KumirValue = Value
KumirRuntimeException = RuntimeException
KumirNamespace: TypeAlias = dict[str, Value]

__all__ = ('Actor', 'KumirValue', 'KumirFunc', 'KumirRuntimeException', 'KumirNamespace')


@dataclass
class KumirFunc:
    py_func: (
            Callable[[list[KumirValue]], KumirValue | None] |
            Callable[[list[KumirValue], Any], KumirValue | None] |
            Callable[[list[KumirValue]], KumirNamespace]
    )
    ret_type: str = ''
    #                kind,type,name
    args: list[tuple[str, str, str]] = field(default_factory=list)


class Actor:
    vars: dict[str, tuple[str, KumirValue]] = {}
    funcs: dict[str, KumirFunc] = {}
