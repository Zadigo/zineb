from typing import Any, Union


def string_to_number(
    value: str, strict: bool = ...) -> Union[int, float, Any]: ...


def check_or_convert_to_type(
    value: Any,
    object_to_check_against: Union[int, float, str, list, tuple, type],
    message: str,
    enforce: bool = ...,
    force_conversion: bool = ...,
    use_default: bool = ...
) -> Any: ...


def convert_to_type(
    value: Any,
    t: Union[int, str, bool, list, tuple],
    field_name: str = ...
) -> Any: ...


def transform_to_bytes(content: str) -> bytes: ...


def detect_object_in_string(value: Any) -> Union[list, dict]: ...


def convert_if_number(value: str) -> Union[int, float]: ...
