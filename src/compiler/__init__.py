from .build_ast import build_ast
from .build_bytecode import build_bytecode, Bytecode

from .exceptions import SyntaxException, RuntimeException
from .vm import VM


def code_to_bytecode(code: str) -> list[Bytecode]:
    return build_bytecode(build_ast(code))
