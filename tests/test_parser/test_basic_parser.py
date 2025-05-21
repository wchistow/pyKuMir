import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, SyntaxException = interpreter.Parser, interpreter.SyntaxException


def test_invalid_char_syntax_error():
    parser = Parser('@')
    with pytest.raises(SyntaxException):
        parser.parse()


def test_invalid_char_instead_of_assign():
    parser = Parser('цел а?')
    with pytest.raises(SyntaxException):
        parser.parse()


def test_invalid_char_in_expr_error():
    parser = Parser('цел а := 1 & 2')
    with pytest.raises(SyntaxException):
        parser.parse()
