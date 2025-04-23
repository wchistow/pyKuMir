from .ast_classes import StoreVar, Output, Op
from .bytecode import Bytecode
from .constants import ValueType

BytecodeType = tuple[int, Bytecode, tuple[ValueType | None | tuple[ValueType], ...]]


def build_bytecode(parsed_code: list) -> list[BytecodeType]:
    bytecode: list[BytecodeType] = []
    for stmt in parsed_code:
        if isinstance(stmt, StoreVar):
            if stmt.value is not None:
                bytecode.extend(_expr_bc(stmt.lineno, stmt.value))
            else:
                bytecode.append((stmt.lineno, Bytecode.LOAD, (None,)))
            bytecode.append((stmt.lineno, Bytecode.STORE, (stmt.typename, stmt.names)))
        elif isinstance(stmt, Output):
            for expr in stmt.exprs:
                bytecode.extend(_expr_bc(stmt.lineno, expr))
            bytecode.append((stmt.lineno, Bytecode.OUTPUT, (len(stmt.exprs),)))
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
    res: list[BytecodeType] = []
    for v in expr:
        if isinstance(v, str) and v.isalpha():  # имя
            res.append((lineno, Bytecode.LOAD_NAME, (v,)))
        elif isinstance(v, str) and v[0] == '"' and v[-1] == '"':  # строка
            res.append((lineno, Bytecode.LOAD, (v[1:-1],)))
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
