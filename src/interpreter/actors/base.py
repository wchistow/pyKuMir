from dataclasses import dataclass, field
from collections.abc import Callable

from ..value import Value

KumirValue = Value

__all__ = ['Actor', 'KumirValue', 'KumirFunc']


@dataclass
class KumirFunc:
    py_func: Callable[[list[KumirValue]], KumirValue | None]
    ret_type: str = ''
    #                kind,type,name
    args: list[tuple[str, str, str]] = field(default_factory=list)


class Actor:
    vars: dict[str, tuple[str, KumirValue]]
    funcs: dict[str, KumirFunc]
