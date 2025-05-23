from .build_bytecode import build_bytecode
from .parser import Parser

from .bytecode import BytecodeType
from .exceptions import SyntaxException, RuntimeException
from .vm import VM

__all__ = ['build_bytecode', 'Parser', 'SyntaxException', 'RuntimeException', 'VM', 'pretty_print_bc']


def code2bc(code: str) -> tuple[list[BytecodeType], dict[str, list[BytecodeType, list[int]]]]:
    p = Parser(code)
    return build_bytecode(p.parse())


def pretty_print_bc(bc: list[BytecodeType], algs: dict) -> None:
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
        print(f'{inst[0]:2}  {inst[1].name:20} {inst[2]}')
    for name, alg in algs.items():
        print(f'{name!r}:')
        tags = alg[1]
        for i, inst in enumerate(alg[0]):
            print(f'    {f"{tags.index(i)}:" if i in tags else "":3}{inst[0]:2}  {inst[1].name:20} {inst[2]}')
