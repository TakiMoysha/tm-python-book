# File for mypy

import ast
import enum
import inspect

#
filename = inspect.getfile(cls)

with open(filename, "r") as f:
    root = ast.parse(f.read(), filename)

#
for node in ast.iter_child_nodes(root):
    if not hasattr(node, "names"):
        continue

    for name in node.names:
        if isinstance(node, ast.Import):
            import_str = f"import {name.name}"
        elif isinstance(node, ast.ImportFrom):
            import_str = f"from {node.module} import {name.name}"
        else:
            continue

        if name.asname:
            import_str += f" as {name.asname}"


#
class SomeClass:
    annotated: str
    initialized = 1
    both: bool = True

    def method(self) -> int:
        self.ignored = "=("
        return 42


#
for member_name in dir(cls):
    member = getattr(cls, member_name)
    if isinstance(member, property):
        print(f"Decorator @property: {member_name}")
    elif callable(member):
        print(f"Callable: {member_name}")
    elif not callable(member) and member_name not in cls.__annotations__:
        print(f"Initialized variables without annotations: {member_name}")

if hasatt(cls, "__annotations__"):
    for name, t in cls.__annotations__.items():
        print(f"Annotation: {name}: {t}")


#
def foo(a, b: str | None = None) -> list:
    return []


signature = inspect.signature(foo)
print(str(signature))


##
class SomeEnum(enum.Enum):
    default = "defalut"
    magic = "magic"


def bar(a, b: SomeEnum = SomeEnum.magic) -> list:
    return []


signature = inspect.signature(bar)
print(str(signature))
print(signature.parameters)
print(signature.return_annotation)
