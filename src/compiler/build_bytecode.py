from .ast_classes import StoreVar, Output, Op, AlgStart, AlgEnd
from .bytecode import Bytecode, BytecodeType
from .constants import ValueType


def build_bytecode(parsed_code: list) -> tuple[list[BytecodeType], dict]:
    bytecode: list[BytecodeType] = []
    algs: dict[str, list[BytecodeType]] = {}
    cur_alg: str | None = None
    main_alg: str | None = None
    last_line = 0
    for stmt in parsed_code:
        if cur_alg is not None:
            cur_ns = algs[cur_alg]
        else:
            cur_ns = bytecode
        if isinstance(stmt, StoreVar):
            if stmt.value is not None:
                cur_ns.extend(_expr_bc(stmt.lineno, stmt.value))
            else:
                cur_ns.append((stmt.lineno, Bytecode.LOAD, (None,)))
            cur_ns.append((stmt.lineno, Bytecode.STORE, (stmt.typename, stmt.names)))
        elif isinstance(stmt, Output):
            for expr in stmt.exprs:
                cur_ns.extend(_expr_bc(stmt.lineno, expr))
            cur_ns.append((stmt.lineno, Bytecode.OUTPUT, (len(stmt.exprs),)))
        elif isinstance(stmt, AlgStart):
            algs[stmt.name] = []
            cur_alg = stmt.name
            if stmt.is_main:
                main_alg = stmt.name
        elif isinstance(stmt, AlgEnd):
            cur_ns.append((stmt.lineno, Bytecode.RET, ()))
            cur_alg = None

        if hasattr(stmt, 'lineno'):
            last_line = stmt.lineno

    if main_alg is not None:
        bytecode.append((last_line, Bytecode.CALL, (main_alg,)))
    return bytecode, algs


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


def pretty_print_bc(bc: list[BytecodeType], indent: int = 0) -> None:
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
        print(f'{" "*indent}{inst[0]:2}  {inst[1].name:15} {inst[2]}')
