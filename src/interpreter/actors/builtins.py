from .base import Actor, KumirValue, KumirFunc


class Builtins(Actor):
    @staticmethod
    def _len(args: list[KumirValue]) -> KumirValue:
        """Встроенная функция `длин`."""
        return KumirValue('цел', len(args[0].value))

    funcs = {
        'длин': KumirFunc(_len, 'цел', [('арг', 'лит', 'строка')])
    }
    vars = {
        'МАКСЦЕЛ': ('цел', KumirValue('цел', 2**31 - 1))
    }
