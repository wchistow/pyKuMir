from dataclasses import dataclass


@dataclass
class _BaseError:
    line: int     # Номер строки
    column: int   # Номер символа
    value: str    # Выражение, на котором ошибка возникла
    message: str  # Сообщение


class SyntaxException(_BaseError):
    ...
