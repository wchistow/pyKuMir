from dataclasses import dataclass
from typing import Optional, Union, TextIO

Table = dict[int, Optional['Value']]


@dataclass
class Value:
    typename: str
    value: str | int | float | TextIO | dict[int, Optional[Union['Value', Table]]]
