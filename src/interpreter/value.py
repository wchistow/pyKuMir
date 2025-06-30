from dataclasses import dataclass
from typing import Optional, Union

Table = dict[Optional['Value']]

@dataclass
class Value:
    typename: str
    value: str | int | float | dict[int, Optional[Union['Value', Table]]]
