from pathlib import Path
import sys

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler.build_ast import build_ast
from compiler.build_bytecode import build_bytecode


def bc_from_source(code: str) -> list[tuple]:
    return build_bytecode(build_ast(code))
