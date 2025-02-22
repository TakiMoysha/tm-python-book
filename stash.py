import time
from typing import Protocol, Self, Any, TypeVar, reveal_type


TTest = TypeVar("TTest", bound="TestClass")


class ITest(Protocol):
    def test(self) -> Self: ...


class TestClass(ITest):
    def __init__(self):
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}()>"

    def push(self, value) -> ITest:
        return self.__class__()

    @classmethod
    def from_str(cls, input: str) -> Self:
        return cls()


class SubTestClass(TestClass):
    pass


class Line[T]:
    other: "Line | None" = None

    @classmethod
    def make_pair(cls: type["Line"]) -> tuple["Line", "Line"]:
        return cls(), cls()

    @classmethod
    def from_dict(cls, values: dict[Any, T]) -> Self:
        reveal_type(cls)
        return cls()

    def copy(self: Self) -> "Line":
        reveal_type(self)
        return self.__class__()


class DecoratorTest:
    pass


left_line, right_line = Line.make_pair()
Line.from_dict({})
reveal_type(left_line)
reveal_type(right_line)

Line.from_dict({})
Line().copy()

#
n = iter(range(10))

res = list(zip(n, map(lambda x: x**2, n)))
print(res)


def test_list():
    value = "hello world!"
    ids = list()
    for i in range(10):
        value += str(i)
        ids.append(id(value))

    return ids


def test_set():
    value = "hello world!"
    ids = set()
    for i in range(10):
        value += str(i)
        ids.add(id(value))

    return ids


def test_vectors(N: int = 10000):
    print("Size: ", N)
    lst = [i for i in range(N)]

    tup = tuple(lst)

    start_time = time.time()
    for i in range(N):
        _ = lst[i]
    print("List access time:", time.time() - start_time)

    start_time = time.time()
    for i in range(N):
        _ = tup[i]
    print("Tuple access time:\t", time.time() - start_time)
