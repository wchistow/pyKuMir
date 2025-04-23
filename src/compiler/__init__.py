from .build_bytecode import build_bytecode
from .parser import Parser, improve

from .exceptions import SyntaxException, RuntimeException
from .vm import VM


def code_to_bytecode(code: str) -> list[tuple]:
    p = Parser()
    return build_bytecode(improve(p.parse(code)))
