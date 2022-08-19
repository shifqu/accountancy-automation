"""Ida's transformer tests."""
from dataclasses import dataclass, field
from typing import Optional, Union

import pytest

from ida_py import transformer
from ida_py.transformer.main import _get_allowed_types, _none_allowed

MY_OPTIONAL_TYPE = str | int | None


@dataclass
class RecursiveDataclassTest:
    foo: int


@dataclass
class TypeTest:
    """Represent a class to test typings on a dataclass.

    A field can be required, not None
    A field can be required, None
    A field can be optional, not None
    A field can be optional, None
    """

    required_recursive: RecursiveDataclassTest
    required_not_none: str
    required_none: Union[int, str, None]
    optional_another: int | float = 0
    optional_not_none: int | str = 0
    optional_none: Optional[Union[int, str]] = None
    optional_custom_type: MY_OPTIONAL_TYPE = None
    container_type: list = field(default_factory=list)  # Recursive is not supported!
    none_type: None = None


def test_from_dict_happy_flow() -> None:
    """Test that from_dict behaves as expected in happy-flow."""

    inp = dict(
        required_recursive={"foo": "300"},
        required_not_none="hello",
        required_none=None,
        none_type=None,
    )
    transformer.from_dict(TypeTest, inp)


@pytest.mark.parametrize(
    ("input_", "match_str"),
    [
        (
            {
                "required_recursive": None,
                "required_not_none": "dummy",
                "required_none": None,
            },
            "can not be None for",
        ),
        (
            {"required_none": None},
            "is a required field for",
        ),
        (
            {
                "required_recursive": {"foo": "300"},
                "required_not_none": "dummy",
                "required_none": None,
                "optional_another": "dummy",
            },
            "is invalid for the field",
        ),
    ],
)
def test_from_dict_error_flow(input_: dict, match_str: str) -> None:
    """Test that from_dict behaves as expected in error-flow."""
    with pytest.raises(transformer.ValidationError, match=match_str):
        transformer.from_dict(TypeTest, input_)


def test_unexpected_type() -> None:
    with pytest.raises(transformer.ValidationError, match="Unexpected type"):
        _none_allowed("dummy")
    with pytest.raises(transformer.ValidationError, match="Unexpected type"):
        _get_allowed_types("dummy")
