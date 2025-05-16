import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
code2bc, RuntimeException, VM = interpreter.code2bc, interpreter.RuntimeException, interpreter.VM


def create_vm(bc, algs):
    return VM(bc, output_f=lambda s: None, input_f=lambda: '', algs=algs)


def test_call_undef_alg_error():
    bytecode = code2bc('алг\nнач\nтест\nкон')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()
