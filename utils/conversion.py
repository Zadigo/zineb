from typing import Any, Union
import ast
from zineb.utils.formatting import LazyFormat

def string_to_number(value: str, strict: bool=False):
    """
    Check if the value is a number and
    return it's true numberic rpresentation

    Parameters
    ----------

        value (Any): value to convert

    Returns
    -------

        Any: int, str, float
    """
    if not isinstance(value, str):
        raise ValueError(f"Value to convert to number should be a string. Got {value}")

    if strict and not value.isnumeric():
        raise ValueError(f"Value should be an integer or a float. Got '{value}'.")

    if value.isnumeric():
        try:
            return int(value)
        except:
            return float(value)
    return value


def check_or_convert_to_type(value: Any, object_to_check_against: Union[int, float, str, list, tuple, type],
                             message: str, enforce: bool=True, force_conversion: bool=False,
                             use_default: bool=False):
    """
    Checks the validity of a value against a Python object for example
    an int, a str or a list

    This check is used only to make sure that a value corresponds
    specifically to a python object with the possibility of raising
    an error if not or force converting the value to the python
    object in question

    Parameters
    ----------

        - value (str, int, type): value to test
        - object_to_check_against (type): int, str, type
        - message (str): message to display
        - enforce (bool, optional): whether to raise an error. Defaults to True
        - force_conversion (bool, optional): try to convert the value to obj. Defaults to False

    Raises
    ------

            TypeError: the value is not of the same type of the python object

    Returns
    -------

            Any: int, str
    """
    if force_conversion:
        try:
            value = object_to_check_against(value)
        except:
            # TODO: Thing is the validators know how to use
            # the default value which is not the case
            # when calling this specific function
            if use_default:
                return 'default'

    result = isinstance(value, object_to_check_against)
    if not result:
        if enforce:
            raise TypeError(message)

    return value


def convert_to_type(value: Any, t: Union[int, str, bool, list, tuple], field_name=None):
    from zineb.models.fields import Empty

    if value is None or value == Empty:
        return value

    try:
        return t(value)
    except Exception:
        attrs = {'value': value, 't': t, 
                'type1': type(value), 'type2': t, 
                    'name': field_name}
        raise ValueError(
            LazyFormat("The value '{value}' does not match the type provided "
            "in {t}. Got {type1} instead of {type2} for model field '{name}'.", **attrs)
        )


def transform_to_bytes(content: str):
    """
    Transform a string to bytes

    Parameters
    ----------

        - content (str): The string to convert

    Raises
    ------

        ValueError: the string is not valid

    Returns
    -------

        - bytes: the converted string in bytes
    """
    if isinstance(content, bytes):
        return content

    if isinstance(content, str):
        return content.encode(encoding='utf-8')
    else:
        raise ValueError(("In order to transform the object to bytes "
                          "you need to provide a string."))


def detect_object_in_string(value: Any):
    """
    Detects if a list, a tuple or a dict
    is embeded in a string and returns the
    true representation of that element

    Args:
        value (Any): [description]

    Returns:
        [type]: [description]
    """
    return ast.literal_eval(value)


def convert_to_dataframe(data: Union[list, dict], columns: list=[]):
    import pandas
    return pandas.DataFrame(data=data, columns=columns)


def convert_if_number(value: str):
    try:
        return int(value)
    except:
        return float(value)
    else:
        raise ValueError(
            LazyFormat('Cannot convert {value} to number.', value=value)
        )
