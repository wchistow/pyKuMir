from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler.parser import Parser
from compiler.exceptions import SyntaxException
from compiler.python_builder import TokensToPythonCodeTranslater

parser = Parser()
translater = TokensToPythonCodeTranslater()


def setup_function(function):
    parser.reset()
    translater.reset()


def test_simple_var():
    code = 'цел а := 1'
    expected = 'а: int = 1'
    assert translater.translate(parser.parse(code)) == expected


def test_var_with_expr():
    code = 'цел а := 1+2*(3+4)'
    expected = 'а: int = 1+2*(3+4)'
    assert translater.translate(parser.parse(code)) == expected


def test_assignment_without_var_def():
    code = ':='
    with pytest.raises(SyntaxException):
        translater.translate(parser.parse(code))


def test_invalid_type_usage():
    code = 'цел вещ а := 1'
    with pytest.raises(SyntaxException):
        translater.translate(parser.parse(code))


def test_invalid_var_def():
    code = 'цел а :='
    with pytest.raises(SyntaxException):
        translater.translate(parser.parse(code))


def test_invalid_var_def_with_newline():
    code = 'цел а :=\n'
    with pytest.raises(SyntaxException):
        translater.translate(parser.parse(code))


def test_invalid_brackets_in_var_expr():
    code = 'цел а := 1+2*(3+4'
    with pytest.raises(SyntaxException):
        translater.translate(parser.parse(code))


def test_invalid_ops_in_var_expr():
    code = 'цел а := 1+2*'
    with pytest.raises(SyntaxException):
        translater.translate(parser.parse(code))


def test_invalid_ops_before_bracket_in_var_expr():
    code = 'цел а := 1+2*(3+)'
    with pytest.raises(SyntaxException):
        translater.translate(parser.parse(code))


def test_executor():
    code = 'использовать Робот'
    expected = 'import Робот'
    assert translater.translate(parser.parse(code)) == expected


def test_invalid_executor():
    code = 'использовать Робота'
    with pytest.raises(SyntaxException):
        translater.translate(parser.parse(code))
