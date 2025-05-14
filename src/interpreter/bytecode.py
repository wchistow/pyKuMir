from enum import Enum

from .value import Value


class Bytecode(Enum):
    LOAD = 0x01
    LOAD_NAME = 0x02
    BIN_OP = 0x03
    STORE = 0x04
    OUTPUT = 0x05
    CALL = 0x06
    RET = 0x07


BytecodeType = tuple[int, Bytecode, tuple[Value | None | tuple[Value], ...]]
