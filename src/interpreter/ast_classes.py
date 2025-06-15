from dataclasses import dataclass, field
from typing import Optional, Union, TypeAlias

from .value import Value

Expr: TypeAlias = list[Union[Value, 'Op']]

@dataclass
class Statement:
    lineno: int

@dataclass
class Output(Statement):
    exprs: list[Expr]

@dataclass
class Input(Statement):
    targets: list[str]

@dataclass
class StoreVar(Statement):
    typename: str | None  # `None` - если переменная уже объявлена (`а := 5`)
    names: list[str]
    value: Optional[Expr] = None

@dataclass
class Op:
    op: str

@dataclass
class AlgStart(Statement):
    is_main: bool
    name: str
    ret_type: str = ''
    ret_name: str = 'знач'
    args: list[tuple[str, str, str]] = field(default_factory=list)

class AlgEnd(Statement):
    ...

@dataclass
class Call(Statement):
    alg_name: str
    args: list[Expr] = field(default_factory=list)

@dataclass
class IfStart(Statement):
    cond: Expr

class IfEnd(Statement):
    ...

class ElseStart(Statement):
    ...

@dataclass
class LoopWithCountStart(Statement):
    count: Expr

class LoopWithCountEnd(Statement):
    ...

@dataclass
class LoopWhileStart(Statement):
    cond: Expr

@dataclass
class LoopWhileEnd(Statement):
    ...

@dataclass
class LoopForStart(Statement):
    target: str
    from_expr: Expr
    to_expr: Expr
    step: Expr

class LoopForEnd(Statement):
    ...

class LoopUntilStart(Statement):
    ...

@dataclass
class LoopUntilEnd(Statement):
    cond: Expr

class Exit(Statement):
    ...
