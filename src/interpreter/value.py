from dataclasses import dataclass


@dataclass
class Value:
    typename: str
    value: str | int | float
