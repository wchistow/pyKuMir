from dataclasses import dataclass
from typing import Optional, Union, TextIO, TypeAlias

Table: TypeAlias = dict[int, Optional['Value']]


@dataclass
class Value:
    typename: str
    value: str | int | float | TextIO | dict[int, Optional[Union['Value', Table]]]
