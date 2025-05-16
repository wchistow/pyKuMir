from enum import Enum

from .value import Value


class Bytecode(Enum):
    LOAD = 0x01
    LOAD_NAME = 0x02
    BIN_OP = 0x03
    STORE = 0x04
    CALL = 0x05
    RET = 0x06
    OUTPUT = 0x07
    INPUT = 0x08


BytecodeType = tuple[int, Bytecode, tuple[Value | None | tuple[Value], ...]]
