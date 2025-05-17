from .ast_classes import StoreVar, Output, Op, AlgStart, AlgEnd, Call, Input
from .bytecode import Bytecode, BytecodeType
from .value import Value


def build_bytecode(parsed_code: list) -> tuple[list[BytecodeType], dict]:
    """Преобразует АСД в байт-код."""
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
        elif isinstance(stmt, Input):
            cur_ns.append((stmt.lineno, Bytecode.INPUT, tuple(stmt.targets)))
        elif isinstance(stmt, AlgStart):
            algs[stmt.name] = []
            cur_alg = stmt.name
            if stmt.is_main:
                main_alg = stmt.name
        elif isinstance(stmt, AlgEnd):
            cur_ns.append((stmt.lineno, Bytecode.RET, ()))
            cur_alg = None
        elif isinstance(stmt, Call):
            cur_ns.append((stmt.lineno, Bytecode.CALL, (stmt.alg_name,)))

        last_line = stmt.lineno

    if main_alg is not None:
        bytecode.append((last_line, Bytecode.CALL, (main_alg,)))
    return bytecode, algs


def _expr_bc(lineno: int, expr: list[Value | Op]) -> list[BytecodeType]:
    """
    Превращает обратную польскую запись вида `(2, 3, Op(op='+'))` в набор команд байт-кода, например:
    ```
    LOAD 2
    LOAD 3
    BIN_OP +
    ```
    """
    res: list[BytecodeType] = []
    for v in expr:
        if isinstance(v, Op):
            res.append((lineno, Bytecode.BIN_OP, (v.op,)))
        elif v.typename == 'get-name':
            res.append((lineno, Bytecode.LOAD_NAME, (v.value,)))
        elif isinstance(v, Value):
            res.append((lineno, Bytecode.LOAD, (v,)))
    return res
