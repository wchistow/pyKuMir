from dataclasses import dataclass
from typing import Optional, Union, TypeAlias

from .value import Value

Expr: TypeAlias = list[Union[Value, 'Op']]

class Statement: ...


@dataclass
class Output(Statement):
    lineno: int
    exprs: list[Expr]

@dataclass
class Input(Statement):
    lineno: int
    targets: list[str]

@dataclass
class StoreVar(Statement):
    lineno: int
    typename: str | None  # `None` - если переменная уже объявлена (`а := 5`)
    names: list[str]
    value: Optional[Expr] = None

@dataclass
class Op:
    op: str

@dataclass
class AlgStart(Statement):
    lineno: int
    is_main: bool
    name: str = ''

@dataclass
class AlgEnd(Statement):
    lineno: int

@dataclass
class Call(Statement):
    lineno: int
    alg_name: str

@dataclass
class IfStart(Statement):
    lineno: int
    cond: Expr

@dataclass
class IfEnd(Statement):
    lineno: int

@dataclass
class ElseStart(Statement):
    lineno: int

@dataclass
class LoopWithCountStart(Statement):
    lineno: int
    count: Expr

@dataclass
class LoopWithCountEnd(Statement):
    lineno: int

@dataclass
class LoopWhileStart(Statement):
    lineno: int
    cond: Expr

@dataclass
class LoopWhileEnd(Statement):
    lineno: int

@dataclass
class LoopForStart(Statement):
    lineno: int
    target: str
    from_expr: Expr
    to_expr: Expr
    step: Expr

@dataclass
class LoopForEnd(Statement):
    lineno: int
