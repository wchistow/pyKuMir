from typing import Callable, NoReturn, TypeAlias

from .bytecode import Bytecode, BytecodeType
from .exceptions import SyntaxException, RuntimeException
from .value import Value

Namespace: TypeAlias = dict[str, tuple[str, Value | None]]


class VM:
    def __init__(self,
                 bytecode: list[BytecodeType],
                 output_f: Callable[[str], None],
                 algs: dict[str, list[BytecodeType]] | None = None) -> None:
        self.output_f = output_f
        self.bytecode = bytecode
        self.algs = algs or {}

        self.glob_vars: Namespace = {}
        self.stack: list[Value | None] = []

        # Локальные переменные текущих функций
        self.call_stack: list[Namespace] = []
        self.in_alg = False

    def reset(self) -> None:
        """Сбрасывает состояние виртуальной машины."""
        self.glob_vars.clear()
        self.call_stack.clear()
        self.stack.clear()

    def execute(self) -> None:
        self._execute(self.bytecode)

    def _execute(self, bc: list[BytecodeType]) -> None:
        for inst in bc:
            if inst[1] == Bytecode.LOAD:
                self.stack.append(inst[2][0])
            elif inst[1] == Bytecode.LOAD_NAME:
                self.stack.append(self.get_var(inst[0], inst[2][0]))
            elif inst[1] == Bytecode.BIN_OP:
                self.bin_op(inst[0], inst[2][0])
            elif inst[1] == Bytecode.STORE:
                self.store_var(inst[0], inst[2][0], inst[2][1])
            elif inst[1] == Bytecode.OUTPUT:
                self.output(inst[2][0])
            elif inst[1] == Bytecode.CALL:
                self.call(inst[0], inst[2][0])
            elif inst[1] == Bytecode.RET:
                self.call_stack.pop()
                return

    def store_var(self, lineno: int, typename: str | None, names: tuple[str]) -> None:
        """Обрабатывает инструкцию STORE"""
        value = self.stack.pop()
        if len(names) > 1 and value is not None:
            raise SyntaxException(lineno, message='при нескольких переменных нельзя указывать значение')
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
            self.stack.append(Value(typename, b.value / a.value))
        elif op == '**' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value(typename, b.value ** a.value))

    def output(self, exprs_num: int) -> None:
        res: list[str] = []
        for _ in range(exprs_num):
            res.append(str(self.stack.pop().value))
        self.output_f(''.join(res[::-1]))

    def call(self, lineno: int, name: str) -> None:
        if name in self.algs:
            self.in_alg = True
            self.call_stack.append({})
            self._execute(self.algs[name])
        else:
            raise RuntimeException(lineno, f'имя {name} не определено')

    def _save_var(self, lineno: int, typename: str, name: str, value: Value | None) -> None:
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
        if name in self._get_all_namespaces():
            return True
        return False

    def _get_all_namespaces(self) -> Namespace:
        res: Namespace = {}
        res |= self.glob_vars
        for alg_ns in self.call_stack:
            res |= alg_ns
        return res


def _find_var_in_namespace(lineno: int, name: str, namespace: dict) -> Value | None:
    if name == 'нс':
        return Value('лит', '\n')
    if name not in namespace:
        return None
    var = namespace[name]
    if var is None:
        raise RuntimeException(lineno, 'нет значения у величины')
    return var[1]
