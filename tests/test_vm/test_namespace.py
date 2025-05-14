import importlib
from pathlib import Path
import sys

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

compiler = importlib.import_module('compiler')
code2bc, VM = compiler.code2bc, compiler.VM
