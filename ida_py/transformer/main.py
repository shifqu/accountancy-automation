"""Ida's transformer main functionality."""
import inspect
from dataclasses import MISSING, Field, is_dataclass
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin

from ida_py.transformer.errors import ValidationError


def from_dict(obj: Any, values: dict) -> Any:
    """Transform the dictionary `values` into `obj`, which is assumed to be a dataclass.

    The type hints of the `obj` are used to cast the values to the correct typing.

    Parameters
    ----------
    obj : Any
        A dataclass object.
    values : dict
        The values to be used for the initialization.

    Returns
    -------
    Any
        An instance of `obj`.

    Raises
    ------
    ValidationError
        Whenever the transformer failed to validate or instantiate the object.
    """
    data = {}
    field_dict: dict[str, Field] = obj.__dataclass_fields__
    type_annotations = inspect.get_annotations(obj, eval_str=True)
    field_dict_values = field_dict.values()
    aliases = [field.metadata["alias"] for field in field_dict_values if "alias" in field.metadata]
    for value_key in values.keys():
        if value_key not in field_dict and value_key not in aliases:
            raise ValidationError(
                f"'{value_key}' is an invalid field for {obj.__name__}. "
                f"Valid fields: {list(field_dict)}"
            )

    for name, field in field_dict.items():
        lookup_name = field.metadata.get("alias", name)
        type_annotation = type_annotations[name]

        if lookup_name not in values:
            if field.default is not MISSING:
                default_value = field.default
            elif field.default_factory is not MISSING:
                default_value = field.default_factory()
            else:
                raise ValidationError(
                    f"'{lookup_name}' is a required field for {obj.__name__}. "
                    f"Valid types: {type_annotation}"
                )
            data[name] = default_value
        else:
            value = values[lookup_name]
            if value is None and not _none_allowed(type_annotation):
                raise ValidationError(
                    f"'{lookup_name}' can not be None for {obj.__name__}. "
                    f"Valid types: {type_annotation}"
                )

            # Check if we should do some recursive converting
            # TODO: Support recursive converting on iterables. Currently the need for this
            #  conversion is not needed, but once the need rises, the check should be
            #  implemented around here.
            allowed_types = _get_allowed_types(type_annotation)
            for allowed_type in allowed_types:
                if is_dataclass(allowed_type):
                    data[name] = from_dict(allowed_type, values[lookup_name])
                    break

            if name in data:
                continue  # We recursively converted

            if type(value) not in allowed_types and value not in allowed_types:
                for allowed_type in allowed_types:
                    try:
                        value = allowed_type(value)
                    except (TypeError, ValueError):
                        """Continue to the next allowed_type in case conversion failed."""
                        continue
                    else:
                        break
                else:
                    raise ValidationError(
                        f"'{value}' is invalid for the field '{lookup_name}' on {obj.__name__}. "
                        f"Valid types: {type_annotation}"
                    )

            data[name] = value

    return obj(**data)


def _none_allowed(type_annotation: Any):
    if type_annotation is None:
        return True
    if inspect.isclass(type_annotation):
        # When a type is a class, they are generally not Optional.
        return False
    if isinstance(type_annotation, UnionType) or get_origin(type_annotation) == Union:
        return NoneType in get_args(type_annotation)

    raise Exception(f"Unexpected type {type_annotation}")


def _get_allowed_types(type_annotation: Any) -> tuple:
    if type_annotation is None or inspect.isclass(type_annotation):
        return (type_annotation,)
    if isinstance(type_annotation, UnionType) or get_origin(type_annotation) == Union:
        return get_args(type_annotation)

    raise Exception(f"Unexpected type {type_annotation}")
