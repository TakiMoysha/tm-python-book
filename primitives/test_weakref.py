import pytest

from weakref import WeakValueDictionary


# sqlalchemy - sessions
# GC ignore objects in WeakValueDictionary


class ApplicationObject:
    def __init__(self) -> None:
        self.setup()

    def setup(self):
        pass


@pytest.mark.asyncio
async def test_should_removed_prepared_object_in_weakref_dict():
    pass
