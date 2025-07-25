from dataclasses import dataclass, field
from typing import Optional, Union, TypeAlias

from .value import Value

Expr: TypeAlias = list[Union[Value, 'Op', 'Call', 'GetItem', 'Slice']]


@dataclass
class Statement:
    lineno: int


@dataclass
class Use(Statement):
    name: str


@dataclass
class Output(Statement):
    exprs: list[Expr]


@dataclass
class Input(Statement):
    targets: list[Union[str, 'GetItem']]


@dataclass
class StoreVar(Statement):
    typename: str | None  # `None` - если переменная уже объявлена (`а := 5`)
    names: list[str]
    value: Union[Optional[Expr], list[list[tuple[Expr, Expr]]]] = None


@dataclass
class Op:
    op: str
    unary: bool = False


@dataclass
class AlgStart(Statement):
    is_main: bool
    name: str
    ret_type: str = ''
    ret_name: str = 'знач'
    args: list[tuple[str, str, str]] = field(default_factory=list)


class AlgEnd(Statement): ...


@dataclass
class Call(Statement):
    alg_name: str
    args: list[Expr] = field(default_factory=list)


@dataclass
class IfStart(Statement):
    cond: Expr


class IfEnd(Statement): ...


class ElseStart(Statement): ...


@dataclass
class LoopWithCountStart(Statement):
    count: Expr


class LoopWithCountEnd(Statement): ...


@dataclass
class LoopWhileStart(Statement):
    cond: Expr


@dataclass
class LoopWhileEnd(Statement): ...


@dataclass
class LoopForStart(Statement):
    target: str
    from_expr: Expr
    to_expr: Expr
    step: Expr


class LoopForEnd(Statement): ...


class LoopUntilStart(Statement): ...


@dataclass
class LoopUntilEnd(Statement):
    cond: Expr


class Exit(Statement): ...


@dataclass
class Assert(Statement):
    expr: Expr


class Stop(Statement): ...


@dataclass
class GetItem(Statement):
    table_name: str
    indexes: list[Expr]


@dataclass
class SetItem(Statement):
    table_name: str
    indexes: list[Expr]
    expr: Expr


@dataclass
class Slice(Statement):
    name: str
    indexes: list[Expr]
