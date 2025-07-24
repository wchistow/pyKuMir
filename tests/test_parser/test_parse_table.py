import importlib
from pathlib import Path
import sys

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, Value = interpreter.Parser, interpreter.value.Value
ast_classes = interpreter.ast_classes


def test_parse_def_simple_table():
    parser = Parser('целтаб а[0:5]')
    parsed = parser.parse()
    assert parsed == [
        ast_classes.StoreVar(
            lineno=1,
            typename='целтаб',
            names=['а'],
            value=[[([Value(typename='цел', value=0)], [Value(typename='цел', value=5)])]],
        )
    ]


def test_parse_def_2d_table():
    parser = Parser('целтаб а[0:5, 1:6]')
    parsed = parser.parse()
    assert parsed == [
        ast_classes.StoreVar(
            lineno=1,
            typename='целтаб',
            names=['а'],
            value=[
                [
                    (
                        [Value(typename='цел', value=0)],
                        [Value(typename='цел', value=5)],
                    ),
                    (
                        [Value(typename='цел', value=1)],
                        [Value(typename='цел', value=6)],
                    ),
                ]
            ],
        )
    ]


def test_parse_getitem():
    parser = Parser('вывод а[1]')
    parsed = parser.parse()
    assert parsed == [
        ast_classes.Output(
            lineno=0,
            exprs=[
                [
                    ast_classes.GetItem(
                        lineno=1,
                        table_name='а',
                        indexes=[[Value(typename='цел', value=1)]],
                    )
                ]
            ],
        )
    ]


def test_parse_2d_getitem():
    parser = Parser('вывод а[0, 1]')
    parsed = parser.parse()
    assert parsed == [
        ast_classes.Output(
            lineno=0,
            exprs=[
                [
                    ast_classes.GetItem(
                        lineno=1,
                        table_name='а',
                        indexes=[
                            [Value(typename='цел', value=0)],
                            [Value(typename='цел', value=1)],
                        ],
                    )
                ]
            ],
        )
    ]


def test_parse_setitem():
    parser = Parser('а[1] := 5')
    parsed = parser.parse()
    assert parsed == [
        ast_classes.SetItem(
            lineno=0,
            table_name='а',
            indexes=[[Value(typename='цел', value=1)]],
            expr=[Value(typename='цел', value=5)],
        )
    ]
