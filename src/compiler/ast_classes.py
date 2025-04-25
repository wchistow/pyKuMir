from dataclasses import dataclass
from typing import Optional, Union

from .constants import ValueType


class Statement: ...


@dataclass
class Output(Statement):
    lineno: int
    exprs: list[tuple[Union[ValueType, 'Op']]]

@dataclass
class StoreVar(Statement):
    lineno: int
    typename: str | None  # `None` - если переменная уже объявлена (`а := 5`)
    names: tuple[str]
    value: Optional[tuple[Union[ValueType, 'Op']]] = None

@dataclass
class Op:
    op: str

@dataclass
class AlgStart(Statement):
    is_main: bool
    name: str = ''

@dataclass
class AlgEnd(Statement):
    ...
