import pytest

@pytest.mark.limit_memory("24 MB")
def test_memory_limit(pytestconfig: pytest.Config, utils: tuple):
    assert True
