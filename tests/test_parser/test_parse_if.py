import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, SyntaxException, Value = interpreter.Parser, interpreter.SyntaxException, interpreter.value.Value
ast_classes = interpreter.ast_classes


def test_parse_simple_if():
    code = '''
    алг нач
        если да то
            вывод 1
        все
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.IfStart(2, cond=[Value('лог', 'да')]),
        ast_classes.Output(3, exprs=[[Value('цел', 1)]]),
        ast_classes.IfEnd(4),
        ast_classes.AlgEnd(5)
    ]
