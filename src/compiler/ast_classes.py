from dataclasses import dataclass
from typing import Any, Optional, Union

from lark import ast_utils, Token, Tree
from lark.tree import Meta

from constants import VALUE_TYPE


class _Ast(ast_utils.Ast): ...

class _Statement(_Ast): ...

@dataclass
class SetVar(_Statement, ast_utils.WithMeta):
    meta: Meta
    typename: Token
    names: Tree
    value: Optional['Value'] = None

@dataclass
class Value(_Ast):
    value: Any

@dataclass
class BinOp(_Ast):
    left: Any
    op: str
    right: Any

# Классы, используемые не в AST, а в `build_ast._improve`:

@dataclass
class StoreVar:
    meta: Meta
    typename: str
    names: tuple[str]
    value: Optional['Expression'] = None

@dataclass
class Op:
    op: str

@dataclass
class Expression:
    expr: tuple[Union[VALUE_TYPE, Op]]
