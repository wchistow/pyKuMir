from pathlib import Path
import sys

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler import VM

from utils import bc_from_source

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
    bytecode = bc_from_source('вывод "привет"')
    vm.execute(bytecode)
    assert printed_text == 'привет'


def test_output_expr():
    bytecode = bc_from_source('вывод 5 + 6')
    vm.execute(bytecode)
    assert printed_text == '11'


def test_output_with_newline():
    bytecode = bc_from_source('вывод "привет", нс')
    vm.execute(bytecode)
    assert printed_text == 'привет\n'


def test_output_many_exprs():
    bytecode = bc_from_source('вывод "привет", ", мир!"')
    vm.execute(bytecode)
    assert printed_text == 'привет, мир!'
