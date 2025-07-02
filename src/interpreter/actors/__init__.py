from .base import Actor
from .builtins import Builtins

actors: dict[str, Actor] = {
    '__builtins__': Builtins()
}
