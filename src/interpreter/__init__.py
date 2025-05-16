from .build_bytecode import build_bytecode
from .parser import Parser, improve

from .bytecode import BytecodeType
from .exceptions import SyntaxException, RuntimeException
from .vm import VM

__all__ = ['build_bytecode', 'Parser', 'improve', 'SyntaxException', 'RuntimeException', 'VM', 'pretty_print_bc']


def code2bc(code: str) -> tuple[list[BytecodeType], dict[str, list[BytecodeType]]]:
    p = Parser(code)
    return build_bytecode(improve(p.parse()))


def pretty_print_bc(bc: list[BytecodeType], indent: int = 0) -> None:
    """
    Печатает переданный байт-код в формате:
    ```
     <номер строки>  <команда> <аргументы>
    ```
    Пример:
    ```
    1  LOAD            (2,)
    ```
    """
    for inst in bc:
        print(f'{" "*indent}{inst[0]:2}  {inst[1].name:15} {inst[2]}')
