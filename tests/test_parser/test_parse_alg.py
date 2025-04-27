from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler.ast_classes import AlgStart, AlgEnd
from compiler import SyntaxException, Parser


def test_parse_simple_alg():
    code = 'алг\nнач\nкон'
    parser = Parser(code)
    parsed1 = parser.parse()

    code = 'алг нач кон'
    parser = Parser(code)
    parsed2 = parser.parse()

    assert parsed1 == [AlgStart(is_main=True, name=''), AlgEnd(2)]
    assert parsed2 == [AlgStart(is_main=True, name=''), AlgEnd(0)]


def test_without_нач_error():
    code = '''алг
    цел а := 5
    кон'''
    parser = Parser(code)
    with pytest.raises(SyntaxException):
        parsed = parser.parse()


def test_without_кон_error():
    code = '''алг
    нач
    цел а := 5'''
    parser = Parser(code)
    with pytest.raises(SyntaxException):
        parsed = parser.parse()
