class LazyFormat:
    def __init__(self, string_to_format, *args, **kwargs): ...
    def __str__(self) -> str : ...
    def __mod__(self) -> str : ...


def remap_to_dict(data: list, include_index: bool = ...) -> list: ...


def reverse_remap_to_dict(data: list) -> list: ...
