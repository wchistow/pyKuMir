from .build_bytecode import build_bytecode
from .parser import Parser, improve

from .bytecode import BytecodeType
from .exceptions import SyntaxException, RuntimeException
from .vm import VM

__all__ = ['build_bytecode', 'Parser', 'improve', 'SyntaxException', 'RuntimeException', 'VM']


def code2bc(code: str) -> tuple[list[BytecodeType], dict[str, list[BytecodeType]]]:
    p = Parser(code)
    return build_bytecode(improve(p.parse()))
