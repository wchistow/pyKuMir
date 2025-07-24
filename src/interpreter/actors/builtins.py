import math
import random
import time
from datetime import datetime

from .base import Actor, KumirValue, KumirFunc


class Builtins(Actor):
    @staticmethod
    def _abs(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', abs(args[0].value))

    @staticmethod
    def _arccos(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.acos(args[0].value))

    @staticmethod
    def _arcctg(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.atan2(1, args[0].value))

    @staticmethod
    def _arcsin(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.asin(args[0].value))

    @staticmethod
    def _arctg(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.atan(args[0].value))

    @staticmethod
    def _cos(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.cos(args[0].value))

    @staticmethod
    def _ctg(args: list[KumirValue]) -> KumirValue:
        x = args[0].value
        return KumirValue('вещ', math.cos(x) / math.sin(x))

    @staticmethod
    def _div(args: list[KumirValue]) -> KumirValue:
        x, y = args[0].value, args[1].value
        return KumirValue('цел', int(x / y))

    @staticmethod
    def _exp(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.e ** args[0].value)

    @staticmethod
    def _iabs(args: list[KumirValue]) -> KumirValue:
        return KumirValue('цел', abs(args[0].value))

    @staticmethod
    def _imax(args: list[KumirValue]) -> KumirValue:
        x, y = args[0].value, args[1].value
        return KumirValue('цел', max(x, y))

    @staticmethod
    def _imin(args: list[KumirValue]) -> KumirValue:
        x, y = args[0].value, args[1].value
        return KumirValue('цел', min(x, y))

    @staticmethod
    def _int(args: list[KumirValue]) -> KumirValue:
        return KumirValue('цел', int(args[0].value))

    @staticmethod
    def _irand(args: list[KumirValue]) -> KumirValue:
        x, y = args[0].value, args[1].value
        return KumirValue('цел', random.randint(x, y))

    @staticmethod
    def _irnd(args: list[KumirValue]) -> KumirValue:
        return KumirValue('цел', random.randint(0, args[0].value))

    @staticmethod
    def _lg(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.log10(args[0].value))

    @staticmethod
    def _ln(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.log(args[0].value))

    @staticmethod
    def _max(args: list[KumirValue]) -> KumirValue:
        x, y = args[0].value, args[1].value
        return KumirValue('вещ', max(x, y))

    @staticmethod
    def _min(args: list[KumirValue]) -> KumirValue:
        x, y = args[0].value, args[1].value
        return KumirValue('вещ', min(x, y))

    @staticmethod
    def _mod(args: list[KumirValue]) -> KumirValue:
        x, y = args[0].value, args[1].value
        return KumirValue('цел', x % y)

    @staticmethod
    def _rand(args: list[KumirValue]) -> KumirValue:
        x, y = args[0].value, args[1].value
        return KumirValue('вещ', random.uniform(x, y))

    @staticmethod
    def _rnd(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', random.uniform(0, args[0].value))

    @staticmethod
    def _sign(args: list[KumirValue]) -> KumirValue:
        x = args[0].value
        if x > 0:
            res = 1
        elif x == 0:
            res = 0
        else:
            res = -1
        return KumirValue('цел', res)

    @staticmethod
    def _sin(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.sin(args[0].value))

    @staticmethod
    def _sqrt(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.sqrt(args[0].value))

    @staticmethod
    def _tg(args: list[KumirValue]) -> KumirValue:
        return KumirValue('вещ', math.tan(args[0].value))

    @staticmethod
    def _to_float(args: list[KumirValue]) -> KumirValue:
        s, default = args[0].value, args[1]
        try:
            return KumirValue('вещ', float(s))
        except ValueError:
            return default

    @staticmethod
    def _to_bool(args: list[KumirValue]) -> KumirValue:
        s, default = args[0].value, args[1]
        if s in ('да', 'нет'):
            return KumirValue('лог', s)
        else:
            return default

    @staticmethod
    def _to_int(args: list[KumirValue]) -> KumirValue:
        s, default = args[0].value, args[1]
        try:
            return KumirValue('цел', float(s))
        except ValueError:
            return default

    @staticmethod
    def _float_to_str(args: list[KumirValue]) -> KumirValue:
        return KumirValue('лит', str(args[0].value))

    @staticmethod
    def _len(args: list[KumirValue]) -> KumirValue:
        return KumirValue('цел', len(args[0].value))

    @staticmethod
    def _unicode(args: list[KumirValue]) -> KumirValue:
        return KumirValue('цел', ord(args[0].value))

    @staticmethod
    def _unichr(args: list[KumirValue]) -> KumirValue:
        return KumirValue('сим', chr(args[0].value))

    @staticmethod
    def _int_to_str(args: list[KumirValue]) -> KumirValue:
        return KumirValue('лит', str(args[0].value))

    @staticmethod
    def _wait(args: list[KumirValue]) -> None:
        x = args[0].value
        time.sleep(x / 1000)

    @staticmethod
    def _cur_time(_: list[KumirValue]) -> KumirValue:
        now = datetime.now()
        seconds_since_midnight = (now - now.replace(hour=0, minute=0,
                                                    second=0, microsecond=0)).total_seconds()
        return KumirValue('цел', int(seconds_since_midnight * 1000))

    funcs = {
        'abs': KumirFunc(_abs, 'вещ', [('арг', 'вещ', 'x')]),
        'arccos': KumirFunc(_arccos, 'вещ', [('арг', 'вещ', 'x')]),
        'arcctg': KumirFunc(_arcctg, 'вещ', [('арг', 'вещ', 'x')]),
        'arcsin': KumirFunc(_arcsin, 'вещ', [('арг', 'вещ', 'x')]),
        'arctg': KumirFunc(_arctg, 'вещ', [('арг', 'вещ', 'x')]),
        'cos': KumirFunc(_cos, 'вещ', [('арг', 'вещ', 'x')]),
        'ctg': KumirFunc(_ctg, 'вещ', [('арг', 'вещ', 'x')]),
        'div': KumirFunc(_div, 'цел', [('арг', 'цел', 'x'), ('арг', 'цел', 'y')]),
        'exp': KumirFunc(_exp, 'вещ', [('арг', 'вещ', 'x')]),
        'iabs': KumirFunc(_iabs, 'цел', [('арг', 'цел', 'x')]),
        'imax': KumirFunc(_imax, 'цел', [('арг', 'цел', 'x'), ('арг', 'цел', 'y')]),
        'imin': KumirFunc(_imin, 'цел', [('арг', 'цел', 'x'), ('арг', 'цел', 'y')]),
        'int': KumirFunc(_int, 'цел', [('арг', 'вещ', 'x')]),
        'irand': KumirFunc(_irand, 'цел', [('арг', 'цел', 'x'), ('арг', 'цел', 'y')]),
        'irnd': KumirFunc(_irnd, 'цел', [('арг', 'цел', 'x')]),
        'lg': KumirFunc(_lg, 'вещ', [('арг', 'вещ', 'x')]),
        'ln': KumirFunc(_ln, 'вещ', [('арг', 'вещ', 'x')]),
        'max': KumirFunc(_max, 'вещ', [('арг', 'вещ', 'x'), ('арг', 'вещ', 'y')]),
        'min': KumirFunc(_min, 'вещ', [('арг', 'вещ', 'x'), ('арг', 'вещ', 'y')]),
        'mod': KumirFunc(_mod, 'цел', [('арг', 'цел', 'x'), ('арг', 'цел', 'y')]),
        'rand': KumirFunc(_rand, 'вещ', [('арг', 'вещ', 'x'), ('арг', 'вещ', 'y')]),
        'rnd': KumirFunc(_rnd, 'вещ', [('арг', 'вещ', 'x')]),
        'sign': KumirFunc(_sign, 'цел', [('арг', 'вещ', 'x')]),
        'sin': KumirFunc(_sin, 'вещ', [('арг', 'вещ', 'x')]),
        'sqrt': KumirFunc(_sqrt, 'вещ', [('арг', 'вещ', 'x')]),
        'tg': KumirFunc(_tg, 'вещ', [('арг', 'вещ', 'x')]),
        'Вещ': KumirFunc(_to_float, 'вещ', [('арг', 'лит', 'строка'), ('арг', 'вещ', 'по умолчанию')]),
        'Лог': KumirFunc(_to_bool, 'лог', [('арг', 'лит', 'строка'), ('арг', 'лог', 'по умолчанию')]),
        'Цел': KumirFunc(_to_int, 'цел', [('арг', 'лит', 'строка'), ('арг', 'цел', 'по умолчанию')]),
        'вещ_в_лит': KumirFunc(_float_to_str, 'лит', [('арг', 'вещ', 'число')]),
        'длин': KumirFunc(_len, 'цел', [('арг', 'лит', 'строка')]),
        'код': KumirFunc(_unicode, 'цел', [('арг', 'сим', 'с')]),
        'юникод': KumirFunc(_unicode, 'цел', [('арг', 'сим', 'с')]),
        'символ': KumirFunc(_unichr, 'сим', [('арг', 'цел', 'n')]),
        'юнисимвол': KumirFunc(_unichr, 'сим', [('арг', 'цел', 'n')]),
        'цел_в_лит': KumirFunc(_int_to_str, 'лит', [('арг', 'цел', 'число')]),
        'ждать': KumirFunc(_wait, '', [('арг', 'цел', 'x')]),
        'время': KumirFunc(_cur_time, 'цел', []),
    }
    vars = {
        'МАКСВЕЩ': ('вещ', KumirValue('вещ', 1.7976931348623e308)),
        'МАКСЦЕЛ': ('цел', KumirValue('цел', 2**31 - 1)),
    }
