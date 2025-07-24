import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, SyntaxException, Value = (
    interpreter.Parser,
    interpreter.SyntaxException,
    interpreter.value.Value,
)
ast_classes = interpreter.ast_classes


def test_parse_simple_alg():
    code = 'алг\nнач\nкон'
    parser = Parser(code)
    parsed1 = parser.parse()

    code = 'алг нач кон'
    parser = Parser(code)
    parsed2 = parser.parse()

    assert parsed1 == [
        ast_classes.AlgStart(0, is_main=True, name=''),
        ast_classes.AlgEnd(2),
    ]
    assert parsed2 == [
        ast_classes.AlgStart(0, is_main=True, name=''),
        ast_classes.AlgEnd(0),
    ]


def test_parse_alg_with_name():
    code = """алг тест
    нач
    кон
    """
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(0, is_main=True, name='тест'),
        ast_classes.AlgEnd(2),
    ]


def test_parse_two_algs():
    code = """алг тест1
    нач
    кон
    
    алг тест2
    нач
    кон
    """
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(0, is_main=True, name='тест1'),
        ast_classes.AlgEnd(2),
        ast_classes.AlgStart(4, is_main=False, name='тест2'),
        ast_classes.AlgEnd(6),
    ]


def test_parse_alg_with_args():
    code = """
    алг тест(арг цел а, арг цел б) нач
        вывод а, б
    кон
    """
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(
            lineno=1,
            is_main=True,
            name='тест',
            args=[['арг', 'цел', 'а'], ['арг', 'цел', 'б']],
        ),
        ast_classes.Output(
            lineno=2,
            exprs=[
                [Value(typename='get-name', value='а')],
                [Value(typename='get-name', value='б')],
            ],
        ),
        ast_classes.AlgEnd(lineno=3),
    ]


def test_parse_call():
    code = """
    алг нач
        приветствие
    кон
    """
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.Call(2, alg_name='приветствие'),
        ast_classes.AlgEnd(3),
    ]


def test_parse_call_with_args():
    code = """
    алг нач
        тест(1, 2)
    кон
    """
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.Call(2, alg_name='тест', args=[[Value('цел', 1)], [Value('цел', 2)]]),
        ast_classes.AlgEnd(3),
    ]


def test_parse_call_with_args_as_expr():
    code = """
    алг нач
        вывод тест(1, 2)
    кон
    """
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(1, is_main=True, name=''),
        ast_classes.Output(
            lineno=2,
            exprs=[
                [
                    ast_classes.Call(
                        lineno=2,
                        alg_name='тест',
                        args=[
                            [Value(typename='цел', value=1)],
                            [Value(typename='цел', value=2)],
                        ],
                    )
                ]
            ],
        ),
        ast_classes.AlgEnd(3),
    ]


def test_parse_alg_with_two_args_with_one_type():
    code = """
    алг нач
    кон

    алг цел сумма(цел а, б) нач
        знач := а + б
    кон
    """
    parser = Parser(code)
    parsed = parser.parse()
    assert (
        ast_classes.AlgStart(
            4,
            is_main=False,
            name='сумма',
            ret_type='цел',
            args=[['арг', 'цел', 'а'], ['арг', 'цел', 'б']],
        )
        in parsed
    )


def test_parse_alg_with_space_in_name():
    code = """алг один два
    нач
    кон
    """
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(0, is_main=True, name='один два'),
        ast_classes.AlgEnd(2),
    ]


def test_parse_call_alg_with_space_in_name():
    code = """
    алг нач
      тест тест
    кон
    алг тест тест
    нач
      вывод 5
    кон"""
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


def test_parse_nested_call():
    code = 'вывод тест1(не тест2(а, 0) = "привет")'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.Output(
            lineno=0,
            exprs=[
                [
                    ast_classes.Call(
                        lineno=0,
                        alg_name='тест1',
                        args=[
                            [
                                ast_classes.Call(
                                    lineno=0,
                                    alg_name='тест2',
                                    args=[
                                        [Value(typename='get-name', value='а')],
                                        [Value(typename='цел', value=0)],
                                    ],
                                ),
                                Value(typename='лит', value='привет'),
                                ast_classes.Op(op='='),
                                ast_classes.Op(op='не', unary=True),
                            ]
                        ],
                    )
                ]
            ],
        )
    ]


def test_without_start_keyword_error():
    code = """алг
    цел а := 5
    кон"""
    parser = Parser(code)
    with pytest.raises(SyntaxException):
        parser.parse()


def test_without_end_keyword_error():
    code = """алг
    нач
    цел а := 5"""
    parser = Parser(code)
    with pytest.raises(SyntaxException):
        parser.parse()


def test_not_first_without_name():
    code = """алг тест
    нач
      вывод 5
    кон
    
    алг
    нач
    вывод 10
    кон
    """
    parser = Parser(code)
    with pytest.raises(SyntaxException):
        parser.parse()
