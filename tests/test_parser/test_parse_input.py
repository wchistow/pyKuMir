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


def test_simple_input():
    parser = Parser('ввод а')
    assert parser.parse() == [ast_classes.Input(0, ['а'])]


def test_parse_input_with_two_targets():
    parser = Parser('ввод а, б')
    assert parser.parse() == [ast_classes.Input(0, ['а', 'б'])]


def test_too_many_commas_error():
    parser = Parser('ввод а,,')
    with pytest.raises(SyntaxException):
        parser.parse()


def test_empty_input_error():
    parser = Parser('ввод')
    with pytest.raises(SyntaxException):
        parser.parse()
