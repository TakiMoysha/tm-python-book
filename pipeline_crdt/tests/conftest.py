import pytest


@pytest.fixture(name="utils")
def utils(pytestconfig: pytest.Config) -> tuple:
    return ()



