import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, SyntaxException, Value = interpreter.Parser, interpreter.SyntaxException, interpreter.value.Value
ast_classes = interpreter.ast_classes


def test_parse_simple_alg():
    code = 'алг\nнач\nкон'
    parser = Parser(code)
    parsed1 = parser.parse()

    code = 'алг нач кон'
    parser = Parser(code)
    parsed2 = parser.parse()

    assert parsed1 == [ast_classes.AlgStart(0, is_main=True, name=''), ast_classes.AlgEnd(2)]
    assert parsed2 == [ast_classes.AlgStart(0, is_main=True, name=''), ast_classes.AlgEnd(0)]


def test_parse_alg_with_name():
    code = '''алг тест
    нач
    кон
    '''
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.AlgStart(0, is_main=True, name='тест'), ast_classes.AlgEnd(2)]


def test_parse_two_algs():
    code = '''алг тест1
    нач
    кон
    
    алг тест2
    нач
    кон
    '''
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(0, is_main=True, name='тест1'),
        ast_classes.AlgEnd(2),
        ast_classes.AlgStart(4, is_main=False, name='тест2'),
        ast_classes.AlgEnd(6)
    ]


def test_parse_call():
    code = '''алг
    нач
        приветствие
    кон
    
    алг приветствие
    нач
        вывод "привет"
    кон
    '''
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(0, is_main=True, name=''),
        ast_classes.Call(2, alg_name='приветствие'),
        ast_classes.AlgEnd(3),
        ast_classes.AlgStart(5, is_main=False, name='приветствие'),
        ast_classes.Output(7, exprs=[[Value('лит', 'привет')]]),
        ast_classes.AlgEnd(8)
    ]


def test_parse_alg_with_space_in_name():
    code = '''алг один два
    нач
    кон
    '''
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.AlgStart(0, is_main=True, name='один два'), ast_classes.AlgEnd(2)]

def test_parse_call_alg_with_space_in_name():
    code = '''
    алг нач
      тест тест
    кон
    алг тест тест
    нач
      вывод 5
    кон'''
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.Call(2, 'тест тест'),
        ast_classes.AlgEnd(3),
        ast_classes.AlgStart(4, is_main=False, name='тест тест'),
        ast_classes.Output(6, [[Value('цел', 5)]]),
        ast_classes.AlgEnd(7),
    ]

# тесты ошибок

def test_without_start_keyword_error():
    code = '''алг
    цел а := 5
    кон'''
    parser = Parser(code)
    with pytest.raises(SyntaxException):
        parser.parse()


def test_without_end_keyword_error():
    code = '''алг
    нач
    цел а := 5'''
    parser = Parser(code)
    with pytest.raises(SyntaxException):
        parser.parse()


def test_not_first_without_name():
    code = '''алг тест
    нач
      вывод 5
    кон
    
    алг
    нач
    вывод 10
    кон
    '''
    parser = Parser(code)
    with pytest.raises(SyntaxException):
        parser.parse()
