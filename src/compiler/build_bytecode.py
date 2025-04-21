from lark import Token

from .ast_classes import StoreVar, Output, Op
from .bytecode import Bytecode
from .constants import ValueType


BytecodeType = tuple[int, Bytecode, tuple]

def build_bytecode(ast_tree) -> list[BytecodeType]:
    bytecode: list[BytecodeType] = []
    for sub_tree in ast_tree.iter_subtrees_topdown():
        if sub_tree.data.value == 'statement':
            stmt = sub_tree.children[0]
            lineno = stmt.meta.line
            if isinstance(stmt, StoreVar):
                if stmt.value is not None:
                    bytecode.extend(_expr_bc(lineno, stmt.value.expr))
                else:
                    bytecode.append((lineno, Bytecode.LOAD, (None,)))
                bytecode.append((lineno, Bytecode.STORE, (stmt.typename, stmt.names)))
            elif isinstance(stmt, Output):
                for expr in stmt.exprs:
                    bytecode.extend(_expr_bc(lineno, expr.expr))
                bytecode.append((lineno, Bytecode.OUTPUT, (len(stmt.exprs),)))
    return bytecode


def _expr_bc(lineno: int, expr: tuple[ValueType | Op]) -> list[BytecodeType]:
    """
    Превращает обратную польскую запись вида `(2, 3, Op(op='+'))` в набор команд байткода, например:
    ```
    LOAD 2
    LOAD 3
    BIN_OP +
    ```
    """
    res = []
    for v in expr:
        if isinstance(v, Token) and v.type == 'NAME':
            res.append((lineno, Bytecode.LOAD_NAME, (v.value,)))
        elif isinstance(v, ValueType):
            res.append((lineno, Bytecode.LOAD, (v,)))
        else:
            res.append((lineno, Bytecode.BIN_OP, (v.op,)))
    return res


def pretty_print_bc(bc: list[BytecodeType]) -> None:
    """
    Печатает переданный байткод в формате:
    ```
     <номер строки>  <команда> <аргументы>
    ```
    Пример:
    ```
     1  LOAD            (2,)
    ```
    """
    for inst in bc:
        print(f'{inst[0]:2}  {inst[1].name:15} {inst[2]}')


if __name__ == '__main__':
    from build_ast import build_ast

    code = """цел а := 5"""
    print(build_bytecode(build_ast(code)))
