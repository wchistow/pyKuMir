import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, SyntaxException, Value = interpreter.Parser, interpreter.SyntaxException, interpreter.value.Value
ast_classes = interpreter.ast_classes


def test_parse_simple_loop_with_count():
    code = '''
    алг нач
        нц 5 раз
            вывод 1
        кц
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.LoopWithCountStart(2, count=[Value('цел', 5)]),
        ast_classes.Output(3, exprs=[[Value('цел', 1)]]),
        ast_classes.LoopWithCountEnd(4),
        ast_classes.AlgEnd(5)
    ]

def test_parse_loop_with_count_with_expr():
    code = '''
    алг нач
        нц 5 + 2 раз
            вывод 1
        кц
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.LoopWithCountStart(2, count=[Value('цел', 5), Value('цел', 2), ast_classes.Op(op='+')]),
        ast_classes.Output(3, exprs=[[Value('цел', 1)]]),
        ast_classes.LoopWithCountEnd(4),
        ast_classes.AlgEnd(5)
    ]

def test_parse_loop_with_count_without_end_error():
    code = '''
    алг нач
        нц 5 + 2 раз
            вывод 1
    кон'''
    parser = Parser(code)

    with pytest.raises(SyntaxException):
        parser.parse()

def test_parse_simple_loop_while():
    code = '''
    алг нач
        нц пока да
            вывод 1
        кц
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.LoopWhileStart(2, cond=[Value('лог', 'да')]),
        ast_classes.Output(3, exprs=[[Value('цел', 1)]]),
        ast_classes.LoopWhileEnd(4),
        ast_classes.AlgEnd(5)
    ]

def test_parse_simple_loop_while_with_expr():
    code = '''
    алг нач
        нц пока 5 > 2
            вывод 1
        кц
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.LoopWhileStart(2, cond=[Value('цел', 5), Value('цел', 2), ast_classes.Op(op='>')]),
        ast_classes.Output(3, exprs=[[Value('цел', 1)]]),
        ast_classes.LoopWhileEnd(4),
        ast_classes.AlgEnd(5)
    ]
