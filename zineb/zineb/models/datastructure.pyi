from functools import lru_cache
from typing import (Any, Dict, List, Literal, Optional, Tuple, Type, TypeVar,
                    Union)

from utils.containers import ModelSmartDict

from zineb.http.responses import HTMLResponse
from zineb.models.datastructure import ModelOptions
from zineb.models.fields import AutoField, Field, Value
from zineb.models.functions import Add, Divide, Multiply, Substract, When

T = TypeVar('T', covariant=True)


class ModelOptions:
    # constraints: List = ...
    initial_model_meta: None = ...
    field_names: List[str] = ...
    # fields_map: OrderedDict[str, Field]
    # related_model_fields: dict = ...
    model: type = ...
    model_name: str = ...
    # ordering: List[str] = ...
    # parents: set = ...
    verbose_name: str = ...
    def __repr__(self) -> str: ...
    def __getattr__(self, name) -> type: ...
    @property
    def is_template_model(self) -> bool: ...
    @property
    def has_ordering(self) -> bool: ...
    def get_option_by_name(self, name: str): ...
    def has_option(self, name) -> bool: ...
    def has_field(self, name: str) -> bool: ...
    def get_field(self, name: str) -> Field: ...


class Base(type):
    def __new__(
        cls: Type,
        name: str,
        bases: tuple,
        attrs: dict
    ) -> Type[Model]: ...


class Model(metaclass=Base):
    html_document: type = ...
    global_errors: List = ...
    response: HTMLResponse = ...
    _cached_resolved_data: None = ...
    _data_container: ModelSmartDict = ...
    _meta: ModelOptions = ...
    def __init__(self): ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __hash__(self) -> int: ...
    def __reduce__(self) -> Tuple[Type[Model], Tuple, Dict]: ...
    def __eq__(self, obj: Any) -> bool: ...

    @staticmethod
    def check_special_function(
        value: Union[str, int, float, Value]
    ) -> None: ...

    @lru_cache(maxsize=10)
    def resolve_all_related_fields(seelf) -> list: ...
    def _get_field_by_name(self, field_name: str) -> Field: ...

    def _bind_to_value_field(
        self,
        field_name: str,
        data: Union[str, int, float]
    ) -> None: ...

    def update_id_field(self) -> AutoField: ...

    def add_calculated_value(
        self, name: str,
        value: Any,
        *funcs: Optional[Union[Add, Divide, Substract, Multiply]]
    ) -> None: ...

    def add_case(self, value: Any, case: When) -> None: ...

    def add_using_expression(
        self,
        name: str,
        tag: str,
        attrs: Optional[dict] = ...
    ) -> None: ...

    def add_values(self, **attrs) -> None: ...
    def add_value(self, name: str, value: Any) -> None: ...

    def check_constraints(
        self,
        clean_value: Union[str, int, float]
    ) -> None: ...

    def full_clean(self, **kwargs) -> None: ...
    def clean(self, data: List, **kwargs) -> None: ...

    def save(
        self,
        commit: Optional[Literal[True]] = ...,
        filename: Optional[str] = ...,
        extension: Optional[Literal['json']] = ...,
        **kwargs
    ) -> Union[None, Union[list, dict]]: ...
