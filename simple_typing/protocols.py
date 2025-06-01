"""Protocol work like as a interface. It defines a set of methods that must be implemented by a class."""

from typing import Protocol


# Definition
class HasLength(Protocol):
    def __len__(self) -> int: ...

    def anouther_method(self, num: float) -> str: ...


def print_length(obj: HasLength) -> None:
    print(len(obj))


# Demo
class MyClass:
    def __len__(self) -> int:
        return 42

    def anouther_method(self, not_num: float) -> str:
        return "42"


class NotCompatible:
    """not compatible, because it has no __len__ method and anouther_method method has different type"""

    def anouther_method(self, not_num: int) -> float:
        return 42.4


print_length(MyClass())
print_length(NotCompatible())
