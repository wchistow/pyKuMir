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
     1  LOAD_CONST           (Value(typename='цел', value=2),)
    ```
    """
    for inst in bc:
        print(f'{inst[0]:2}  {inst[1].name:20} {inst[2]}')
    for name, alg in algs.items():
        args = ', '.join(' '.join(arg) for arg in alg[0])
        print(f'{name!r} ({args}):')
        tags = alg[1]
        for i, inst in enumerate(alg[3][0]):
            cur_tags = [str(index) for index, tag in enumerate(tags) if tag == i]
            print(f'    {",".join(cur_tags) + (":" if cur_tags else ""):4}'
                  f'{inst[0]:2}  {inst[1].name:20} {inst[2]}')
