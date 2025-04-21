from enum import Enum


class Bytecode(Enum):
    LOAD = 0x01
    LOAD_NAME = 0x02
    BIN_OP = 0x03
    STORE = 0x04
    OUTPUT = 0x05
