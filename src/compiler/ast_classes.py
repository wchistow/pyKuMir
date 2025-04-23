from dataclasses import dataclass
from typing import Optional, Union

from .constants import ValueType

@dataclass
class Output:
    lineno: int
    exprs: list[tuple[Union[ValueType, 'Op']]]

@dataclass
class StoreVar:
    lineno: int
    typename: str | None  # `None` - если переменная уже объявлена (`а := 5`)
    names: tuple[str]
    value: Optional[tuple[Union[ValueType, 'Op']]] = None

@dataclass
class Op:
    op: str
