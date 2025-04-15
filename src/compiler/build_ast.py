"""Строит AST с помощью lark."""
import sys

from lark import Lark, ast_utils, Transformer, v_args, Tree, Token
from lark.exceptions import UnexpectedInput

from .ast_classes import DeclaringVar, Value, BinOp, StoreVar, Op, Expression, Output
from .constants import ValueType
from .exceptions import SyntaxException

this_module = sys.modules[__name__]


class ToAst(Transformer):
    def STRING(self, s: Token) -> str:
        return s[1:-1]

    def NUMBER(self, n: Token) -> int | float:
        if n.startswith('$') : # шестандцатиричное
            return int(n[1:], 16)
        elif '.' in n:
            return float(n)
        else:
            return int(n)

    def NAME(self, n: Token) -> bool | Token:
        if n == 'да':
            return True
        elif n == 'нет':
            return False
        return n


def build_ast(code: str) -> Tree:
    """
    Строит AST с помощью lark.

    Args:
        code (str): исходный код программы на алгоритмическом языке
    Returns:
        Tree: AST
    """

    parser = Lark.open('gram.lark', rel_to=__file__, propagate_positions=True, parser='lalr')
    transformer = ast_utils.create_transformer(this_module, ToAst())

    try:
        tree = transformer.transform(parser.parse(code))
    except UnexpectedInput as err:
        raise SyntaxException(err.line, token=err.token, expected=err.expected) from None
    else:
        return _improve(tree)


def _improve(tree: Tree) -> Tree:
    for t in tree.iter_subtrees():
        for c in t.children:
            new = None
            match c:
                case DeclaringVar():
                    if isinstance(c.value, Value):
                        expr = Expression((c.value.value,))
                    elif c.value is not None:
                        expr = Expression(_to_reverse_polish(c.value.children[0]))
                    else:
                        expr = None
                    new = StoreVar(
                        c.meta,
                        c.typename.value,
                        tuple(name.value for name in c.names.children),
                        expr)
                case Output():
                    new = Output(
                        c.meta,
                        [Expression(_to_reverse_polish(expr.children)) for expr in c.exprs.children]
                    )
            if isinstance(c, Tree) and  c.data.value == 'store_var':
                new = StoreVar(
                    c.meta,
                    None,
                    tuple(c.children[0]),
                    Expression(_to_reverse_polish(c.children[1].children)) if c.children[1] is not None else None)
            if new is not None:
                t.children[t.children.index(c)] = new
    return tree


def _get_priority(op: str) -> int:
    """Возвращает приоритет оператора."""
    match op:
        case '+' | '-':
            return 0
        case '*' | '/':
            return 1
    return 0


def _to_reverse_polish(expr: list | Tree) -> tuple[ValueType | Op]:
    notation: list[ValueType | Op] = []
    operator_stack: list[Token] = []
    in_parentheses = False
    indent = 0
    code_in_brackets = []
    if isinstance(expr, list):
        tokens = []
        for tok in expr:
            tokens.extend(_get_all_toks(tok))
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
            match token:
                case Value():
                    notation.append(token.value)
                case Token():
                    if token == '(':
                        in_parentheses = True
                    else:
                        while True:
                            if not operator_stack:
                                break
                            if _get_priority(operator_stack[-1]) >= _get_priority(token.value):
                                notation.append(Op(operator_stack.pop().value))
                            else:
                                break
                        operator_stack.append(token)
    for op in operator_stack[::-1]:
        notation.append(Op(op.value))
    return tuple(notation)


def _get_all_toks(expr) -> list:
    match expr:
        case BinOp():
            return [*_get_all_toks(expr.left), expr.op, *_get_all_toks(expr.right)]
        case Value():
            return [expr]
        case Tree():
            res = []
            for c in expr.children:
                res.extend(_get_all_toks(c))
            return res
        case _:
            return [expr]


if __name__ == '__main__':
    code = """цел а := 5 * (6 + 7)"""
    tree = build_ast(code)
    print(tree)
