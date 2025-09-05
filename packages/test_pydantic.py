import pytest
import pydantic


@pytest.mark.parametrize("test_a, test_b", [(-1, "-1"), (0, "-1")])
def test_class_validator(test_a, test_b):
    class MyModel(pydantic.BaseModel):
        a: int
        b: str

        @pydantic.field_validator("a", "b")
        def check_a_and_b(cls, v):
            if type(v) is int and v < 0:
                raise ValueError("a and b must be positive")
            elif type(v) is str and v == "-1":
                raise ValueError("a and b must be positive")
            return v

    with pytest.raises(ValueError):
        MyModel(a=test_a, b=test_b)
