from dataclasses import dataclass
from typing import Any, Optional

from lark import ast_utils, Token, Tree
from lark.tree import Meta

from .constants import ValueType


class _Ast(ast_utils.Ast): ...

class _Statement(_Ast): ...

@dataclass
class DeclaringVar(_Statement, ast_utils.WithMeta):
    meta: Meta
    typename: Token | None = None  # `None` - если переменая уже объявлена
    names: Tree = None  # не может быть `None`. Это нужно только из-за того, что у `typename` есть значение по умолчанию
    value: Optional['Value'] = None

@dataclass
class StoreVal(_Statement, ast_utils.WithMeta):
    meta: Meta
    name: Tree
    value: Optional['Value'] = None

@dataclass
class Value(_Ast):
    value: Any

@dataclass
class BinOp(_Ast):
    left: Any
    op: str
    right: Any

@dataclass
class Output(_Statement, ast_utils.WithMeta):
    meta: Meta
    exprs: list['Expression']

# Классы, используемые не в AST, а в `build_ast._improve`:

@dataclass
class StoreVar:
    meta: Meta
    typename: str | None  # `None` - если переменная уже объявлена (`а := 5`)
    names: tuple[str]
    value: Optional['Expression'] = None

@dataclass
class Op:
    op: str

@dataclass
class Expression:
    expr: tuple[ValueType | Op]
