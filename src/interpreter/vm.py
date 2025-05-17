from typing import Callable, NoReturn, TypeAlias

from .bytecode import Bytecode, BytecodeType
from .exceptions import SyntaxException, RuntimeException
from .value import Value

Namespace: TypeAlias = dict[str, tuple[str, Value | None]]


class VM:
    def __init__(self,
                 bytecode: list[BytecodeType],
                 output_f: Callable[[str], None],
                 input_f: Callable[[], str],
                 algs: dict[str, list[BytecodeType]] | None = None) -> None:
        self.output_f = output_f
        self.input_f = input_f
        self.bytecode = bytecode
        self.algs = algs or {}

        self.glob_vars: Namespace = {'нс': ('лит', Value('лит', '\n'))}
        self.stack: list[Value | None] = []

        # Локальные переменные текущих функций
        self.call_stack: list[Namespace] = []
        self.in_alg = False

        self.CALL_TRANSITIONS = {
            Bytecode.LOAD: lambda inst: self.stack.append(inst[2][0]),
            Bytecode.LOAD_NAME: lambda inst: self.stack.append(self.get_var(inst[0], inst[2][0])),
            Bytecode.BIN_OP: lambda inst: self.bin_op(inst[0], inst[2][0]),
            Bytecode.STORE: lambda inst: self.store_var(inst[0], inst[2][0], inst[2][1]),
            Bytecode.OUTPUT: lambda inst: self.output(inst[2][0]),
            Bytecode.INPUT: lambda inst: self.input(inst[0], inst[2]),
            Bytecode.CALL: lambda inst: self.call(inst[0], inst[2][0]),
            Bytecode.RET: lambda inst: self.call_stack.pop()
        }

    def execute(self) -> None:
        self._execute(self.bytecode)

    def _execute(self, bc: list[BytecodeType]) -> None:
        for inst in bc:
            self.CALL_TRANSITIONS[inst[1]](inst)
            if inst[1] == Bytecode.RET:
                break

    def store_var(self, lineno: int, typename: str | None, names: tuple[str]) -> None:
        """Обрабатывает инструкцию STORE"""
        value = self.stack.pop()
        if typename is None:  # сохранение значения в уже объявленную переменную
            if not self._var_defined(names[0]):
                raise RuntimeException(lineno, f'имя "{names[0]}" не объявлено')
            var = self._get_all_namespaces()[names[0]]
            self._save_var(lineno, var[0], names[0], value)
            return
        if len(names) == 1:
            self._save_var(lineno, typename, names[0], value)
        else:  # объявление нескольких переменных (`цел а, б`)
            for name in names:
                self._save_var(lineno, typename, name, None)

    def bin_op(self, lineno: int, op: str) -> None:
        a = self.stack.pop()
        b = self.stack.pop()
        typename = a.typename
        if sorted((a.typename, b.typename)) == ['вещ', 'цел']:
            typename = 'вещ'
        elif a.typename != b.typename:
            raise RuntimeException(lineno, f'нельзя "{b.typename} {op} {a.typename}"')

        if op == '+' and a.typename in ('цел', 'вещ', 'лит'):
            self.stack.append(Value(typename, b.value + a.value))
        elif op == '+' and a.typename == 'сим':
            self.stack.append(Value('лит', b.value + a.value))
        elif op == '-' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value(typename, b.value - a.value))
        elif op == '*' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value(typename, b.value * a.value))
        elif op == '/' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value('вещ', b.value / a.value))
        elif op == '**' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value(typename, b.value ** a.value))

    def output(self, exprs_num: int) -> None:
        res: list[str] = []
        for _ in range(exprs_num):
            res.append(str(self.stack.pop().value))
        self.output_f(''.join(res[::-1]))

    def input(self, lineno: int, targets: list[str]) -> None:
        cur_target_i = 0
        while cur_target_i < len(targets):
            inputted = self.input_f()
            target = targets[cur_target_i]
            try:
                target_var = self._get_all_namespaces()[target]
            except KeyError:
                raise RuntimeException(lineno, 'имя не объявлено') from None
            target_var_type = target_var[0]
            if target_var_type == 'лит':
                self._save_var(lineno, target_var_type, target,
                               _convert_string_to_type(lineno, inputted, target_var_type))
                cur_target_i += 1
            else:
                for text in inputted.split(' '):
                    try:
                        target = targets[cur_target_i]
                    except IndexError:
                        break
                    var_type = self._get_all_namespaces()[target][0]
                    self._save_var(lineno, var_type, target,
                                   _convert_string_to_type(lineno, text, var_type))
                    cur_target_i += 1

    def call(self, lineno: int, name: str) -> None:
        if name in self.algs:
            self.in_alg = True
            self.call_stack.append({})
            self._execute(self.algs[name])
        else:
            raise RuntimeException(lineno, f'имя {name} не определено')

    def _save_var(self, lineno: int, typename: str, name: str, value: Value | None) -> None | NoReturn:
        """
        Создаёт переменную типа `typename` с именем `name`
        и значением `value` (`None` - объявлена, но не определена).
        """
        namespace = self.call_stack[-1] if self.in_alg else self.glob_vars
        if value is None:
            namespace[name] = (typename, None)
            return
        value_type = value.typename
        if value_type == typename:  # типы целевой переменной и значения совпадают
            namespace[name] = (typename, value)
        else:
            raise RuntimeException(lineno, message=f'нельзя "{typename} := {value_type}"')

    def get_var(self, lineno: int, name: str) -> Value | NoReturn:
        var = _find_var_in_namespace(lineno, name, self._get_all_namespaces())
        if var is not None:
            return var
        raise RuntimeException(lineno, 'имя не объявлено')

    def _var_defined(self, name: str) -> bool:
        """
        Возвращает индекс переменой с именем `name`.
        Если такой нет, возвращает -1.
        """
        return name in self._get_all_namespaces()

    def _get_all_namespaces(self) -> Namespace:
        res = self.glob_vars
        if self.call_stack:
            res |= self.call_stack[-1]
        return res


def _convert_string_to_type(lineno: int, string: str, var_type: str) -> Value:
    if var_type == 'цел':
        try:
            return Value('цел', int(string))
        except ValueError:
            raise RuntimeException(lineno, 'Ошибка ввода целого числа') from None
    elif var_type == 'вещ':
        try:
            return Value('вещ', float(string))
        except ValueError:
            raise RuntimeException(lineno, 'Ошибка ввода вещественного числа') from None
    elif var_type == 'лог':
        return Value('лог', string)
    elif var_type == 'лит':
        return Value('лит', string)
    elif var_type == 'сим':
        if len(string) > 1:
            raise RuntimeException(lineno, 'Ошибка ввода: введено лишнее')
        return Value('сим', string)


def _find_var_in_namespace(lineno: int, name: str, namespace: Namespace) -> Value | None | NoReturn:
    try:
        var = namespace[name]
    except KeyError:
        return None
    if var[1] is None:
        raise RuntimeException(lineno, 'нет значения у величины')
    return var[1]
