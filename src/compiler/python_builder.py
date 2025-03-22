from enum import auto, Enum
from typing import Iterable

from .exceptions import _BaseError, SyntaxException
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

    def translate(self, tokens: Iterable[Token]) -> str | _BaseError:
        for tok in tokens:
            if self.state == _State.ASSIGNMENT_VALUE:
                err = self.process_assignment_value(tok)
                if err is not None:
                    return err
                continue

            match tok.typename:
                case 'ASSIGNMENT':
                    err = self.process_assignment(tok)
                    if err is not None:
                        return err
                case 'CMD':
                    self.process_cmd(tok)
                case 'NEWLINE':
                    self.process_newline(tok)
                case 'TYPE':
                    err = self.process_type(tok)
                    if err is not None:
                        return err

        if self.state == _State.ASSIGNMENT_VALUE and \
                    not self.vas.cur_stmt.strip().endswith('='):  # после знака := есть выражение
            self.code.append(self.vas.cur_stmt)
        elif self.state != _State.WAIT:
            return SyntaxException(tok.line, tok.column, tok.value, 'неверный синтаксис')
        
        return '\n'.join(self.code)
    
    def process_assignment(self, tok: Token):
        if self.state != _State.ASSIGNMENT_SIGN:
            return SyntaxException(tok.line, tok.column, tok.value,
                                   'неправильное использование присваивания')
        else:
            self.vas.cur_stmt += ' = '
            self.state = _State.ASSIGNMENT_VALUE
    
    def process_assignment_value(self, tok: Token):
        if tok.typename in {'ASSIGN', 'NUMBER', 'CHAR', 'STR', 'CMD', 'OP'}:
            self.vas.cur_stmt += str(tok.value)
        elif tok.typename != 'NEWLINE':
            return SyntaxException(tok.line, tok.column, tok.value, 'неверный синтаксис')
    
    def process_cmd(self, tok: Token):
        if self.state == _State.ASSIGNMENT_NAME:
            self.vas.cur_stmt = f'{tok.value}: {self.vas.cur_var_type}'
            self.vas.cur_var_type = ''
            self.state = _State.ASSIGNMENT_SIGN
    
    def process_newline(self, tok: Token):
        if self.state == _State.ASSIGNMENT_VALUE:
            self.code.append(self.vas.cur_stmt)
            self.vas.cur_stmt = None
            self.state = _State.WAIT
    
    def process_type(self, tok: Token):
        if self.state == _State.WAIT:
            self.vas.cur_var_type = TYPES_KEYWORDS[tok.value]
            self.state = _State.ASSIGNMENT_NAME
        else:
            return SyntaxException(tok.line, tok.column, tok.value,
                                   f'неправильное использование ключевого слова {tok.value!r}')


if __name__ == '__main__':
    code = 'цел а := 1 + 2 - (3*8)'
    parser = Parser()
    tokens = parser.parse(code)
    translater = TokensToPythonCodeTranslater()
    print(translater.translate(tokens))
