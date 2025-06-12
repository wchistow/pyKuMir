import importlib
from pathlib import Path
import sys

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, SyntaxException, Value = interpreter.Parser, interpreter.SyntaxException, interpreter.value.Value
ast_classes = interpreter.ast_classes

def test_parse_switch():
    code = '''
    алг нач
        цел а := 6
        выбор
            при а = 0: вывод 0
            иначе: вывод "что-то другое"
        все
    кон'''
    parser = Parser(code)
    parsed = parser.parse()

    assert parsed == [
        ast_classes.AlgStart(lineno=1, is_main=True, name=''),
        ast_classes.StoreVar(lineno=2, typename='цел', names=['а'], value=[Value(typename='цел', value=6)]),
        ast_classes.IfStart(lineno=4, cond=[Value(typename='get-name', value='а'),
                                            Value(typename='цел', value=0), ast_classes.Op(op='=')]),
        ast_classes.Output(lineno=4, exprs=[[Value(typename='цел', value=0)]]),
        ast_classes.ElseStart(lineno=5),
        ast_classes.Output(lineno=5, exprs=[[Value(typename='лит', value='что-то другое')]]),
        ast_classes.IfEnd(lineno=6),
        ast_classes.AlgEnd(lineno=7),
    ]
