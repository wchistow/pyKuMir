from .build_ast import build_ast
from .build_bytecode import build_bytecode

from .exceptions import SyntaxException, RuntimeException
from .vm import VM


def code_to_bytecode(code: str) -> list[tuple]:
    return build_bytecode(build_ast(code))
