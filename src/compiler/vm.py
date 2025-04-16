from typing import Callable, NamedTuple, NoReturn

from lark import Token

from .constants import ValueType, KEYWORDS
from .exceptions import SyntaxException, RuntimeException


class Var(NamedTuple):
    typename: str
    name: str
    value: ValueType | None


class VM:
    def __init__(self, output_f: Callable[[str], None]) -> None:
        self.glob_vars: list[Var] = []
        self.output_f = output_f
        
        self.stack: list[ValueType | None] = []

    def reset(self) -> None:
        self.glob_vars.clear()

    def execute(self, bytecode: list[tuple]) -> None:
        for inst in bytecode:
            if inst[1] == 'load':
                self.stack.append(inst[2][0])
            elif inst[1] == 'load_name':
                self.stack.append(self.get_var(inst[0], inst[2][0]))
            elif inst[1] == 'bin_op':
                self.bin_op(inst[0], inst[2][0])
            elif inst[1] == 'store':
                self.store_var(inst[0], inst[2][0], inst[2][1])
            elif inst[1] == 'output':
                self.output(inst[0], inst[2][0])

    def store_var(self, lineno: int, typename: str | None, names: tuple[str]) -> None:
        value = self.stack.pop()
        if len(names) > 1 and value is not None:
            raise SyntaxException(lineno, message='при нескольких переменных нельзя указывать значение')
        if typename is None:  # сохранение значения в уже объявленную переменную
            var_i = self._var_defined(names[0])
            if var_i == -1:
                raise RuntimeException(lineno, f'имя "{names[0]}" не объявлено')
            var = self.glob_vars.pop(var_i)
            self._save_var(lineno, var.typename, var.name, value)
            return
        if len(names) == 1:
            self._save_var(lineno, typename, names[0], value)
        else:  # объявление нескольких переменных (`цел а, б`)
            for name in names:
                self._save_var(lineno, typename, name, None)
    
    def bin_op(self, lineno: int, op: str) -> None:
        a = self.stack.pop()
        b = self.stack.pop()
        self._check_type_is_eq(lineno, a, b, op)
        self.stack.append(eval(f'{b} {op} {a}'))

    def output(self, lineno: int, exprs_num: int) -> None:
        res: list[str] = []
        for _ in range(exprs_num):
            res.append(str(self.stack.pop()))
        self.output_f(''.join(res[::-1]))

    def _save_var(self, lineno: int, typename: str, name: str, value: ValueType | None) -> None:
        if name in KEYWORDS:
            raise SyntaxException(lineno, message="ключевое слово в имени")
        if value is None:
            self.glob_vars.append(Var(typename, name, None))
            return
        value_type = self._get_type(lineno, value)
        if value_type == typename:  # типы целевой переменной и значения совпадают
            self.glob_vars.append(Var(typename, name, value))
        else:
            raise RuntimeException(lineno, message=f'нельзя "{typename} := {value_type}"')

    def get_var(self, lineno: int, name: str) -> ValueType | NoReturn:
        if name == 'нс':
            return '\n'
        for var in self.glob_vars:
            if var.name == name:
                if var.value is None:
                    raise RuntimeException(lineno, 'нет значения у величины.')
                return var.value
        raise RuntimeException(lineno, 'имя не объявлено')

    def _var_defined(self, name: str) -> int:
        """
        Возвращает индекс переменой с именем `name` в списке `self.vars`. Если такой нет, возвращает -1.
        """
        for i, var in enumerate(self.glob_vars):
            if var.name == name:
                return i
        return -1

    def _check_type_is_eq(self, lineno: int, a: ValueType, b: ValueType, op: str) -> None:
        a_type = self._get_type(lineno, a)
        b_type = self._get_type(lineno, b)
        if a_type != b_type:
            raise RuntimeException(lineno, f'нельзя "{b_type} {op} {a_type}"')

    def _get_type(self, lineno: int, value: ValueType | Token) -> str:
        """"Переводит" типы с python на алгоритмический."""
        if isinstance(value, Token):
            return self._get_type(lineno, self.get_var(lineno, value.value))
        else:
            types = {
                int: 'цел',
                float: 'вещ',
                str: 'лит',
                bool: 'лог'
            }
            return types[type(value)]
