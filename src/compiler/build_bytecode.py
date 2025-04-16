from lark import Token

from .ast_classes import StoreVar, Output
from .constants import ValueType


Bytecode = tuple[int, str, tuple]

def build_bytecode(ast_tree) -> list[Bytecode]:
    bytecode: list[Bytecode] = []
    for sub_tree in ast_tree.iter_subtrees_topdown():
        if sub_tree.data.value == 'statement':
            stmt = sub_tree.children[0]
            lineno = stmt.meta.line
            if isinstance(stmt, StoreVar):
                if stmt.value is not None:
                    bytecode.extend(_expr_bc(lineno, stmt.value.expr))
                else:
                    bytecode.append((lineno, 'load', (None,)))
                bytecode.append((lineno, 'store', (stmt.typename, stmt.names)))
            elif isinstance(stmt, Output):
                for expr in stmt.exprs:
                    bytecode.extend(_expr_bc(lineno, expr.expr))
                bytecode.append((lineno, 'output', (len(stmt.exprs),)))
    return bytecode


def _expr_bc(lineno: int, expr):
    res = []
    for v in expr:
        if isinstance(v, Token) and v.type == 'NAME':
            res.append((lineno, 'load_name', (v.value,)))
        elif isinstance(v, ValueType):
            res.append((lineno, 'load', (v,)))
        else:
            res.append((lineno, 'bin_op', (v.op,)))
    return res


def pretty_print_bc(bc: list[Bytecode]) -> None:
    for inst in bc:
        print(f'{inst[0]:2}  {inst[1]:15} {inst[2]}')


if __name__ == '__main__':
    from build_ast import build_ast

    code = """цел а := 5"""
    print(build_bytecode(build_ast(code)))
