from dataclasses import dataclass

from .constants import ValueType


@dataclass
class Value:
    typename: str
    value: ValueType
