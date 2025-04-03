from enum import auto, Enum
from typing import Iterable, NoReturn

from .exceptions import SyntaxException
from .parser import Token, Parser

TYPES_KEYWORDS = {
    'цел': 'int',
    'вещ': 'float',
    'лит': 'str',
    'сим': 'chr',
    'лог': 'bool',
}


class _VariableAssignmentState:
    cur_stmt = ''
    cur_var_type = ''


class _State(Enum):
    WAIT = auto()
    ASSIGNMENT_NAME = auto()  # ждём имя переменной
    ASSIGNMENT_SIGN = auto()  # ждем :=
    ASSIGNMENT_VALUE = auto()  # ждём значение переменной


class TokensToPythonCodeTranslater:
    def __init__(self):
        self.code = []
        self.vas = _VariableAssignmentState()
        self.state = _State.WAIT

    def reset(self):
        self.__init__()

    def translate(self, tokens: Iterable[Token]) -> NoReturn | str:
        for tok in tokens:
            if self.state == _State.ASSIGNMENT_VALUE:
                self.process_assignment_value(tok)

            match tok.typename:
                case 'ASSIGNMENT':
                    self.process_assignment(tok)
                case 'CMD':
                    self.process_cmd(tok)
                case 'NEWLINE':
                    self.process_newline(tok)
                case 'TYPE':
                    self.process_type(tok)

        if self.state == _State.ASSIGNMENT_VALUE and \
                    not self.vas.cur_stmt.strip().endswith('='):  # после знака := есть выражение
            self.add_var_def_to_code(tok)
        elif self.state != _State.WAIT:
            raise SyntaxException(tok.line, tok.column, tok.value, 'неверный синтаксис')

        return '\n'.join(self.code)

    def process_assignment(self, tok: Token) -> NoReturn | None:
        if self.state != _State.ASSIGNMENT_SIGN:
            raise SyntaxException(tok.line, tok.column, tok.value,
                                   'неправильное использование присваивания')
        else:
            self.vas.cur_stmt += ' = '
            self.state = _State.ASSIGNMENT_VALUE

    def process_assignment_value(self, tok: Token) -> NoReturn | None:
        if tok.typename in {'ASSIGN', 'NUMBER', 'CHAR', 'STR', 'CMD', 'OP'}:
            self.vas.cur_stmt += str(tok.value)
        elif tok.typename != 'NEWLINE':
            raise SyntaxException(tok.line, tok.column, tok.value, 'неверный синтаксис')

    def validate_var_expr(self, var_def: str) -> NoReturn | None:
        expr = var_def.split('=')[-1].strip()
        if expr.count('(') != expr.count(')'):
            raise SyntaxException(None, None, expr[-1], 'неверный синтаксис')
        elif expr.endswith(('+', '-', '*', '/')):
            raise SyntaxException(None, None, expr[-1], 'неверный синтаксис')
        elif (expr.find('+)'), expr.find('-)'), expr.find('*)'), expr.find('/)')) != (-1, -1, -1, -1):
            raise SyntaxException(None, None, expr[-1], 'неверный синтаксис')

    def add_var_def_to_code(self, cur_tok: Token) -> NoReturn | None:
        if not self.vas.cur_stmt.split('=')[-1].strip():
            raise SyntaxException(cur_tok.line, cur_tok.column, cur_tok.value, 'пустое выражение')
        try:
            self.validate_var_expr(self.vas.cur_stmt)
        except SyntaxException as err:
            err.line = cur_tok.line
            err.column = cur_tok.column
            raise err
        else:
            self.code.append(self.vas.cur_stmt)

    def process_cmd(self, tok: Token) -> None:
        if self.state == _State.ASSIGNMENT_NAME:
            self.vas.cur_stmt = f'{tok.value}: {self.vas.cur_var_type}'
            self.vas.cur_var_type = ''
            self.state = _State.ASSIGNMENT_SIGN

    def process_newline(self, tok: Token) -> NoReturn | None:
        if self.state == _State.ASSIGNMENT_VALUE:
            self.add_var_def_to_code(tok)
            self.vas.cur_stmt = None
            self.state = _State.WAIT

    def process_type(self, tok: Token) -> NoReturn | None:
        if self.state == _State.WAIT:
            self.vas.cur_var_type = TYPES_KEYWORDS[tok.value]
            self.state = _State.ASSIGNMENT_NAME
        else:
            raise SyntaxException(tok.line, tok.column, tok.value,
                                   f'неправильное использование ключевого слова {tok.value!r}')


if __name__ == '__main__':
    # code = 'цел а := 1 + 2 - (3*8)'
    code = 'цел а :=\n'
    parser = Parser()
    tokens = parser.parse(code)
    translater = TokensToPythonCodeTranslater()
    print(translater.translate(tokens))
