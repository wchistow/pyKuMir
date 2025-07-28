from enum import auto, Enum

from .value import Value


class Bytecode(Enum):
    LOAD_CONST = auto()
    LOAD_NAME = auto()
    MAKE_TABLE = auto()
    BIN_OP = auto()
    UNARY_OP = auto()
    STORE = auto()
    SET_RES_VAR = auto()
    CALL = auto()
    RET = auto()
    OUTPUT = auto()
    INPUT = auto()
    JUMP_TAG = auto()
    JUMP_TAG_IF_FALSE = auto()
    JUMP_TAG_IF_TRUE = auto()
    ASSERT = auto()
    STOP = auto()
    GET_ITEM = auto()
    SET_ITEM = auto()
    MAKE_SLICE = auto()
    USE = auto()


BytecodeType = tuple[int, Bytecode, tuple[Value | None | tuple[Value], ...]]
