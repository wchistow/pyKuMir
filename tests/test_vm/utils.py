from pathlib import Path
import sys

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler import build_bytecode, Parser, improve


def bc_from_source(code: str) -> list[tuple]:
    parser = Parser(code)
    return build_bytecode(improve(parser.parse()))
