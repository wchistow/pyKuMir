from typing import Callable, TypeAlias

from .bytecode import Bytecode, BytecodeType
from .exceptions import RuntimeException
from .value import Value

Namespace: TypeAlias = dict[str, tuple[str, Value | None]]


class VM:
    def __init__(self,
                 bytecode: list[BytecodeType],
                 output_f: Callable[[str], None],
                 input_f: Callable[[], str],
                 algs: dict[str, list[BytecodeType, list[int]]] | None = None) -> None:
        """
        :param bytecode: список команд байт-кода
        :param output_f: функция, в неё передаётся строка для вывода
        :param input_f: функция, вызывается для получения ввода пользователя
        :param algs: словарь алгоритмов в программе (формата `имя: список команд байт-кода`)
        """
        self.output_f = output_f
        self.input_f = input_f
        self.bytecode = bytecode
        self.algs = algs or {}

        self.glob_vars: Namespace = {'нс': ('лит', Value('лит', '\n'))}
        self.stack: list[Value | None] = []

        self.call_stack: list[Namespace] = []  # Локальные переменные текущих функций
        self.in_alg = False

        self.cur_tags: list[int] = []
        self.cur_inst_n = 0

        self.CALL_TRANSITIONS = {
            Bytecode.LOAD_CONST: lambda inst: self.stack.append(inst[2][0]),
            Bytecode.LOAD_NAME: lambda inst: self.stack.append(self.get_var(inst[0], inst[2][0])),
            Bytecode.BIN_OP: lambda inst: self.bin_op(inst[0], inst[2][0]),
            Bytecode.STORE: lambda inst: self.store_var(inst[0], inst[2][0], inst[2][1]),
            Bytecode.OUTPUT: lambda inst: self.output(inst[2][0]),
            Bytecode.INPUT: lambda inst: self.input(inst[0], inst[2]),
            Bytecode.CALL: lambda inst: self.call(inst[0], inst[2][0]),
            Bytecode.RET: lambda inst: self.call_stack.pop(),
            Bytecode.JUMP_TAG: lambda inst: self.jump_tag(inst[2][0]),
            Bytecode.JUMP_TAG_IF_FALSE: lambda inst: self.jump_tag_if_false(inst[0], inst[2][0])
        }

        self.INSTS_WITHOUT_INCREASE_COUNTER = {Bytecode.JUMP_TAG, Bytecode.JUMP_TAG_IF_FALSE}

    def execute(self) -> None:
        self._execute(self.bytecode)

    def _execute(self, bc: list[BytecodeType]) -> None:
        while self.cur_inst_n < len(bc):
            inst = bc[self.cur_inst_n]
            self.CALL_TRANSITIONS[inst[1]](inst)
            if inst[1] == Bytecode.RET:
                break
            if inst[1] not in self.INSTS_WITHOUT_INCREASE_COUNTER:
                self.cur_inst_n += 1

    def store_var(self, lineno: int, typename: str | None, names: tuple[str]) -> None:
        """
        Обрабатывает инструкцию STORE
        :param lineno: номер текущей строки
        :param typename: тип переменной(ых), `None`, если нужно сохранить значения в уже объявленную переменную
        :param names: имя/имена переменной(ых)
        """
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
        """
        Обрабатывает инструкцию BIN_OP
        :param lineno: номер текущей строки
        :param op: оператор, например `'+'`
        """
        a = self.stack.pop()
        b = self.stack.pop()
        typename = a.typename

        # операции над разными типами можно проводить, только если это цел или вещ
        if sorted((a.typename, b.typename)) == ['вещ', 'цел']:
            typename = 'вещ'
        elif a.typename != b.typename:
            raise RuntimeException(lineno, f'нельзя "{b.typename} {op} {a.typename}"')

        if op == '+' and a.typename in ('цел', 'вещ', 'лит'):
            self.stack.append(Value(typename, b.value + a.value))
        elif op == '+' and a.typename == 'сим':
            self.stack.append(Value('лит', b.value + a.value))  # <сим> + <сим> = <лит>
        elif op == '-' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value(typename, b.value - a.value))
        elif op == '*' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value(typename, b.value * a.value))
        elif op == '/' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value('вещ', b.value / a.value))
        elif op == '**' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value(typename, b.value ** a.value))
        elif op == '>=' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value('лог', _bool_to_str(b.value >= a.value)))
        elif op == '<=' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value('лог', _bool_to_str(b.value <= a.value)))
        elif op == '=':
            self.stack.append(Value('лог', _bool_to_str(b.value == a.value)))
        elif op == '<>':
            self.stack.append(Value('лог', _bool_to_str(b.value != a.value)))
        elif op == '>':
            self.stack.append(Value('лог', _bool_to_str(b.value > a.value)))
        elif op == '<':
            self.stack.append(Value('лог', _bool_to_str(b.value < a.value)))
        elif op == 'или' and typename == 'лог':
            self.stack.append(Value(
                'лог',
                _bool_to_str(_str_to_bool(b.value) or _str_to_bool(a.value)))
            )
        elif op == 'и' and typename == 'лог':
            self.stack.append(Value(
                'лог',
                _bool_to_str(_str_to_bool(b.value) and _str_to_bool(a.value)))
            )
        else:
            raise RuntimeException(lineno, f'нельзя "{b.typename} {op} {a.typename}"')

    def output(self, exprs_num: int) -> None:
        """
        Обрабатывает инструкцию OUTPUT
        :param exprs_num: количество выражений, которых нужно вывести (они загружаются из стека)
        """
        exprs = [str(self.stack.pop().value) for _ in range(exprs_num)]
        self.output_f(''.join(exprs[::-1]))

    def input(self, lineno: int, targets: list[str]) -> None:
        """
        Обрабатывает инструкцию INPUT
        :param lineno: номер текущей строки кода
        :param targets: список имён переменных, в которые необходимо записать ввод пользователя
        """
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
        """
        Обрабатывает инструкцию CALL
        :param lineno: номер текущей строки кода
        :param name: имя алгоритма, который нужно вызвать
        """
        if name in self.algs:
            self.in_alg = True
            self.call_stack.append({})
            self.cur_tags = self.algs[name][1]
            self.cur_inst_n = 0
            self._execute(self.algs[name][0])
        else:
            raise RuntimeException(lineno, f'имя {name} не определено')

    def jump_tag(self, tag: int) -> None:
        self.cur_inst_n = self.cur_tags[tag]

    def jump_tag_if_false(self, lineno: int, tag: int) -> None:
        cond = self.stack.pop()
        if cond.typename != 'лог':
            raise RuntimeException(lineno, 'условие после "если" не логическое')
        if cond.value != 'да':
            self.jump_tag(tag)
        else:
            self.cur_inst_n += 1

    def _save_var(self, lineno: int, typename: str, name: str, value: Value | None) -> None:
        """
        Создаёт переменную
        :param lineno: номер текущей строки кода
        :param typename: тип переменной
        :param name: имя переменной
        :param value: значение переменной (`None` - объявлена, но не определена)
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

    def get_var(self, lineno: int, name: str) -> Value:
        """
        :param lineno: номер текущей строки кода
        :param name: имя переменной
        :return: экземпляр класса `Value` - значение переменной
        :raise: RuntimeException - если имя не объявлено
        """
        var = _find_var_in_namespace(lineno, name, self._get_all_namespaces())
        if var is not None:
            return var
        raise RuntimeException(lineno, 'имя не объявлено')

    def _var_defined(self, name: str) -> bool:
        """
        :param name: имя переменной
        :return: `True`, если имя объявлено, иначе `False`
        """
        return name in self._get_all_namespaces()

    def _get_all_namespaces(self) -> Namespace:
        """
        :return: словарь - все доступные переменные
        """
        res = self.glob_vars
        if self.call_stack:
            res |= self.call_stack[-1]
        return res


def _str_to_bool(v: str) -> bool:
    return v == 'да'


def _bool_to_str(b: bool) -> str:
    return 'да' if b else 'нет'


def _convert_string_to_type(lineno: int, string: str, var_type: str) -> Value:
    """
    Преобразует строку в значение языка КуМир в зависимости от переданного типа
    :param string: исходная строка
    :param var_type: тип, в которые необходимо преобразовать строку
    :return: экземпляр класса `Value` - значение
    """
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


def _find_var_in_namespace(lineno: int, name: str, namespace: Namespace) -> Value | None:
    """
    :param name: имя переменной
    :param namespace: словарь всех переменных
    :return: `None` если переменная не найдена, иначе `Value`
    :raise: RuntimeException - если переменная объявлена, но ей не присвоено значение
    """
    try:
        var = namespace[name]
    except KeyError:
        return None
    if var[1] is None:
        raise RuntimeException(lineno, 'нет значения у величины')
    return var[1]
