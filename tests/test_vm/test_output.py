import importlib
from pathlib import Path
import sys

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

compiler = importlib.import_module('compiler')
code2bc, VM = compiler.code2bc, compiler.VM

printed_text = ''


def create_vm(bc, algs):
    return VM(bc, output_f=output, algs=algs)


def output(s: str) -> None:
    global printed_text
    printed_text = s


def setup_function(function):
    global printed_text
    printed_text = ''


def test_output_simple_text():
    bytecode = code2bc('вывод "привет"')
    vm = create_vm(*bytecode)
    vm.execute()
    assert printed_text == 'привет'


def test_output_expr():
    bytecode = code2bc('вывод 5 + 6')
    vm = create_vm(*bytecode)
    vm.execute()
    assert printed_text == '11'


def test_output_with_newline():
    bytecode = code2bc('вывод "привет", нс')
    vm = create_vm(*bytecode)
    vm.execute()
    assert printed_text == 'привет\n'


def test_output_many_exprs():
    bytecode = code2bc('вывод "привет", ", мир!"')
    vm = create_vm(*bytecode)
    vm.execute()
    assert printed_text == 'привет, мир!'
