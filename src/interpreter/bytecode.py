from enum import auto, Enum

from .value import Value


class Bytecode(Enum):
    LOAD_CONST = auto()
    LOAD_NAME = auto()
    BIN_OP = auto()
    UNARY_OP = auto()
    STORE = auto()
    CALL = auto()
    RET = auto()
    OUTPUT = auto()
    INPUT = auto()
    JUMP_TAG = auto()
    JUMP_TAG_IF_FALSE = auto()
    JUMP_TAG_IF_TRUE = auto()
    ASSERT = auto()


BytecodeType = tuple[int, Bytecode, tuple[Value | None | tuple[Value], ...]]
