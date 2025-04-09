"""Строит AST с помощью lark."""
import sys
from typing import Union

from lark import Lark, ast_utils, Transformer, v_args, Tree, Token

from .ast_classes import SetVar, Value, BinOp, StoreVar, Op, Expression
from .exceptions import SyntaxException

this_module = sys.modules[__name__]


class ToAst(Transformer):
    def STRING(self, s: str) -> str:
        return s[1:-1]

    def NUMBER(self, n: str) -> int:
        return int(n)

    @v_args(inline=True)
    def start(self, x):
        return x


def build_ast(code: str) -> Tree:
    """
    Строит AST с помощью lark.

    Args:
        code (str): исходный код программы на алгоритмическом языке
    Returns:
        Tree: AST
    """
    parser = Lark.open('gram.lark', rel_to=__file__, parser='lalr')

    transformer = ast_utils.create_transformer(this_module, ToAst())
    tree = transformer.transform(parser.parse(code))
    return _improve(tree)


def _improve(tree: Tree) -> Tree:
    for t in tree.iter_subtrees():
        for c in t.children:
            if isinstance(c, SetVar):
                sv = StoreVar(
                    c.meta,
                    c.typename.value,
                    tuple(name.value for name in c.names.children),
                    Expression(_to_reverse_polish(c.value.children[0])) if c.value is not None else None)
                t.children[t.children.index(c)] = sv
    return tree


def _get_priority(op: str) -> int:
    """Возвращает приоритет оператора."""
    if op in ('+', '-'):
        return 0
    elif op in ('*', '/'):
        return 1
    else:
        return 0


def _to_reverse_polish(expr: Union[list, Tree]) -> tuple[Union[str, int, Op]]:
    notation: list[Union[str, int, Op]] = []
    operator_stack: list[Token] = []
    in_parentheses = False
    indent = 0
    code_in_brackets = []
    if isinstance(expr, list):
        tokens = expr
    else:
        tokens = _get_all_toks(expr)
    for token in tokens:
        if in_parentheses:
            if token == '(':
                indent += 1
                code_in_brackets.append(token)
            elif token != ')':
                code_in_brackets.append(token)
            elif token == ')':
                if indent == 0:
                    in_parentheses = False
                    notation.extend(_to_reverse_polish(code_in_brackets))
                    code_in_brackets.clear()
                else:
                    indent -= 1
                    code_in_brackets.append(token)
        else:
            if isinstance(token, Value):
                notation.append(token.value)
            elif isinstance(token, Token):
                if token == '(':
                    in_parentheses = True
                else:
                    if token == ')':
                        raise SyntaxException('Слишком много закрывающихся скобок')
                    while True:
                        if not operator_stack:
                            break
                        if _get_priority(operator_stack[-1]) >= _get_priority(token.value):
                            notation.append(Op(operator_stack.pop().value))
                        else:
                            break
                    operator_stack.append(token)
    if in_parentheses:
        raise SyntaxException('Слишком мало закрывающихся скобок')
    for op in operator_stack[::-1]:
        notation.append(Op(op.value))
    return tuple(notation)


def _get_all_toks(expr) -> list:
    if isinstance(expr, BinOp):
        return [*_get_all_toks(expr.left), expr.op, *_get_all_toks(expr.right)]
    elif isinstance(expr, Value):
        return [expr]
    elif isinstance(expr, Tree):
        res = []
        for c in expr.children:
            res.extend(_get_all_toks(c))
        return res
    else:
        return [expr]


if __name__ == '__main__':
    code = """цел а := 5 * (6 + 7)"""
    tree = build_ast(code)
    print(tree)
