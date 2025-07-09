from .base import Actor
from .builtins import Builtins
from .files import Files

actors: dict[str, Actor] = {
    '__builtins__': Builtins(),
    'Файлы': Files()
}
