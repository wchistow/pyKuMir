from pathlib import Path
import sys

from lark import Token

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler.ast_classes import Op
from compiler.build_bytecode import Bytecode
from compiler.vm import VM

printed_text = ''

def output(s: str) -> None:
    global printed_text
    printed_text = s


def setup_function(function):
    global printed_text
    printed_text = ''
    vm.reset()


vm = VM(output_f=output)


def test_output_simple_text():
    # вывод "привет"
    bytecode = [Bytecode(1, 'output', {'exprs': [('привет',)]})]
    vm.execute(bytecode)
    assert printed_text == 'привет'


def test_output_expr():
    # вывод 5 + 6
    bytecode = [Bytecode(1, 'output', {'exprs': [(5, 6, Op(op='+'))]})]
    vm.execute(bytecode)
    assert printed_text == '11'


def test_output_with_newline():
    # вывод "привет", нс
    bytecode = [Bytecode(1, 'output', {'exprs': [('привет',), (Token('NAME', 'нс'),)]})]
    vm.execute(bytecode)
    assert printed_text == 'привет\n'


def test_output_many_exprs():
    # вывод "привет", ", мир!"
    bytecode = [Bytecode(1, 'output', {'exprs': [('привет',), (', мир!',)]})]
    vm.execute(bytecode)
    assert printed_text == 'привет, мир!'
