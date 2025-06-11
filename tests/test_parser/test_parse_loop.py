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

def test_parse_simple_loop_for():
    code = '''
    алг нач
        нц для а от 0 до 5
            вывод а
        кц
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.LoopForStart(2, target='а', from_expr=[Value(typename='цел', value=0)],
                                 to_expr=[Value(typename='цел', value=5)],
                                 step=[Value(typename='цел', value=1)]),
        ast_classes.Output(3, exprs=[[Value('get-name', 'а')]]),
        ast_classes.LoopForEnd(4),
        ast_classes.AlgEnd(5)
    ]

def test_parse_loop_for_with_step():
    code = '''
    алг нач
        нц для а от 0 до 5 шаг 2
            вывод а
        кц
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.LoopForStart(2, target='а', from_expr=[Value(typename='цел', value=0)],
                                 to_expr=[Value(typename='цел', value=5)],
                                 step=[Value(typename='цел', value=2)]),
        ast_classes.Output(3, exprs=[[Value('get-name', 'а')]]),
        ast_classes.LoopForEnd(4),
        ast_classes.AlgEnd(5)
    ]

def test_parse_infinite_loop():
    code = '''
    алг нач
        нц
            вывод 1
        кц
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.LoopUntilStart(2),
        ast_classes.Output(3, exprs=[[Value('цел', 1)]]),
        ast_classes.LoopUntilEnd(4, cond=[Value('лог', 'да')]),
        ast_classes.AlgEnd(5)
    ]

def test_parse_loop_until():
    code = '''
    алг нач
        нц
            вывод 1
        кц при да
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.LoopUntilStart(2),
        ast_classes.Output(3, exprs=[[Value('цел', 1)]]),
        ast_classes.LoopUntilEnd(4, cond=[Value('лог', 'да')]),
        ast_classes.AlgEnd(5)
    ]

def test_parse_break():
    code = '''
    алг нач
        нц
            вывод 1
            выход
        кц
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.LoopUntilStart(2),
        ast_classes.Output(3, exprs=[[Value('цел', 1)]]),
        ast_classes.Exit(4),
        ast_classes.LoopUntilEnd(5, cond=[Value('лог', 'да')]),
        ast_classes.AlgEnd(6)
    ]

def test_parse_break_outside_loop_error():
    code = '''
    алг нач
        если да
            вывод 1
            выход
        все
    кон'''
    parser = Parser(code)

    with pytest.raises(SyntaxException):
        parser.parse()
