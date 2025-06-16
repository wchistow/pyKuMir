import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
code2bc, VM, RuntimeException = interpreter.code2bc, interpreter.VM, interpreter.RuntimeException


def create_vm(bc, algs):
    return VM(bc, output_f=lambda s: None, input_f=lambda: '', algs=algs)


def test_assert_true():
    bc = code2bc('утв да')
    vm = create_vm(*bc)
    vm.execute()  # Не должно быть ошибки

def test_assert_false():
    bc = code2bc('утв 1 > 10')
    vm = create_vm(*bc)

    with pytest.raises(RuntimeException):
        vm.execute()
